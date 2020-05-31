import enum
import logging
import random
import items
import messages
import copy

from threading import Thread
from time import sleep
from typing import List
from nodes import SingleItemNode


log = logging.getLogger()


class Op(enum.Enum):

    def __repr__(self):
        return "{}".format(self.name)

    # Inits a heartbeat from a node
    SendHeartbeat = 1

    # Notifies everyone of death
    BroadcastDeath = 2

    # Signals to perform re-allocation; different from allocate in case we
    # use a different optimized algorithm for re-allocation
    TriggerReAllocate = 4

    """
    Operations which are supported right now
    """

    # Signals to initiate initial flow allocation consensus
    TriggerAllocate = 3

    # Signals to broadcast update dep request i.e. update its production, consumption requirements
    SendUpdateDep = 5


class OpHandler:

    @staticmethod
    def getMsgForOp(source: SingleItemNode, op: Op, type: messages.MsgType=messages.MsgType.Request, dest=""):
        '''
            returns an object of type Message from messages.py.
        '''
        source_id = source.node_id
        if op == Op.TriggerAllocate:
            return messages.AllocateReq(source_id)
        elif op == op.SendHeartbeat:
            if type == messages.MsgType.Request:
               return messages.HeartbeatReq(source_id)
            else:
               return messages.HeartbeatResp(source_id, dest)
        elif op == Op.SendUpdateDep:
            return messages.UpdateReq(source_id, items.ItemDependency.halveDependency(source.dependency))
        elif op == Op.BroadcastDeath:
            return messages.UpdateReq(source_id, items.ItemDependency.newNullDependency())
        else:
            assert False, "Invalid op: {}".format(op.name)


class OpsRunnerThread(Thread):
    '''
        Operation runner allows the node initializer to declare
        the operations the node should take without having any influence
        from any other node.

        E.g. during a test, we want a specific node to run reallocate.

        NOTE:
            Not to be used during actual demo unless an operation needs to
            be simulated.
    '''

    def __init__(self, node_process: 'SocketBasedNodeProcess', ops: List, delay=1):
        '''
            ops: operations the node will run when it starts.
            callback: the callback to send a message
        '''
        super(OpsRunnerThread, self).__init__()

        self.node_process = node_process
        self.ops_to_run = ops
        self.delay = delay

        self.node = node_process.node
        self.node_id = node_process.node.get_id()

    def get_message_from_op(self, op):
        log.debug('node %s constructing message for operation %s', self.node_id, op)
        return OpHandler.getMsgForOp(self.node, op)

    def whether_to_kill_node(self):
        # Only kills a node if they are part of the supply chain
        leader = self.node_process.state_helper.get_leader()
        flow = self.node_process.state_helper.get_flow()
        if leader == self.node_id:
            return False
        elif flow is not None:
            try:
                ins = len(flow.getIncomingFlowsForNode(str(self.node_id)))
                outs = len(flow.getOutgoingFlowsForNode(str(self.node_id)))
                if (ins * outs) > 0:
                    if random.random() < 0.5:
                        log.warning("Killing node: {}".format(self.node_id))
                        return True
                    else:
                        return False
            except Exception:
                return False
        else:
            return False

    def run(self):
        log.warning('node %s running operation thread with operations %s', self.node_id, self.ops_to_run)

        # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
        sleep(1 * self.delay)

        for op in self.ops_to_run:
            msg = self.get_message_from_op(op)
            # Add hacky initial method to simulate conditional node death
            if op == Op.BroadcastDeath:
                if self.whether_to_kill_node():
                    self.node_process.sendMessage(msg)
            else:
                self.node_process.sendMessage(msg)
            sleep(self.delay)

        log.warning('node %s finished running operations %s', self.node_id, self.ops_to_run)
