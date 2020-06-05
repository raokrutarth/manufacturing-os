import enum
from threading import Thread, Event
import logging
import random
import messages
import copy

from op import Op

from threading import Thread
from time import sleep
from typing import List
from nodes import SingleItemNode, NodeState
import operations

log = logging.getLogger()

class OpsGenerator(Thread):
    def __init__(self, node_process, cluster, queue, delay=1, failure_rate=0.2, recover_rate=0.2):
        '''
            Random Operation Generator
        '''
        super(OpsGenerator, self).__init__()
        self.name = "ops-generator-{}".format(node_process.node.get_id())
        self.node_process = node_process
        self.node = node_process.node
        self.cluster = cluster
        self.queue = queue
        self.delay = delay
        self.state_helper = node_process.state_helper
        self.failure_rate = failure_rate
        self.recover_rate = recover_rate
        self.running = Event()
        self.running.set()  # set the stage to run by default

    def getRandomOperation(self):
        if self.node.state == NodeState.active and random.random() < self.failure_rate:
            return Op.Kill
        elif self.node.state == NodeState.inactive and random.random() < self.recover_rate:
            return Op.Recover

        return None

    def is_node_part_of_flow(self, node_id):
        # Only kills a node if they are part of the supply chain
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
        while self.running.is_set():
            op = self.getRandomOperation()
            if op != None:
                self.queue.put(op)
            sleep(self.delay)

