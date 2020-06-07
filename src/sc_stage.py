from threading import Thread, Event
from queue import Queue, Empty
from time import sleep
import logging
from string import ascii_uppercase, digits
from random import choice
from os.path import abspath
from uuid import uuid4
from nodes import NodeState

from items import Item, ItemReq
from file_dict import FileDict
from messages import BatchRequest, \
                    BatchStatusRequest, \
                    BatchSentResponse, \
                    Message, \
                    WaitingForBatchResponse, \
                    BatchDeliveryConfirmResponse, \
                    BatchUnavailableResponse
log = logging.getLogger()


class BatchStatus():
    IN_QUEUE = "in-queue"  # ready to be consumed or sent
    DELIVERED = "delivered"  # batch was delivered downstream
    CONSUMED = "consumed"  # batch was consumed in present node
    IN_TRANSIT = "in-transit"  # batch sent by producing node and awaited downstream

    # statues when current node is waiting for the neighbor to report the status
    WAITING_FOR_NEIGHBOR = "waiting-for-neighbor-response"


class SuppyChainStage(Thread):

    '''
        SuppyChainStage (SCG) implements the business logic needed
        by the production stage. Each node maintains a SuppyChainStage that
        is given a stream of parts/items that get converted into a stream of
        outputs.

        i.e. SCG mocks a physical production stage that consumes and creates
        products like a stage in a factory would.
    '''

    def __init__(self, node_process, time_per_batch=3):
        '''
            name: unique name of stage. Used to identify log file.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_batch: time in seconds it takes to make one unit.
            inbound_node_fetcher: function implemented by node that allows fetching incoming nodes
        '''
        super(SuppyChainStage, self).__init__()
        self.node_id = node_process.node.get_id()
        self.name = "sc-stage-{}".format(node_process.node.get_id())
        self.item_dep = node_process.node.get_dependency()  # TODO (Nishant) verify this is up to date with latest prereqs
        self.inbound_material = {}  # map of item-type -> Queue()
        self.outbound_material = Queue()
        self.time_per_batch = time_per_batch
        self.state_helper = node_process.state_helper
        # self.cluster = node_process.cluster
        self.metrics = node_process.metrics

        self.node = node_process.node
        self.send_message = node_process.sendMessage  # function to send messages to cluster

        self.inbound_log = FileDict(abspath("./tmp/" + self.name + ".inbound.log"))
        self.outbound_log = FileDict(abspath("./tmp/" + self.name + ".outbound.log"))

        # dict to keep track of requests that haven't gotten a response yet
        # maps request_id -> Message object
        self.pending_requests = {}

        # hack to stop stage
        self.running = Event()
        self.running.set()  # set the stage to run by default

        self.manufacture_count = 0
        self.consumed_count = 0
        self._attempt_log_recovery()

        log.info("Node %d's stage bootstrap complete", self.node_id)

    def _attempt_log_recovery(self):
        '''
            attempts to populate the in-memory data structures from
            data in the WAL.
        '''
        self.inbound_material = {}  # map of item-type -> Queue()
        self.outbound_material = Queue()

        out_log, in_log = self.outbound_log, self.inbound_log
        if not out_log.size() and not in_log.size():
            log.info("Node %d's batch status WALs are empty. Skipping post-crash item and material status verification", self.node_id)
            return

        flow = self.state_helper.get_flow()
        self.metrics.increase_metric(self.node_id, "flow_queries")
        while not flow:
            # cant proceed until flow is obtained
            sleep(self.time_per_batch)
            log.debug("Node %d waiting for flow to be set to start batch status verification", self.node_id)
            flow = self.state_helper.get_flow()
            self.metrics.increase_metric(self.node_id, "flow_queries")

        self._attempt_inbound_recovery(in_log, flow)
        self._attempt_outbound_recovery(out_log, flow)

    def _attempt_inbound_recovery(self, in_log, flow):
        log.info("Node %d attempting post-crash recovery to verify status of batches in inbound WAL of size %d", self.node_id, in_log.size())

        neighbors = [nid for nid, _ in flow.getIncomingFlowsForNode(self.node_id)]
        unknown_state_batches = set()

        for batch, state in in_log.items():
            # only consumed batches need no further confirmation from
            # neighbors about the status of the item
            if state != BatchStatus.CONSUMED:
                self._request_batch_status_from_neighbor(neighbors, batch)
                unknown_state_batches.add(batch)
            else:
                self.consumed_count += 1

        for batch in unknown_state_batches:
            self.outbound_log[batch] = BatchStatus.WAITING_FOR_NEIGHBOR

    def _attempt_outbound_recovery(self, out_log, flow):
        log.info("Node %d attempting post-crash recovery to verify status of batches in outbound WAL of size %d", self.node_id, out_log.size())

        neighbors = [nid for nid, _ in flow.getOutgoingFlowsForNode(self.node_id)]
        unknown_state_batches = set()

        for batch, state in out_log.items():
            # only items marked in-transit, in-queue or waiting-for-neigh need
            # confirmation of status from it's neighbors.
            if state != BatchStatus.DELIVERED:
                self._request_batch_status_from_neighbor(neighbors, batch)
                unknown_state_batches.add(batch)
            else:
                # we are sure the item was consumed downstream
                self.manufacture_count += 1

        for batch in unknown_state_batches:
            self.outbound_log[batch] = BatchStatus.WAITING_FOR_NEIGHBOR

    def _request_batch_status_from_neighbor(self, neighbors, batch):
        '''
            TODO
            make a status check request to the neighbor about the given batch
        '''
        # send a batch status check request with send_message()
        pass

    def process_batch_status_check_request(self, request: Message):
        log.debug("Node %d received batch status check query %s", self.node_id, request)
        # TODO
        # reply with right the status of the item as present in
        # the node's inbound/outbound logs.
        assert request.action == BatchStatusRequest

        # if consumed or in-queue, send delivered
        # if in-transit, send waiting
        # if not in log, send unseen

    def stop(self):
        '''
            - Stop the stage's production & consumption loop.
            - Destory in-memory state. E.g. the inbound and outbound queues.
        '''
        log.critical("Node %d's stage is being stopped", self.node_id)
        # stop the production loop
        self.running.clear()

        # clear in-memory state
        self.outbound_material = None
        for item_type in self.inbound_material:
            # Set all inbound queues to null
            self.inbound_material[item_type] = None
        self.manufacture_count = self.consumed_count = 0

    def restart(self):
        '''
            Simulated restart after a crash. Initalise in-memory state
            and attempt a recovery from the WAL.
        '''
        self.outbound_material = Queue()
        self._attempt_log_recovery()

    def get_stage_result_type(self):
        return self.item_dep.get_result_type()

    def _mark_request_complete(self, response):
        '''
            Removes the request ID in the response from pending requests.
            i.e. The request ID was created when this stage made a request and
            the rid was added to the pending_requests until a response was received.
        '''
        try:
            del self.pending_requests[response.request_id]
        except KeyError:
            log.error("Node %d was not waiting got a response for request ID %s but got %s", self.node_id, response.request_id, response)

    def process_item_waiting_response(self, message):
        log.debug("Node %d got an in-transit ack from node %d for batch %s", self.node_id, message.source, message.item_req)
        batch = message.item_req
        curr_status = self.outbound_log[batch]
        if curr_status != BatchStatus.IN_TRANSIT:
            log.warning("Node %d's outbound log for item %s was at status %s, expected %s", self.node_id, batch, curr_status, BatchStatus.IN_TRANSIT)
            self.outbound_log[batch] = BatchStatus.IN_TRANSIT

    def process_batch_request(self, request: Message):
        log.debug("Node %d received request %s", self.node_id, request)

        # verify the right item type is being requested
        if request.item_req.item.type != self.get_stage_result_type():  # TODO (Nishant) this check will fail if prereq is not updated
            log.error("Node %d requested to supply %s but it produces %s",
                      self.node_id, request.item_req, self.get_stage_result_type())

        # verify the right node is making the request
        flow = self.state_helper.get_flow()
        self.metrics.increase_metric(self.node_id, "flow_queries")
        if flow:
            allowed_requesters = flow.getOutgoingFlowsForNode(self.node_id)
            allowed_requesters = [nid for nid, _ in allowed_requesters]
            if request.source not in allowed_requesters:
                log.error("Node %d got a supply-batch request from node %d but %d's outgoing edges are %s. Ignoring request.",
                          self.node_id, request.source, self.node_id, allowed_requesters)
        else:
            log.error("Node %d unable to retrieve flow. Ignoring request %s", self.node_id, request)
            return

        try:
            # outbound queue has items waiting to be sent
            produced_batch = self.outbound_material.get(block=False)
            self.inbound_log[produced_batch] = BatchStatus.IN_TRANSIT

            reply = BatchSentResponse(
                source=self.node_id,
                dest=request.source,
                item_req=produced_batch,
                request_id=request.request_id,
            )
            self.send_message(reply)
            log.info("Node %d successfully sent batch %s to node %s", self.node_id, produced_batch, request.source)
            return
        except Empty:
            # outbound queue is empty
            log.error("Node %d unable to supply %s because no batch of %s has been manufactired yet.",
                      self.node_id, request,  self.get_stage_result_type())

        reply = BatchUnavailableResponse(
            source=self.node_id,
            dest=request.source,
            item_req=request.item_req,
            request_id=request.request_id,
        )
        self.send_message(reply)

    def process_batch_request_response(self, response: Message):
        '''
            receives a BatchSentResponse or BatchUnavailableResponse message after
            the node made a request for a part
        '''
        log.debug("Node %d received %s after batch request %s", self.node_id, response, response.request_id)
        if isinstance(response, BatchSentResponse):
            batch = response.item_req
            if not self.item_dep.is_valid_material(batch):  # TODO (Nishant) this check will fail if the prereq is not updated
                log.error("Node %d received invalid batch %s from node %d. Node %d's deps are %s. Ignoring received batch.",
                          self.node_id, batch, response.source, self.node_id, self.item_dep)
                return

            self.inbound_log[batch] = BatchStatus.IN_TRANSIT
            ack = WaitingForBatchResponse(
                source=self.node_id,
                dest=response.source,
                item_req=batch,
                request_id=response.request_id,
            )
            self.send_message(ack)
            log.info("Node %d marking batch %s in-transit in local WAL", self.node_id, response.item_req)

            sleep(self.time_per_batch)  # HACK simulated transit time

            log.info("Node %d sending batch %s delivery confirmation to node %d", self.node_id, response.item_req, response.source)
            self.inbound_log[batch] = BatchStatus.IN_QUEUE
            ack = BatchDeliveryConfirmResponse(
                source=self.node_id,
                dest=response.source,
                item_req=batch,
                request_id=response.request_id,
            )
            self.send_message(ack)
            batch_type = batch.item.type
            if batch_type not in self.inbound_material:
                # start a new queue for a new type of inbound item
                log.info("Node {} started new inbound queue for type {}".format(self.node_id, batch_type))
                self.inbound_material[batch_type] = Queue()
            self.inbound_material[batch_type].put(batch)

            log.info("Node %d received batch %s from node %d and enqueued into inbound queue", self.node_id, response.item_req, response.source)
        else:
            log.error("Node %d unable to obtain batch of type %s from node %d. Request ID: %s",
                      self.node_id, response.item_req.item.type, response.source, response.request_id)

        self._mark_request_complete(response)

    def _generate_new_item_id(self):
        return ''.join(choice(ascii_uppercase) for _ in range(5)) + \
            ''.join(choice(digits) for _ in range(3))

    def mark_item_delivered(self, message: Message):
        '''
            callback invoked by the node to mark a result item delivered to a downstream
            node. Updates the persistant log. Gets called when a downstream node sends a
            BatchDeliveryConfirm message
        '''
        item = message.item_req
        self.outbound_log[item] = BatchStatus.DELIVERED

    def _send_material_request_upstream(self, supplier_id, supplier_type):
        '''
            Identifies the supplier nodes from where parts are to be requested
            and makes a request for the parts from that node.
        '''
        log.debug("Node %d sending a material batch request for item type %s to node %d", self.node_id, supplier_type, supplier_id)

        batch_request = BatchRequest(
            source=self.node_id,
            dest=supplier_id,
            item_req=ItemReq(Item(supplier_type, None), 1),  # HACK only batches of size 1 requested
            request_id=str(uuid4())[:8],  # HACK for unique but short request IDs
        )
        self.send_message(batch_request)
        self.pending_requests[batch_request.request_id] = batch_request

        log.debug("Node %d sent a material batch request %s", self.node_id, batch_request)

    def _attempt_manufacture_cycle(self, suppliers):
        '''
            suppliers: list of (node_id, item_req) tuples obtained from the latest flow
        '''
        prereqs = self.item_dep.get_prereq()  # [ItemReq(Item(type:0)...uantity:1)]
        if prereqs:
            prereq_types = set([ir.item.type for ir in prereqs])
            supplier_types = set(suppliers.keys())

            if not prereq_types.issuperset(supplier_types):  # verify there is prerequisite for each supplier
                # TODO (Nishant) you'll see this error if the underlying prereques don't match the flow
                log.critical("Node {} has more suppliers ({}) from flow than the node's prerequisite types ({})"
                             .format(self.node_id, supplier_types, prereq_types))
                log.error("Node %d skipping manufacturing cycle", self.node_id)
                return

            has_all_materials = True
            for item_type, supplier_id in suppliers.items():

                if item_type not in self.inbound_material or self.inbound_material[item_type].empty():
                    log.info("Node %d needs batch of type %s from node %s", self.node_id, item_type, supplier_id)
                    self._send_material_request_upstream(supplier_id, item_type)
                    has_all_materials = False

            if has_all_materials:
                for item_type, supplier_id in suppliers.items():
                    queue = self.inbound_material[item_type]

                    material_req = queue.get(block=False)  # HACK wait at most 1 second for a material batch
                    self.inbound_log[material_req] = BatchStatus.CONSUMED
                    log.info("Node %d successfully consumed %s", self.node_id, material_req)
                    self.consumed_count += 1
            else:
                # all the necessary inbound materials are not present in the inbound
                # queues. batch requests have been made and this manufacture cycle needs to be skipped.
                return

        new_item_id = str(self.get_stage_result_type()) + '-' + str(self._generate_new_item_id())
        new_item = Item(_type=self.get_stage_result_type(), _id=new_item_id)
        new_batch = ItemReq(new_item, 1)  # TODO/FIXME assumes batch size is always 1

        self.outbound_log[new_batch] = BatchStatus.IN_QUEUE
        self.outbound_material.put(new_batch)
        self.manufacture_count += 1
        log.debug("Node %d successfully manufactured batch %s and enqueued to outbound queue", self.node_id, new_batch)

    def _update_stage_metrics(self):
        '''
            Called at the end of a manufacture batch cycle to
            populate any metrics the stage needs to publish.
        '''
        self.metrics.set_metric(self.node_id, "batches_produced", self.manufacture_count)
        self.metrics.set_metric(self.node_id, "batches_consumed", self.consumed_count)

    def run(self):

        log.debug("Node %d starting manufacturing cycle of %s", self.node_id, self.get_stage_result_type())

        while self.running.is_set():
            sleep(self.time_per_batch)

            if self.node.state == NodeState.inactive:
                log.error("Node %d's stage still running after node was set to inactive", self.node_id)
                continue

            flow = self.state_helper.get_flow()
            if not flow:
                log.error("Node %d unable to retrieve flow to acquire items %s. Skipping cycle.",
                          self.node_id, self.item_dep.get_prereq())
                continue

            latest_suppliers = flow.getIncomingFlowsForNode(self.node_id)  # [(1, ItemReq(Item(type:1)...uantity:1))]
            log.debug("Node %d seeing suppliers %s in flow", self.node_id, [sid for sid, _ in latest_suppliers])
            self.metrics.increase_metric(self.node_id, "flow_queries")

            latest_suppliers = {ir.item.type: sid for sid, ir in latest_suppliers}  # convert the flow edges to dict
            self._attempt_manufacture_cycle(latest_suppliers)

            self._update_stage_metrics()
