import enum
from threading import Thread, Event, Timer
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


def get_random_node_to_kill(cluster):
    nodes = cluster.nodes
    active_nodes = [node for node in nodes if node.state == NodeState.active]
    if len(active_nodes) == 0:
        return None
    else:
        return random.choice(active_nodes)


def get_random_node_to_recover(cluster):
    nodes = cluster.nodes
    inactive_nodes = [node for node in nodes if node.state == NodeState.inactive]
    if len(inactive_nodes) == 0:
        return None
    else:
        return random.choice(inactive_nodes)


def kill_node(cluster, queues):
    node_to_kill = get_random_node_to_kill(cluster)
    if node_to_kill is not None:
        queues[node_to_kill.node_id].put(Op.Kill)


def recover_node(cluster, queues):
    node_to_recover = get_random_node_to_recover(cluster)
    if node_to_recover is not None:
        queues[node_to_recover.node_id].put(Op.Recover)


def generator(queues, cluster, failure_rate=3, recover_rate=3):
    '''
    :param queues:
    :param cluster:
    :param failure_rate: how many nodes to kill every minutes
    :param recover_rate: how many nodes to cover every minutes
    :return:
    '''
    SU, BD, RC = operations.Op.SendUpdateDep, operations.Op.Kill, operations.Op.Recover
    failure_interval = int(round(60/failure_rate))
    half_failure_interval = int(round(60/failure_rate/2))
    recover_interval = int(round(60/recover_rate))

    Timer(failure_interval, kill_node, args=[cluster, queues])
    sleep(half_failure_interval)
    Timer(recover_interval, recover_node, args=[cluster, queues])


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
            continue
            op = self.getRandomOperation()
            if op != None:
                self.queue.put(op)
            sleep(self.delay)

