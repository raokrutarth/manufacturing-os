from threading import Thread, Event
from queue import Queue, Empty
from time import sleep
import logging
from string import ascii_uppercase, digits
from random import choice
from os.path import abspath
from uuid import uuid4


from items import Item, ItemDependency, ItemReq
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
            # TODO (Chen)
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

    def clear_logs(self):
        '''
            used for testing
        '''
        self.inbound_log.clear()
        self.outbound_log.clear()

    def get_outbound_queue(self):
        return self.outbound_material

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

    def _acquire_needed_materials(self):
        '''
            Identifies the nodes from where parts are to be requested
            and makes a request for the parts from that node.
        '''
        if not self.item_dep.has_prereq():
            # stage requires no inbound material.
            log.debug("Node %d has no inbound materials to acquire. "
                      "Continuing without making material request.", self.node_id)
            return True

        flow = self.state_helper.get_flow()
        if not flow:
            log.error("Unable to retrieve flow to acquire items %s for manufacture in node %d",
                      self.item_dep.get_prereq(), self.node_id)
            return False

        for required_item in iter(self.item_dep.input_item_reqs):
            for node_id in flow.get_inbound_node_ids():
                batch_request = BatchRequest(
                    source=self.node_id,
                    dest=node_id,
                    item_req=required_item,
                    request_id=str(uuid4())[:8],  # HACK for unique but short request IDs
                )
                self.send_message(batch_request)
                self.pending_requests[batch_request.request_id] = batch_request

        return True

    def reply_to_batch_status_query(self, request: Message):
        log.debug("Received batch status check query %s", request)
        # TODO Chen
        # reply with right the status of the item as present in
        # the node's inbound/outbound logs.
        assert request.action == BatchStatusRequest

    def process_item_waiting_response(self, message):
        log.debug("Stage at node %s is now waiting for batch %s", message.source, message.item_req)
        batch = message.item_req
        assert self.outbound_log[batch] == StageStatus.IN_TRANSIT

    def process_batch_request(self, request: Message):
        log.debug("Node %d received request %s", self.node_id, request)
        # TODO verify request.source is allowed to make requests to this node
        if request.item_req.item.type != self.get_stage_result_type():
            log.error("Node %d requested to supply %s but it produces %s",
                      self.node_id, request.item_req, self.get_stage_result_type())
            reply = BatchUnavailableResponse(
                source=self.node_id,
                dest=request.source,
                item_req=request.item_req,
                request_id=request.request_id,
            )
            self.send_message(reply)
            return

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
            log.info("Successfully sent part %s in reply to request %s", produced_batch, request)
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
                log.error("Invalid batch of %s sent to node with deps %s. Ignoring item.", material, self.item_dep)
                return

            self.inbound_log[material] = StageStatus.IN_TRANSIT

            ack = WaitingForBatchResponse(
                source=self.node_id,
                dest=response.source,
                item_req=material,
                request_id=response.request_id,
            )
            self.send_message(ack)
            log.info("Material %s marked in-transit from upstream node", response.item_req)

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

        try:
            del self.pending_requests[response.request_id]
        except KeyError:
            log.warning("Node %d unable to find request id %s in pending requests but got a response for it.",
                        self.node_id, response.request_id)

    def _generate_new_item_id(self):
        return ''.join(choice(ascii_uppercase) for _ in range(5)) + \
            ''.join(choice(digits) for _ in range(3))

    def mark_item_delivered(self, message: Message):
        '''
            callback invoked by the node to mark
            an result item delivered to a downstream
            node. updates the persistant log.
        '''
        item = message.item_req
        self.outbound_log[item] = StageStatus.DELIVERED

    def manufacture_batch_and_enqueue(self):
        '''
            TODO
            logic to poll/query/update the inbound queue until it can make one unit of
            the output using the right quantities by reffering to the item_dep.

            This is a blocking call since it has to wait on the inbound queue.
        '''

        if self.item_dep.has_prereq():
            try:
                # TODO add support of multiple inbound item types to produce single result
                # type. i.e. add inbound queues per inbounf item type.
                material = self.inbound_material.get()
                self.inbound_log[material] = StageStatus.CONSUMED
                log.info("Successfully consumed %s in node %s", material, self.node_id)
            except Empty:
                # queue is empty, need to wait till it's not.
                log.error("Inbound material queue on stage at node %d was empty. "
                          "Skipping manufacturing of a batch of %s",
                          self.node_id, self.get_stage_result_type())
                return

        new_item_id = self.get_stage_result_type() + '-' + self._generate_new_item_id()
        new_item = Item(_type=self.get_stage_result_type(), _id=new_item_id)
        self.outbound_log[new_item] = StageStatus.IN_QUEUE
        self.outbound_material.put(new_item)
        self.manufacture_count += 1
        log.debug("Node %d successfully manufactured item %s and enqueued to outbound queue",
                  self.node_id, new_item)

    def run(self):

        log.debug("Starting manufacturing cycle of %s in node %d with stage %s",
                  self.get_stage_result_type(), self.node_id, self.name)
        while self.running.is_set():
            if self._acquire_needed_materials():
                self.manufacture_batch_and_enqueue()
            sleep(self.time_per_batch)
