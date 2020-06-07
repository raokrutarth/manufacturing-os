import logging
import random
import multiprocessing
from operations import Operations as Op
from time import sleep
from nodes import NodeState
import schedule
import time
from state import FileBasedStateHelper

log = logging.getLogger()
manager = multiprocessing.Manager()
dead_node_list = manager.list()


def get_random_node_to_kill(cluster, leader_can_fail=False):
    nodes = cluster.nodes
    active_nodes = [node for node in nodes if node.state == NodeState.active]

    if not leader_can_fail:
        for node in active_nodes:
            state_helper = FileBasedStateHelper(node, cluster)
            if state_helper.am_i_leader():
                active_nodes.remove(node)

    if len(active_nodes) == 0:
        return None
    else:
        kill_node = random.choice(active_nodes)
        dead_node_list.append(kill_node)
        return kill_node


def get_random_node_to_recover(cluster):
    num_of_dead_nodes = len(dead_node_list)
    if len(dead_node_list) == 0:
        return None

    recover_node = dead_node_list.pop(0)
    return recover_node


def kill_node(cluster, queues, failure_prob_per_sec, leader_can_fail=False):
    if random.random() < failure_prob_per_sec:
        node_to_kill = get_random_node_to_kill(cluster, leader_can_fail)
        if node_to_kill is not None:
            if node_to_kill not in dead_node_list:
                queues[node_to_kill.node_id].put(Op.Kill)
                log.critical("Node %d to be killed", node_to_kill.node_id)
            else:
                return None


def recover_node(cluster, queues, recover_prob_per_sec):
    if random.random() < recover_prob_per_sec:
        node_to_recover = get_random_node_to_recover(cluster)
        if node_to_recover is not None:
            queues[node_to_recover.node_id].put(Op.Recover)
            log.critical("Node %d to be recovered", node_to_recover.node_id)


def send_update_dep(cluster, queues, update_dep_prob_per_sec):
    if random.random() < update_dep_prob_per_sec:
        nodes = cluster.nodes
        active_nodes = [node for node in nodes if node.state == NodeState.active]
        if len(active_nodes) == 0:
            return None
        else:
            node = random.choice(active_nodes)
            queues[node.node_id].put(Op.SendUpdateDep)
            log.warning("Node %d to update dependency", node.node_id)

def run_generator(queues, cluster, failure_rate=0, recover_rate=0, update_dep_rate=0, leader_can_fail=False):
    '''
    :param queues:
    :param cluster:
    :param failure_rate: how many nodes to kill every minutes
    :param recover_rate: how many nodes to cover every minutes
    :param update_dep_rate: how many update_dep to send every minutes
    :return:
    '''

    failure_prob_per_sec = min(1.0, failure_rate / 60.0)
    recover_prob_per_sec = min(1.0, recover_rate / 60.0)
    update_dep_prob_per_sec = min(1.0, update_dep_rate / 60.0)

    schedule.every().second.do(kill_node, cluster, queues, failure_prob_per_sec, leader_can_fail)
    sleep(2)
    schedule.every().second.do(send_update_dep, cluster, queues, update_dep_prob_per_sec)
    schedule.every().second.do(recover_node, cluster, queues, recover_prob_per_sec)

    while True:
        schedule.run_pending()
        time.sleep(1)
