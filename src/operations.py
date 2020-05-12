import enum
import logging
import messages
import items
import copy
from threading import Thread
from time import sleep
from typing import List

from nodes import BaseNode
from messages import MsgType


log = logging.getLogger()


class Op(enum.Enum):

    # Inits a heartbeat from a node
    Heartbeat = 1

    # Notifies everyone of death
    Death = 2

    # Signals to perform re-allocation; different from allocate in case we
    # use a different optimized algorithm for re-allocation
    ReAllocate = 4

    """
    Operations which are supported right now
    """

    # Signals to initiate initial flow allocation consensus
    Allocate = 3

    # Signals to broadcast update dep request i.e. update its production, consumption requirements
    UpdateDep = 5


class OpHandler:

    @staticmethod
    def getMsgForOp(source: BaseNode, op: Op, type: MsgType = MsgType.Request, dest=None):
        '''
            TODO (Nishant): explain why this is needed.

            returns an object of type Message from messages.py.
            Which allows ___
        '''
        if op == Op.Allocate:
            return messages.AllocateReq(source)
        elif op == op.Heartbeat:
            if type == MsgType.Request:
               return messages.HeartbeatReq(source)
            else:
               return messages.HeartbeatResp(source, dest)
        elif op == Op.UpdateDep:
            return messages.UpdateReq(source, items.ItemDependency.newNullDependency())
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

    def __init__(self, node_process: 'SocketBasedNodeProcess', ops: List, callback: 'sendMessage', delay=1):
        '''
            ops: operations the node will run when it starts.
            callback: the callback to send a message
        '''
        super(OpsRunnerThread, self).__init__()

        self.node_process = node_process
        self.callback = callback
        self.ops_to_run = ops
        self.delay = delay

        self.node_id = node_process.node.get_name()

    def get_message_from_op(self, op):
        log.info('node %s constructing message for operation %s', self.node_id, op)
        return OpHandler.getMsgForOp(self.node_id, op)

    def check_adjacent_nodes_liveness(self):
        log.debug('node %s running operation thread with heartbeat before %s', self.node_id, self.ops_to_run)

        # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
        sleep(3 * self.delay)
        # Append Hearbeat action to check liveness
        #self.ops_to_run.append(Op.Heartbeat)
        print("******* ops to run: ", len(self.ops_to_run), " , ", self.ops_to_run)

        for op in self.ops_to_run:
            heartbeat = OpHandler.getMsgForOp(source=self, op=op.Heartbeat, dest=self)
            self.node_process.sendMessage(heartbeat)
            sleep(self.delay)

        log.debug('node %s finished running heartbeat and ready to run operations %s', self.node_id, self.ops_to_run)

    def run(self):
        log.debug('node %s running operation thread with operations %s', self.node_id, self.ops_to_run)

        # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
        sleep(3 * self.delay)

        # Append Hearbeat action to check liveness
        self.ops_to_run.append(Op.Heartbeat)  # to be replaced by check_adjacent_nodes_liveness
        #self.check_adjacent_nodes_liveness()

        for op in self.ops_to_run:
            msg = self.get_message_from_op(op)
            self.callback(msg)
            sleep(self.delay)

        log.debug('node %s finished running operations %s', self.node_id, self.ops_to_run)
