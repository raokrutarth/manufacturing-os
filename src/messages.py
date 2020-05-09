import enum
import logging

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

    def __init__(self, source: BaseNode, action: Action, type: MsgType, dest=None):
        self.type = type
        self.source = source
        self.dest = dest
        self.action = action

    def __repr__(self):
        return "{}-{}:{}->{}".format(self.action, self.type, self.source, self.dest)


class Ack(Message):

    def __init__(self, source: BaseNode, dest: BaseNode, msgId):
        super(Ack, self).__init__(source, Action.Allocate, MsgType.Response, dest)
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

    def __init__(self, source: BaseNode):
        super(AllocateReq, self).__init__(source, Action.Allocate, MsgType.Request)


class AllocateResp(Message):
    """
    Nodes replying their requirements, capacity, supply, etc
    """

    def __init__(self, source: BaseNode, dest: BaseNode, dependency: ItemDependency):
        super(AllocateResp, self).__init__(source, Action.Allocate, MsgType.Response, dest)
        self.dependency = dependency


class AllocateCommit(Message):
    """
    Leader sending message to commit for the specified flow;
    Contains the allocated dependency for the node
    """

    def __init__(self, source: BaseNode, dependency: ItemDependency):
        super(AllocateCommit, self).__init__(source, Action.Allocate, MsgType.Request)
        self.dependency = dependency


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

    def __init__(self, source: BaseNode, new_dependency: ItemDependency):
        super(UpdateReq, self).__init__(source, Action.Update, MsgType.Request)
        self.dependency = new_dependency

    def __repr__(self):
        return "{}, NewDependency: {}".format(super(UpdateReq, self).__repr__(), self.dependency)
#
#
# class MessageHandler(object):
#     """
#     Message handler
#     """
#
#     def __init__(self, node_process: 'SocketBasedNodeProcess', ops: List[Op], callback: 'sendMessage', delay=1):
#         '''
#             ops: operations the node will run when it starts.
#             callback: the callback to send a message
#         '''
#         super(OpsRunnerThread, self).__init__()
#
#         self.node_process = node_process
#         self.callback = callback
#         self.ops_to_run = ops
#         self.delay = delay
#
#         self.node_id = node_process.node.get_name()
#
#     def get_message_from_op(self, op):
#         log.info('node %s constructing message for operation %s', self.node_id, op)
#         return OpHandler.getMsgForOp(self.node_id, op)
#
#     def run(self):
#         log.debug('node %s running operation thread with operations %s', self.node_id, self.ops_to_run)
#
#         # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
#         sleep(self.delay)
#
#         for op in self.ops_to_run:
#             msg = self.get_message_from_op(op)
#             self.callback(msg)
#             sleep(self.delay)
#
#         log.debug('node %s finished running operations %s', self.node_id, self.ops_to_run)
