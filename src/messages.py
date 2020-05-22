import enum
import logging
import cluster as ctr

from nodes import BaseNode
from items import ItemDependency, ItemReq


log = logging.getLogger()


class MsgType(enum.Enum):
    Request = 1
    Response = 2


class Action(enum.Enum):
    """
    Stores classes for actions allowed between different nodes
    """

    # Inits a heartbeat from a node
    Heartbeat = 1

    # Signals death of node
    Death = 2

    # Signals to perform re-allocation; different from allocate in case we use a
    # different optimized algorithm for
    # re-allocation
    ReAllocate = 3

    # Signals to initiate initial flow allocation consensus
    Allocate = 4

    # Signals a generic Ack
    Ack = 5

    # Signals to update dependency i.e. production-consumption requirements
    Update = 6

    # Signals used by SC stage to keep track of inventory
    # For nodes A -> B:
    #  - B requests material batch from A with RequestMaterialBatch.
    #  - A sends a SentItemBatch or ItemBatchNotAvailable to B.
    #  - B sends a WaitingForMaterialBatch to A.
    #  - B sends a BatchDeliveryConfirm to A after delivery.
    RequestMaterialBatch = 7
    SentItemBatch = 8
    ItemBatchNotAvailable = 9
    WaitingForMaterialBatch = 10  # like an ack for SentItemBatch
    BatchDeliveryConfirm = 11

    # Signals used by SC stage in crash recovery
    # For nodes A -> B & A crashed:
    #  - A wakes up and verifies for all items marked in-transit/in-queue is accurate in log.
    #  - B replies with a BatchDeliveryConfirm, WaitingForMaterialBatch or
    #    ItemBatchNotAvailable by looking at it's log.
    CheckBatchStatus = 12


class Message(object):
    """
    Base class for all messages
    """

    ALL = -1  # assumes a node id is always an int > 0

    def __init__(self, source, action: Action, typeVal: MsgType, dest=ALL):
        '''
            source: node_id of the node sending the message.
            dest: node_id of the intended recepient.
            type: can be response/request.
            action: determines the purpose of the message.
        '''
        self.type = typeVal
        self.source = source
        self.dest = dest
        self.action = action

        # NOTE
        # since the source and dest are node_ids, make sure the values
        # qualify as valid node_ids. Skipping the check to verify if the id
        # is a valid id of a node in the cluster.
        assert isinstance(self.source, int), "Invalid type of source: {}".format(self.source)
        assert isinstance(self.dest, int), "Invalid type of dest: {}".format(self.dest)

    def __repr__(self):
        return "Message(from:{}, to:{}, type:{}, action:{})" \
            .format(self.source, self.dest, self.type, self.action)


class AckResp(Message):

    def __init__(self, source, dest, msgId=""):
        super(AckResp, self).__init__(source, Action.Ack, MsgType.Response, dest)
        self.msgId = msgId


"""
Helper classes for Allocation related operations. Current implementation assumes,
    Step 1. AllocateReq
    Step 2. AllocateResp
    Step 3. AllocateCommit
"""


class AllocateReq(Message):
    """
    Signal to every node to communicate their supply requirements
    """

    def __init__(self, source):
        super(AllocateReq, self).__init__(source, Action.Allocate, MsgType.Request)


class AllocateResp(Message):
    """
    Nodes replying their requirements, capacity, supply, etc
    """

    def __init__(self, source, dest, dependency: ItemDependency):
        super(AllocateResp, self).__init__(source, Action.Allocate, MsgType.Response, dest)
        self.dependency = dependency


class AllocateCommit(Message):
    """
    Leader sending message to commit for the specified flow;
    Contains the allocated dependency for the node
    """

    def __init__(self, source, dependency: ItemDependency):
        super(AllocateCommit, self).__init__(source, Action.Allocate, MsgType.Request)
        self.dependency = dependency


class HeartbeatReq(Message):
    """
    Signal to every node to response with heartbeat
    """
    def __init__(self, source):
        super(HeartbeatReq, self).__init__(source, Action.Heartbeat, MsgType.Request)


class HeartbeatResp(Message):
    """
    Nodes replaying their heartbeat
    """
    def __init__(self, source, dest):
        super(HeartbeatResp, self).__init__(source, Action.Heartbeat, MsgType.Response, dest)


"""
Helper classes for Update related operations. Current implementation assumes,
    Step 1. UpdateReq
    Step 2. Source gets Ack from Leader
    Step 3. Leader performs reallocation using the Allocate Paradigm
"""


