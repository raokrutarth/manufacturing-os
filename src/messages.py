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

    # Signals to initiate leader election
    ElectLeader = 2

    # Notifies everyone of death
    Death = 3

    # Signals to perform re-allocation; different from allocate in case we use a
    # different optimized algorithm for
    # re-allocation - which we should ideally do
    ReAllocate = 4

    # Signals to initiate initial flow allocation consensus
    Allocate = 5

    # Signals an generic Ack
    Ack = 6


class Message(object):
    """
    Base class for all messages
    """

    def __init__(self, source: BaseNode, action: Action, type: MsgType, dest=None):
        self.type = type
        self.source = source
        self.dest = dest
        self.action = action


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

class HeartbeatReq(Message):
    """
    Signal to every node to response with heartbeat
    """
    def __init__(self, source: BaseNode):
        super(HeartbeatReq, self).__init__(source, Action.Heartbeat, MsgType.Request)

class HeartbeatResp(Message):
    """
    Nodes replaying their heartbeat
    """
    def __init__(self, source:BaseNode, dest:BaseNode, dependency:ItemDependency):
        super(HeartbeatReq, self).__init__(source, Action.Heartbeat, MsgType.Response, dest)
        self.dependency = dependency