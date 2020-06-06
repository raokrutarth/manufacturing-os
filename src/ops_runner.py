import logging
import random
import items
import messages
import copy

from threading import Thread
from time import sleep
from typing import List
from nodes import SingleItemNode, NodeState
from operations import Operations as Op

log = logging.getLogger()

class OpHandler:

    @staticmethod
    def getMsgForOp(source: SingleItemNode, op: Op, dest=""):
        '''
            returns an object of type Message from messages.py.
        '''
        source_id = source.node_id
        if op == Op.TriggerAllocate:
            return messages.AllocateReq(source_id)
        elif op == Op.SendHeartbeat:
            if type == messages.MsgType.Request:
               return messages.HeartbeatReq(source_id)
            else:
               return messages.HeartbeatResp(source_id, dest)
        elif op == Op.SendUpdateDep:
            return messages.UpdateReq(source_id, items.ItemDependency.halveDependency(source.dependency))
        elif op == Op.Kill:
            return messages.UpdateReq(source_id, items.ItemDependency.newNullDependency())
        elif op == Op.Recover:
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

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay=1):
        '''
            ops: operations the node will run when it starts.
            callback: the callback to send a message
        '''
        super(OpsRunnerThread, self).__init__()

        self.node_process = node_process
        self.delay = delay

        self.node = node_process.node
        self.node_id = node_process.node.get_id()

    def get_message_from_op(self, op):
        log.debug('node %s constructing message for operation %s', self.node_id, op)
        return OpHandler.getMsgForOp(self.node, op)

    def is_node_part_of_flow(self, node_id):
        leader = self.node_process.state_helper.get_leader()
        flow = self.node_process.state_helper.get_flow()
        if leader == self.node.node_id:
            return False
        elif flow is not None:
            try:
                ins = len(flow.getIncomingFlowsForNode(str(node_id)))
                outs = len(flow.getOutgoingFlowsForNode(str(node_id)))
                # if both ins !=0 and outs !=0, then has both incoming and outgoing
                if (ins * outs) > 0:
                    return True
            except Exception:
                return False
        else:
            return False

    def run(self):
        log.warning('node %s running operation thread with operations %s', self.node_id, self.node_process.op_queue)

        # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
        sleep(self.delay)

        while True:
            op = self.node_process.op_queue.get()
            if op == Op.Kill:
                self.node_process.on_kill()
            elif op == Op.Recover:
                self.node_process.on_recover()
            else:
                if self.node_process.node.state == NodeState.active:
                    msg = self.get_message_from_op(op)
                    self.node_process.sendMessage(msg)
            sleep(self.delay)

        log.warning('node %s finished running operations %s', self.node_id, self.node_process.op_queue)