class UpdateReq(Message):
    """
    Signal to every node to that the source has updated its requirements
    """

    def __init__(self, source, new_dependency: ItemDependency):
        super(UpdateReq, self).__init__(source, Action.Update, MsgType.Request)
        self.dependency = new_dependency

    def __repr__(self):
        return "{}, NewDependency: {}".format(super(UpdateReq, self).__repr__(), self.dependency)

"""
    Helper classes for SC Stage related operations
    NOTE:
        - The request_id field allows the sender of the request to keep track of
          requests that have received a reply. Should be unique per request.
"""

class BatchRequest(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(BatchRequest, self).__init__(source, Action.RequestMaterialBatch, MsgType.Request, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "BatchRequest(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )

class BatchStatusRequest(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(BatchStatusRequest, self).__init__(source, Action.CheckBatchStatus, MsgType.Request, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "BatchStatusRequest(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )

class BatchSentResponse(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(BatchSentResponse, self).__init__(source, Action.SentItemBatch, MsgType.Response, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "BatchSentResponse(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )

class BatchUnavailableResponse(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(BatchUnavailableResponse, self).__init__(source, Action.ItemBatchNotAvailable, MsgType.Response, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "BatchUnavailableResponse(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )

class WaitingForBatchResponse(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(WaitingForBatchResponse, self).__init__(source, Action.ItemBatchNotAvailable, MsgType.Response, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "WaitingForBatchResponse(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )

class BatchDeliveryConfirmResponse(Message):
    def __init__(self, source: int, dest: int, item_req: ItemReq, request_id: str):
        super(BatchDeliveryConfirmResponse, self).__init__(source, Action.ItemBatchNotAvailable, MsgType.Response, dest)
        self.item_req = item_req
        self.request_id = request_id

    def __repr__(self):
        return "BatchDeliveryConfirmResponse(from:{}, to: {}, batch:{}, req-id:{})".format(
            self.source, self.dest, self.item_req, self.request_id,
        )


class MessageHandler(object):
    """
        Message Handler responsible for managing and manipulating state mutations upon sending and receiving messages
        In order to support any given action in the MessageHandler, follow the below steps.
            1. Add the necessary action type in Action e.g. Heartbeat
            2. Add on request and response functions for the action e.g. on_heartbeat_req and on_heartbeat_resp
            3. Add the function to the callbacks in get_action_callbacks
    """

    @staticmethod
    def getMsgForAction(source, action: Action, msg_type: MsgType, dest=""):
        """
            returns an object of type Message for the specified message
        """
        if action == Action.Allocate:
            return AllocateReq(source)
        elif action == Action.Heartbeat:
            if msg_type == MsgType.Request:
                return HeartbeatReq(source)
            else:
                return HeartbeatResp(source, dest)
        elif action == Action.Update:
            return UpdateReq(source, ItemDependency.newNullDependency())
        elif action == Action.Death:
            return UpdateReq(source, ItemDependency.newNullDependency())
        elif action == Action.Ack:
            return AckResp(source, dest)
        else:
            assert False, "Invalid action: {}".format(action.name)

    def __init__(self, node_process: 'SocketBasedNodeProcess'):
        super(MessageHandler, self).__init__()

        self.node_process = node_process
        self.node = node_process.node
        self.sc_stage = node_process.sc_stage
        self.node_id = node_process.node.get_id()
        self.callbacks = self.get_action_callbacks()

    def get_action_callbacks(self):
        """
            Returns the message type -> function nested map
            where the functions are implemented by the message handler
            as callbacks for a given request/response type.
        """
        request_callbacks = {
            Action.Heartbeat: self.on_heartbeat_req,
            Action.Death: self.none_fn,
            Action.ReAllocate: self.none_fn,
            Action.Allocate: self.none_fn,
            Action.Ack: self.none_fn,
            Action.Update: self.on_update_req,

            Action.RequestMaterialBatch: self.on_request_material_req,
            Action.CheckBatchStatus: self.on_check_batch_status_req,
        }
        response_callbacks = {
            Action.Heartbeat: self.on_heartbeat_resp,
            Action.Death: self.none_fn,
            Action.ReAllocate: self.none_fn,
            Action.Allocate: self.none_fn,
            Action.Ack: self.none_fn,
            Action.Update: self.on_update_resp,

            Action.SentItemBatch: self.on_item_sent_resp,
            Action.BatchDeliveryConfirm: self.on_batch_unavailable_resp,
            Action.ItemBatchNotAvailable: self.on_batch_unavailable_resp,
            Action.WaitingForMaterialBatch: self.on_item_waiting_resp,
            Action.BatchDeliveryConfirm: self.on_delivery_confirmed_resp,
        }
        callbacks = {
            MsgType.Response: response_callbacks,
            MsgType.Request: request_callbacks,
        }
        return callbacks

    def sendMessage(self, message):
        log.info("sending message %s from node %s", message, self.node.node_id)
        self.node_process.message_queue.put(message)

    def onMessage(self, message):
        is_msg_for_all = message.dest == Message.ALL
        is_msg_for_me = message.dest == self.node_id
        is_msg_from_me = message.source == self.node_id

        if is_msg_for_all or is_msg_for_me and not is_msg_from_me:
            log.info("Received: %s from %s", message, message.source)
            return self.callbacks[message.type][message.action](message)

        return None

    """
    Callback implementations of all possible messages and their requests/response variants
    MessageHandler has access to specifics of
    """

    def none_fn(self, _message):
        pass

    def on_request_material_req(self, message: Message):
        '''
            Callback implementing the actions to be taken when a downstream
            node requests material made by self.node.sc_stage.
        '''
        # TODO
        # call the node's stage API to pop an item off the
        # outbound queue and mark item in-transit and send SentItemBatch.
        # if item not available send ItemBatchNotAvailable
        assert message.action == Action.RequestMaterialBatch
        self.sc_stage.process_batch_request(message)

    def on_item_sent_resp(self, message: Message):
        '''
            Callback implementing the actions to be taken when an upstream
            node confirms that it sent an item batch.

            Message is a response to a RequestMaterialBatch or CheckBatchStatus request.
        '''
        assert message.action == Action.SentItemBatch
        self.sc_stage.process_batch_request_response(message)

    def on_batch_unavailable_resp(self, message: Message):
        '''
            Callback implementing the actions to be taken when an upstream
            node denies to send an item batch.

            Message is a response to a RequestMaterialBatch request by upstream node.
        '''
        assert message.action == Action.ItemBatchNotAvailable
        self.sc_stage.process_batch_request_response(message)

    def on_item_waiting_resp(self, message: Message):
        '''
            Callback implementing the actions to be taken when an downstream
            node acknowledges it will wait for an item as the item is in-transit.

            Message is a response to SentItemBatch or CheckBatchStatus messages.
        '''
        assert message.action == Action.WaitingForMaterialBatch
        self.sc_stage.process_item_waiting_response(message)

    def on_delivery_confirmed_resp(self, message: Message):
        '''
            Callback implementing the actions to be taken when an downstream
            node confirmed an item was received downstream.

            Message can a response to CheckBatchStatus messages or a follow-up
            response to SentItemBatch (after a WaitingForMaterialBatch).
        '''
        assert message.action == Action.BatchDeliveryConfirm
        self.sc_stage.mark_item_delivered(message)

    def on_check_batch_status_req(self, message: Message):
        '''
            Callback implementing the actions to be taken when a neighbor
            node makes a request to check the status of a batch.

            Can reply with ItemBatchNotAvailable, BatchDeliveryConfirm, WaitingForMaterialBatch
            SentItemBatch
        '''
        assert message.action == Action.CheckBatchStatus
        self.sc_stage.reply_to_batch_status_query(message)


    def on_heartbeat_req(self, message):
        assert message.action == Action.Heartbeat
        response = MessageHandler.getMsgForAction(
            source=self.node.node_id,
            action=message.action,
            msg_type=MsgType.Response,
            dest=message.source
        )
        self.sendMessage(response)

    def on_heartbeat_resp(self, message):
        assert message.action == Action.Heartbeat
        log.debug("Received Heartbeat Response from %s: on %s", message.source, self.node_id)
        self.node_process.update_heartbeat(message.source)

    # TODO: No await here! Causes something downstream to fail for some reason.
    #  Figure out how to convert this into async
    def on_update_req(self, message):
        assert message.action == Action.Update

        is_leader = self.node_process.raft_helper.am_i_leader()
        # TODO: add handling when this is not the leader; Simple fail and retry on source?
        if is_leader:
            # TODO: Create efficient restructure strategy once Andrej's flow algorithm handles more complex topologies
            # flow = self.node_process.raft_helper.get_flow()
            self.node_process.cluster.update_deps(message.source, message.dependency)
            new_flow = ctr.bootstrap_shortest_path(self.node_process.cluster.nodes)
            self.node_process.raft_helper.update_flow(new_flow)

            # Send an ack
            response = MessageHandler.getMsgForAction(
                source=self.node.node_id,
                action=Action.Ack,
                msg_type=MsgType.Response,
                dest=message.source
            )
            self.sendMessage(response)

    def on_update_resp(self, message):
        log.debug("%s : Update Resp received: {}", message.source)
