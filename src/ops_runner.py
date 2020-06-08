import logging
import items
from threading import Thread
from time import sleep

import messages
from nodes import SingleItemNode, NodeState
from operations import Operations as Op

log = logging.getLogger()


class OpHandler:

    @staticmethod
    def getMsgForOp(source_id: int, op: Op, type: messages.MsgType = messages.MsgType.Request, dest=-1):
        '''
            returns an object of type Message or operations sent
            to the node.

            NOTE operations are different from messages exchanged between nodes.
            primary usage of operations is to manually "instruct" a node to commit
            an action using an external client from the main thread.
        '''
        if op == Op.TriggerAllocate:
            return messages.AllocateReq(source_id)
        elif op == Op.SendHeartbeat:
            if type == messages.MsgType.Request:
                return messages.HeartbeatReq(source_id)
            else:
                return messages.HeartbeatResp(source_id, dest)
        elif op == Op.SendUpdateDep:
            return messages.UpdateReq(source_id, items.ItemDependency.newNullDependency())
        elif op == Op.Kill:
            return messages.UpdateReq(source_id, items.ItemDependency.newNullDependency())
        elif op == Op.Recover:
            return messages.UpdateReq(source_id, items.ItemDependency.newNullDependency())
        else:
            assert False, "looked up message for invalid operation {} in operation handler".format(op)


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
        super(OpsRunnerThread, self).__init__()

        self.node_process = node_process
        self.delay = delay

        self.node_id = node_process.node_id

    def get_message_from_op(self, op):
        log.debug('Node %s constructing message for operation %s', self.node_id, op)
        return OpHandler.getMsgForOp(self.node_id, op)

    def is_node_part_of_flow(self, node_id):
        leader = self.node_process.state_helper.get_leader()
        flow = self.node_process.state_helper.get_flow()
        if leader == self.node_id:
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
        log.info('Node %s running operation thread with operations %s', self.node_id, self.node_process.op_queue)

        # Add an initial delay in order for the cluster to be setup (raftos and other dependencies)
        sleep(self.delay)

        while True:
            op = self.node_process.op_queue.get()
            if op == Op.Kill:
                # node is being asked to crash
                self.node_process.on_kill()
            elif op == Op.Recover:
                # node is being asked to wake-up from a crash
                self.node_process.on_recover()
            else:
                # node is being requested to run
                if not self.node_process.is_active:
                    msg = self.get_message_from_op(op)
                    log.debug('Node %s responding to operation %s with %s', self.node_id, op, msg)
                    self.node_process.sendMessage(msg)
                else:
                    log.error("Node %d is inactive and cannot respond to operation %s", self.node_id, op)

            sleep(self.delay)
