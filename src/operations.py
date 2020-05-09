import enum
import logging
import copy
from threading import Thread
from time import sleep
from typing import List

import messages
from nodes import BaseNode


log = logging.getLogger()

class Op(enum.Enum):

    # Inits a heartbeat from a node
    Heartbeat = 1

    # Signals to initiate leader election
    ElectLeader = 2

    # Notifies everyone of death
    Death = 3

    # Signals to perform re-allocation; different from allocate in
    # case we use a different optimized algorithm for
    # re-allocation - which we should ideally do
    ReAllocate = 4

    """
    Operations which are supported right now
    """

    # Signals to initiate initial flow allocation consensus
    Allocate = 5


class OpHandler:

    @staticmethod
    def getMsgForOp(source: BaseNode, op: Op):
        '''
            TODO (Nishant): explain why this is needed.

            returns an object of type Message from messages.py.
            Which allows ___
        '''
        if op == Op.Allocate:
            return messages.AllocateReq(source)
        elif op == Op.Heartbeat:
            return messages.HeartbeatReq(source)
        else:
            assert False, "Invalid op: {}".format(op.name)

class OpsRunnerThread(Thread):
    '''
        Operation runner allows the node instinatiator to declare
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
        self.node_id = node_process.node.get_name()
        self.delay = delay

    def to_message_class(self, op):
        log.info('node %s constructing message for operation %s', self.node_id, op)
        return OpHandler.getMsgForOp(self.node_id, op)

    def run(self):
        log.debug('node %s running operation thread with operations %s',
            self.node_id, self.ops_to_run)

        # Add Heartbeat Action
        ops_to_run = copy.deepcopy(self.ops_to_run)
        ops_to_run.append(Op.Heartbeat)

        for op in ops_to_run:
            msg = self.to_message_class(op)
            self.callback(msg)
            sleep(self.delay)

        log.debug('node %s finished running bootstrap operations %s',
            self.node_id, self.ops_to_run)

