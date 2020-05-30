import enum
import logging
import cluster as ctr

from nodes import BaseNode
from items import ItemDependency


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


class Message(object):
    """
    Base class for all messages
    """

    ALL = "all"

    def __init__(self, source, action: Action, typeVal: MsgType, dest=ALL):
        self.type = typeVal
        self.source = source
        self.dest = dest
        self.action = action

        # Allow any basic types for source, dest
        assert type(self.source) in [str, int], "Invalid type of source: {}".format(self.source)
        assert type(self.dest) in [str, int], "Invalid type of dest: {}".format(self.dest)

    def __repr__(self):
        return "{}-{}:{}->{}".format(self.action, self.type, self.source, self.dest)


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


class MessageHandler(object):
    """
        Message Handler responsible for managing and manipulating state mutations upon sending and receiving messages
        In order to support any given action in the MessageHandler, follow the below steps.
            1. Add the necessary action type in Action e.g. Heartbeat
            2. Add on request and response functions for the action e.g. on_heartbeat_req and on_heartbeat_resp
            3. Add the function to the callbacks in get_action_callbacks
    """

    @staticmethod
    def getMsgForAction(source, action: Action, type: MsgType, dest=""):
        """
            returns an object of type Message for the specified message
        """
        if action == Action.Allocate:
            return AllocateReq(source)
        elif action == Action.Heartbeat:
            if type == MsgType.Request:
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
        '''
            ops: operations the node will run when it starts.
            callback: the callback to send a message
        '''
        super(MessageHandler, self).__init__()

        self.node_process = node_process
        self.node = node_process.node
        self.node_id = node_process.node.get_id()
        self.callbacks = self.get_action_callbacks()

    def get_action_callbacks(self):
        """
        Fill details of all callbacks in this function. See existing instances for examples
        """
        request_callbacks = {
            Action.Heartbeat: self.on_heartbeat_req,
            Action.Death: self.none_fn,
            Action.ReAllocate: self.none_fn,
            Action.Allocate: self.none_fn,
            Action.Ack: self.none_fn,
            Action.Update: self.on_update_req,
        }
        response_callbacks = {
            Action.Heartbeat: self.on_heartbeat_resp,
            Action.Death: self.none_fn,
            Action.ReAllocate: self.none_fn,
            Action.Allocate: self.none_fn,
            Action.Ack: self.none_fn,
            Action.Update: self.on_update_resp,
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
        if is_msg_from_me:
            # Ignore the message from myself
            return None
        elif is_msg_for_all or is_msg_for_me:
            log.info("Received: %s from %s", message, message.source)
            return self.callbacks[message.type][message.action](message)
        else:
            return None

    """
    Callback implementations of all possible messages and their requests/response variants
    MessageHandler has access to specifics of
    """

    def none_fn(self, _message):
        pass

    def on_heartbeat_req(self, message):
        assert message.action == Action.Heartbeat
        response = MessageHandler.getMsgForAction(
            source=self.node.node_id,
            action=message.action,
            type=MsgType.Response,
            dest=message.source
        )
        self.sendMessage(response)

    def on_heartbeat_resp(self, message):
        assert message.action == Action.Heartbeat
        log.debug("Received Heartbeat Response from %s: on %s", message.source, self.node_id)
        self.node_process.update_heartbeat(message.source)

    def on_update_req(self, message):
        assert message.action == Action.Update

        is_leader = self.node_process.state_helper.am_i_leader()
        # TODO: add handling when this is not the leader; Simple fail and retry on source?
        if is_leader:
            # TODO: Create efficient restructure strategy once Andrej's flow algorithm handles more complex topologies
            # flow = self.node_process.raft_helper.get_flow()
            self.node_process.cluster.update_deps(message.source, message.dependency)
            new_flow = ctr.bootstrap_shortest_path(self.node_process.cluster.nodes)
            self.node_process.state_helper.update_flow(new_flow)

            # Send an ack
            response = MessageHandler.getMsgForAction(
                source=self.node.node_id,
                action=Action.Ack,
                type=MsgType.Response,
                dest=message.source
            )
            self.sendMessage(response)

    def on_update_resp(self, message):
        log.debug("%s : Update Resp received: {}", message.source)
