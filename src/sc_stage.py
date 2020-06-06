from threading import Thread, Event
from queue import Queue, Empty
from time import sleep
import logging
from string import ascii_uppercase, digits
from random import choice
from os.path import abspath
from uuid import uuid4
from typing import List
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


class StageStatus():
    IN_QUEUE = "in-queue"  # ready to be consumed or sent
    DELIVERED = "delivered"  # item was delivered downstream
    CONSUMED = "consumed"  # item was consumed in present node
    IN_TRANSIT = "in-transit"


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
        self.name = "sc-stage-{}".format(node_process.node.get_id())
        self.item_dep = node_process.node.get_dependency()
        self.inbound_material = Queue() if self.item_dep else None
        self.outbound_material = Queue()
        self.time_per_batch = time_per_batch
        self.state_helper = node_process.state_helper
        self.cluster = node_process.cluster
        self.node_id = node_process.node.get_id()
        self.node = node_process.node
        self.send_message = node_process.sendMessage  # function to send messages to cluster

        self.inbound_log = FileDict(abspath("./tmp/" + self.name + ".inbound.log"))
        self.outbound_log = FileDict(abspath("./tmp/" + self.name + ".outbound.log"))

        # dict to keep track of requests that haven't gotten
        # a response and need additional retries.
        self.pending_requests = {}

        # hack to stop stage
        self.running = Event()
        self.running.set()  # set the stage to run by default

        self.manufacture_count = 0
        self._attempt_log_recovery()

    def _attempt_log_recovery(self):
        '''
            attempts to populate the in-memory data structures from
            data in the disk log if there is any.

            uses raftos

            The log is unique to the stage using the stage-name as the key.

            TODO
        '''
        for item, state in self.inbound_log.items():
            if state == StageStatus.IN_QUEUE:
                self.inbound_material.put(item)

        for item, state in self.outbound_log.items():
            # TODO
            # check with neighbors if the item status
            # in the logs is accurate. i.e. if it is marked
            # in-transit or in-queue or consumed in their logs.
            if state == StageStatus.IN_QUEUE:
                self.outbound_material.put(item)
            elif state == StageStatus.IN_TRANSIT:
                pass
            self.manufacture_count += 1

        return

    def stop(self):
        '''
            - Stop the stage's priduction & consumption loop.
            - Destory the inbound and outbound queues.

            Used for testing.
        '''
        # stop the production loop
        self.running.clear()
        # flush & invalidate the queues
        self.inbound_material = self.outbound_material = None
        # leave the logs for the next stage instance with the same
        # name to pick up

    def get_stage_result_type(self):
        return self.item_dep.get_result_type()

    def get_manufacture_count(self):
        '''
            returns the count of items produced by the stage since the
            first time the stage was created.
        '''
        return self.manufacture_count

    def get_inbound_waiting_items_count(self):
        return self.inbound_material.qsize()

    def get_outbound_waiting_items_count(self):
        return self.outbound_material.qsize()

    def _send_material_requests_upstream(self):
        '''
            Identifies the nodes from where parts are to be requested
            and makes a request for the parts from that node.
        '''
        if not self.item_dep.has_prereq():
            # stage requires no inbound material.
            log.debug("Node %d has no inbound materials to acquire. "
                      "Continuing without making material request.", self.node_id)
            return True, []

        flow = self.state_helper.get_flow()
        if not flow:
            log.error("Unable to retrieve flow to acquire items %s for manufacture in node %d",
                      self.item_dep.get_prereq(), self.node_id)
            return False, []

        suppliers = flow.getIncomingFlowsForNode(self.node_id)
        supplier_ids = [sid for sid, _ in suppliers]
        log.debug("Node %d seeing suppliers %s in flow", self.node_id, supplier_ids)

        for supplier_id, supplier_type in suppliers:
            batch_request = BatchRequest(
                source=self.node_id,
                dest=supplier_id,
                item_req=supplier_type,
                request_id=str(uuid4())[:8],  # HACK for unique but short request IDs
            )
            self.send_message(batch_request)
            self.pending_requests[batch_request.request_id] = batch_request
            log.debug("Node %d sent a material batch request %s", self.node_id, batch_request)

        return True, supplier_ids

    def _retry_pending_requests(self):
        if self.pending_requests:
            log.debug("Node %d retrying %d requests that did not receive a response", self.node_id, len(self.pending_requests))
            for request in self.pending_requests:
                # log.debug("[TODO] Node %d retrying request %s", self.node_id, request)
                pass

    def _mark_request_complete(self, response):
        '''
            Removes the request ID in the response from pending requests.
            i.e. The request ID was created when this stage made a request and
            the rid was added to the pending_requests until a response was received.
        '''
        try:
            del self.pending_requests[response.request_id]
        except KeyError:
            log.warning("Node %d unable to find request id %s in pending requests but got a response %s",
                        self.node_id, response.request_id, response)

    def reply_to_batch_status_query(self, request: Message):
        log.debug("Received batch status check query %s", request)
        # TODO
        # reply with right the status of the item as present in
        # the node's inbound/outbound logs.
        assert request.action == BatchStatusRequest

    def process_item_waiting_response(self, message):
        log.debug("Stage at node %s is now waiting for batch %s from %d",
                  message.source, message.item_req, self.node_id)
        batch = message.item_req
        curr_status = self.outbound_log[batch]
        if curr_status != StageStatus.IN_TRANSIT:
            log.warning("Node %d's outbound log for item %s was at status %s, expected %s",
                        self.node_id, batch, curr_status, StageStatus.IN_TRANSIT)
            self.outbound_log[batch] = StageStatus.IN_TRANSIT

    def process_batch_request(self, request: Message):
        log.debug("Node %d received request %s", self.node_id, request)

        # verif the right item type is being requested
        if request.item_req.item.type != self.get_stage_result_type():
            log.error("Node %d requested to supply %s but it produces %s",
                      self.node_id, request.item_req, self.get_stage_result_type())

        # verify the right node is making the request
        flow = self.state_helper.get_flow()
        if flow:
            allowed_requesters = flow.getOutgoingFlowsForNode(self.node_id)
            allowed_requesters = [sid for sid, _ in allowed_requesters]
            if request.source not in allowed_requesters:
                log.error("Node %d got a supply request from %d but %d's outgoing edges are %s",
                          self.node_id, request.source, self.node_id, allowed_requesters)
        else:
            log.error("Node %d unable to retrieve flow to acquire items %s",
                      self.node_id, self.item_dep.get_prereq())

        try:
            # outbound queue has items waiting to be sent
            produced_batch = self.outbound_material.get()
            self.inbound_log[produced_batch] = StageStatus.IN_TRANSIT

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
        log.debug("Node %d got %s after request %s", self.node_id, response, response.request_id)
        if isinstance(response, BatchSentResponse):
            material = response.item_req
            if not self.item_dep.is_valid_material(material):
                log.error("Node %d received invalid batch %s from node %d. Node %d's deps are %s. Ignoring received batch.",
                          self.node_id, material, response.source, self.node_id, self.item_dep)
                return

            self.inbound_log[material] = StageStatus.IN_TRANSIT

            ack = WaitingForBatchResponse(
                source=self.node_id,
                dest=response.source,
                item_req=material,
                request_id=response.request_id,
            )
            self.send_message(ack)
            log.info("Node %d marked material %s in-transit from upstream node", self.node_id, response.item_req)

            sleep(self.time_per_batch)  # HACK simulated transit time

            self.inbound_log[material] = StageStatus.IN_QUEUE
            ack = BatchDeliveryConfirmResponse(
                source=self.node_id,
                dest=response.source,
                item_req=material,
                request_id=response.request_id,
            )
            self.send_message(ack)
            self.inbound_material.put(material)
            log.info("Node %d received %s from upstream node %d",
                     self.node_id, response.item_req, response.source)
        else:
            log.error("Node %d unable to obtain %s from node %d. Request ID: %s",
                      self.node_id, response.item_req, response.source, response.request_id)

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
        self.outbound_log[item] = StageStatus.DELIVERED

    def _manufacture_batch_and_enqueue(self, suppliers: List[int]):
        '''
            TODO
            logic to poll/query/update the inbound queue until it can make one unit of
            the output using the right quantities by reffering to the item_dep.

            This is a blocking call since it has to wait on the inbound queue.
        '''
        if self.item_dep.has_prereq():
            try:
                # For each manufactured batch item, do a get() in the inbound queue once.
                # NOTE/FIXME/TODO
                # This does not work if batches of different item quantities
                # and item types are required by the stage's inbound requirements.
                # The manufacture logic assumes each result batch can be made with
                # any, single, incoming batch.
                log.info("Node %d waiting for %s from %s", self.node_id, self.item_dep.get_prereq(), suppliers)
                material_req = self.inbound_material.get(timeout=5)  # HACK wait at most 5 seconds for a material batch
                self.inbound_log[material_req] = StageStatus.CONSUMED
                log.info("Node %d successfully consumed %s", self.node_id, material_req)
            except Empty:
                # queue is empty, need to wait till it's not.
                log.warning("Node %d's inbound material queue is empty but needs %s. Skipping manufacturing of one batch of item type %s",
                            self.node_id, self.item_dep.get_prereq(), self.get_stage_result_type())
                return

        new_item_id = str(self.get_stage_result_type()) + '-' + str(self._generate_new_item_id())
        new_item = Item(_type=self.get_stage_result_type(), _id=new_item_id)
        new_batch = ItemReq(new_item, 1)  # TODO/FIXME assumes batch size is always 1

        self.outbound_log[new_batch] = StageStatus.IN_QUEUE
        self.outbound_material.put(new_batch)
        self.manufacture_count += 1
        log.debug("Node %d successfully manufactured batch %s and enqueued to outbound queue",
                  self.node_id, new_batch)

    def run(self):

        log.debug("Starting manufacturing cycle of %s in node %d with stage %s",
                  self.get_stage_result_type(), self.node_id, self.name)
        while self.running.is_set():
            if self.node.state == NodeState.inactive:
                continue

            requested, suppliers = self._send_material_requests_upstream()
            if requested:
                self._manufacture_batch_and_enqueue(suppliers)

            self._retry_pending_requests()

            sleep(self.time_per_batch)
