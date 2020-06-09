from threading import Thread, Event
from queue import Queue, Empty
from time import sleep
import logging
from string import ascii_uppercase, digits
from random import choice
from os.path import abspath
from uuid import uuid4
from random import randint

from nodes import NodeState
from items import Item, ItemReq
from file_dict import FileDict
from messages import BatchRequest, \
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


class SuppyChainStage(Thread):

    '''
        SuppyChainStage (SCG) implements the business logic needed
        by the production stage. Each node maintains a SuppyChainStage that
        is given a stream of parts/items that get converted into a stream of
        outputs.

        i.e. SCG mocks a physical production stage that consumes and creates
        products like a stage in a factory would.
    '''

    def __init__(self, node_process, time_per_batch=1):
        '''
            name: unique name of stage. Used to identify log file.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_batch: time in seconds it takes to make one unit.
            inbound_node_fetcher: function implemented by node that allows fetching incoming nodes
        '''
        super(SuppyChainStage, self).__init__()
        self.node_id = node_process.node_id
        self.name = "sc-stage-{}".format(node_process.node_id)
        self.inbound_material = {}  # map of item-type -> Queue()

        self.outbound_material = Queue()
        self.time_per_batch = time_per_batch
        self.state_helper = node_process.state_helper
        self.metrics = node_process.metrics
        self.node_process = node_process

        self.send_message = node_process.sendMessage  # function to send messages to cluster

        self.inbound_log = FileDict(abspath("./tmp/" + self.name + ".inbound.log"))
        self.outbound_log = FileDict(abspath("./tmp/" + self.name + ".outbound.log"))

        # dict to keep track of requests that haven't gotten a response yet
        # maps request_id -> Message object
        self.pending_requests = set()

        # hack to stop stage
        self.stage_active = Event()
        self.stage_active.set()  # set the stage to run by default

        self.manufacture_count = 0
        self.consumed_count = 0

        self.metrics.set_metric(self.node_id, "failed_flow_queries", 0)
        self.metrics.set_metric(self.node_id, "skipped_manufacture_cycles", 0)
        self.metrics.set_metric(self.node_id, "batch_unavailable_messages_sent", 0)
        self.metrics.set_metric(self.node_id, "successful_manufacture_cycles", 0)
        self.metrics.set_metric(self.node_id, "flow_queries", 0)
        self.metrics.set_metric(self.node_id, "wal_recovered_inbound_batches", 0)
        self.metrics.set_metric(self.node_id, "wal_recovered_outbound_batches", 0)
        self.metrics.set_metric(self.node_id, "wal_ghost_outbound_batches", 0)
        self.metrics.set_metric(self.node_id, "wal_ghost_inbound_batches", 0)
        self.metrics.set_metric(self.node_id, "empty_outbound_inventory_occurrences", 0)
        self.metrics.set_metric(self.node_id, "batches_delivered", 0)

        self._attempt_log_recovery()

        log.info("Node %d's stage bootstrap complete", self.node_id)

    def item_dep(self):
        return self.node_process.node().get_dependency()

    def node(self):
        return self.node_process.node()

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
            log.debug("Node %d waiting for flow to be set to start batch status verification in WAL recovery", self.node_id)
            self.metrics.increase_metric(self.node_id, "failed_flow_queries")

            flow = self.state_helper.get_flow()
            self.metrics.increase_metric(self.node_id, "flow_queries")
            sleep(1)

        self._attempt_inbound_recovery(in_log, flow)
        self._attempt_outbound_recovery(out_log, flow)

    def _attempt_inbound_recovery(self, in_log, flow):
        log.info("Node %d attempting post-crash recovery to verify status of batches in inbound WAL of size %d", self.node_id, in_log.size())

        neighbors = {ir.item.type: nid for nid, ir in flow.getIncomingFlowsForNode(self.node_id)}

        for batch, state in in_log.items():
            log.info("Node %d found batch %s in state %s in inbound WAL", self.node_id, batch, state)
            batch_type = batch.item.type
            if state == BatchStatus.IN_TRANSIT and batch_type in neighbors:
                # make a best effort to correct status in neighbor
                self.inbound_log[batch] = BatchStatus.IN_QUEUE
                ack = BatchDeliveryConfirmResponse(
                    source=self.node_id,
                    dest=neighbors[batch_type],
                    item_req=batch,
                    request_id=None,
                )
                self.send_message(ack)
                self._add_batch_to_inbound_queue(batch)
            elif state == BatchStatus.IN_QUEUE:
                self._add_batch_to_inbound_queue(batch)
                self.metrics.increase_metric(self.node_id, "wal_recovered_inbound_batches")
            elif state == BatchStatus.CONSUMED:
                self.consumed_count += 1
                self.metrics.increase_metric(self.node_id, "wal_recovered_inbound_batches")
            else:
                self.metrics.increase_metric(self.node_id, "wal_ghost_inbound_batches")

    def _attempt_outbound_recovery(self, out_log, flow):
        log.info("Node %d attempting post-crash recovery to verify status of batches in outbound WAL of size %d", self.node_id, out_log.size())

        neighbors = {ir.item.type: nid for nid, ir in flow.getOutgoingFlowsForNode(self.node_id)}

        for batch, state in out_log.items():
            log.info("Node %d found batch %s in state %s in outbound WAL", self.node_id, batch, state)
            # if in-transit in WAL, resend the sentBatch message, the downstream node will
            # reply with a delivery confirmation.
            if state == BatchStatus.IN_TRANSIT and batch.item.type in neighbors:
                replay_message = BatchSentResponse(
                    source=self.node_id,
                    dest=neighbors[batch.item.type],
                    item_req=batch,
                    request_id=None,
                )
                self.send_message(replay_message)
            elif state == BatchStatus.IN_QUEUE:
                self.outbound_material.put(batch)
                self.metrics.increase_metric(self.node_id, "wal_recovered_outbound_batches")
            elif state == BatchStatus.DELIVERED:
                # we are sure the item was delivered downstream
                self.manufacture_count += 1
                self.metrics.increase_metric(self.node_id, "wal_recovered_outbound_batches")
            else:
                self.metrics.increase_metric(self.node_id, "wal_ghost_outbound_batches")

    def stop(self):
        '''
            - Stop the stage's production & consumption loop.
            - Destory in-memory state. E.g. the inbound and outbound queues.
        '''
        log.critical("Node %d's stage is being stopped", self.node_id)
        # stop the production loop
        self.stage_active.clear()

        # clear in-memory state;
        # Init to Queue() as it sometimes fails due to race condition
        self.outbound_material = Queue()
        for item_type in self.inbound_material:
            # Set all inbound queues to null
            self.inbound_material[item_type] = Queue()
        self.manufacture_count = self.consumed_count = 0

    def restart(self):
        '''
            Simulated restart after a crash. Initalise in-memory state
            and attempt a recovery from the WAL.
        '''
        log.critical("Node %d's stage is being restarted", self.node_id)
        self.outbound_material = Queue()
        self._attempt_log_recovery()
        self.stage_active.set()

    def get_stage_result_type(self):
        return self.item_dep().get_result_type()

    def _add_batch_to_inbound_queue(self, batch):
        batch_type = batch.item.type
        if batch_type not in self.inbound_material:
            # start a new queue for a new type of inbound item
            log.info("Node {} started new inbound queue for type {}".format(self.node_id, batch_type))
            self.inbound_material[batch_type] = Queue()

        self.inbound_material[batch_type].put(batch)

    def _mark_request_complete(self, response):
        '''
            Removes the request ID in the response from pending requests.
            i.e. The request ID was created when this stage made a request and
            the rid was added to the pending_requests until a response was received.
        '''
        self.pending_requests.remove(response.request_id)

    def process_item_waiting_response(self, message):
        log.debug("Node %d got an in-transit ack from node %d for batch %s", self.node_id, message.source, message.item_req)
        batch = message.item_req
        curr_status = self.outbound_log[batch]
        if curr_status != BatchStatus.IN_TRANSIT:
            log.info("Node %d's outbound log for item %s was at status %s, expected %s",
                     self.node_id, batch, curr_status, BatchStatus.IN_TRANSIT)
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
            log.info("Node %d unable to supply %s because no batch of %s has been manufactired yet.",
                     self.node_id, request,  self.get_stage_result_type())
            self.metrics.increase_metric(self.node_id, "empty_outbound_inventory_occurrences")

        reply = BatchUnavailableResponse(
            source=self.node_id,
            dest=request.source,
            item_req=request.item_req,
            request_id=request.request_id,
        )
        self.send_message(reply)
        self.metrics.increase_metric(self.node_id, "batch_unavailable_messages_sent")

    def am_i_a_finale_item(self):
        """
        Checks if this stage produces a finale item
        TODO: Optimize; this should be a flag or state in self.cluster
        """
        flow = self.state_helper.get_flow()
        if flow:
            # TODO this can also be true for island nodes
            num_ins = len(flow.getIncomingFlowsForNode(self.node_id))
            num_outs = len(flow.getOutgoingFlowsForNode(self.node_id))
            # return (num_ins > 0) and (num_outs == 0)
            return (num_ins > 0) and (num_outs == 0)
        return False

    def process_batch_request_response(self, response: Message):
        '''
            receives a BatchSentResponse or BatchUnavailableResponse message after
            the node made a request for a part
        '''
        log.debug("Node %d received %s after batch request %s", self.node_id, response, response.request_id)
        if isinstance(response, BatchSentResponse):
            batch = response.item_req
            if not self.item_dep().is_valid_material(batch):
                log.error("Node %d received invalid batch %s from node %d. Node %d's deps are %s. Ignoring received batch.",
                          self.node_id, batch, response.source, self.node_id, self.item_dep())
                return

            batch_seen_before = False
            if batch in self.inbound_log:
                log.info("Node %d seeing duplicate send message for batch %s, will not add to inbound queue",
                         self.node_id, batch)
                batch_seen_before = True

            self.inbound_log[batch] = BatchStatus.IN_TRANSIT
            ack = WaitingForBatchResponse(
                source=self.node_id,
                dest=response.source,
                item_req=batch,
                request_id=response.request_id,
            )
            self.send_message(ack)
            log.info("Node %d marking batch %s in-transit in local WAL", self.node_id, response.item_req)

            # sleep(randint(self.time_per_batch, self.time_per_batch*3))  # HACK simulated transit time

            log.info("Node %d sending batch %s delivery confirmation to node %d", self.node_id, response.item_req, response.source)
            self.inbound_log[batch] = BatchStatus.IN_QUEUE
            ack = BatchDeliveryConfirmResponse(
                source=self.node_id,
                dest=response.source,
                item_req=batch,
                request_id=response.request_id,
            )
            self.send_message(ack)

            if not batch_seen_before:
                self.metrics.increase_metric(self.node_id, "batches_received")
                self._add_batch_to_inbound_queue(batch)
                log.info("Node %d received batch %s from node %d and enqueued into inbound queue",
                         self.node_id, response.item_req, response.source)
        else:
            self.metrics.increase_metric(self.node_id, "batch_unavailable_messages_received")
            log.info("Node %d unable to obtain batch of type %s from node %d. Will try again in the next cycle. "
                     "Request ID: %s",  self.node_id, response.item_req.item.type, response.source, response.request_id)

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
        batch = message.item_req
        if batch not in self.outbound_log or self.outbound_log[batch] != BatchStatus.DELIVERED:
            self.metrics.increase_metric(self.node_id, "batches_delivered")
            self.outbound_log[batch] = BatchStatus.DELIVERED

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
        self.pending_requests.add(batch_request.request_id)

        self.metrics.increase_metric(self.node_id, "batches_requested")

        log.debug("Node %d sent a material batch request %s", self.node_id, batch_request)

    def _attempt_manufacture_cycle(self, suppliers):
        '''
            suppliers: list of (node_id, item_req) tuples obtained from the latest flow
        '''
        prereqs = self.item_dep().get_prereq()  # [ItemReq(Item(type:0)...uantity:1)]
        if prereqs:
            prereq_types = set([ir.item.type for ir in prereqs])
            supplier_types = set(suppliers.keys())

            if not prereq_types.issuperset(supplier_types) or not supplier_types:
                # TODO (Nishant) you'll see this error if the underlying prereques don't match the flow
                log.critical("Node {} has more suppliers ({}) from flow than the node's prerequisite types ({})"
                             .format(self.node_id, supplier_types, prereq_types))
                log.error("Node %d skipping manufacturing cycle", self.node_id)

                self.metrics.increase_metric(self.node_id, "skipped_manufacture_cycles")
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
                self.metrics.increase_metric(self.node_id, "skipped_manufacture_cycles")
                # all the necessary inbound materials are not present in the inbound
                # queues. batch requests have been made and this manufacture cycle needs to be skipped.
                return

        new_item_id = str(self.get_stage_result_type()) + '-' + str(self._generate_new_item_id())
        new_item = Item(_type=self.get_stage_result_type(), _id=new_item_id)
        new_batch = ItemReq(new_item, 1)  # TODO/FIXME assumes batch size is always 1

        self.outbound_log[new_batch] = BatchStatus.IN_QUEUE
        self.outbound_material.put(new_batch)
        self.manufacture_count += 1
        self.metrics.increase_metric(self.node_id, "successful_manufacture_cycles")

        # Log production of important items differently
        if self.am_i_a_finale_item():
            log.critical("Node %d successfully manufactured batch %s which is a finale item", self.node_id, new_batch)
        else:
            log.debug("Node %d successfully manufactured batch %s and enqueued to outbound queue",
                      self.node_id, new_batch)

    def run(self):

        # Add cooldown before starting stage, allows initial leader, flow to be detected
        sleep(2.0)

        log.debug("Node %d starting manufacturing cycle of %s", self.node_id, self.get_stage_result_type())

        while True:
            self.stage_active.wait()  # Blocks until the stage is set to active
            sleep(self.time_per_batch)

            self.metrics.increase_metric(self.node_id, "total_manufacture_cycles")
            self.metrics.set_metric(self.node_id, "batches_produced_total", self.manufacture_count)
            self.metrics.set_metric(self.node_id, "batches_consumed_total", self.consumed_count)
            self.metrics.set_metric(self.node_id, "unanswered_batch_requests_current", len(self.pending_requests))
            self.metrics.set_metric(self.node_id, "outbound_wal_size", self.outbound_log.size())
            self.metrics.set_metric(self.node_id, "inbound_wal_size", self.inbound_log.size())

            if not self.node_process.is_active:
                log.error("Node %d's stage still running after node process was set to inactive", self.node_id)
                continue

            flow = self.state_helper.get_flow()
            self.metrics.increase_metric(self.node_id, "flow_queries")
            if not flow:
                log.error("Node %d unable to retrieve flow to acquire items %s. Skipping cycle.",
                          self.node_id, self.item_dep().get_prereq())
                self.metrics.increase_metric(self.node_id, "skipped_manufacture_cycles")
                self.metrics.increase_metric(self.node_id, "failed_flow_queries")
                continue

            latest_suppliers = flow.getIncomingFlowsForNode(self.node_id)  # [(1, ItemReq(Item(type:1)...uantity:1))]
            log.debug("Node %d seeing suppliers %s in flow", self.node_id, [sid for sid, _ in latest_suppliers])

            latest_suppliers = {ir.item.type: sid for sid, ir in latest_suppliers}  # convert the flow edges to dict
            self._attempt_manufacture_cycle(latest_suppliers)
