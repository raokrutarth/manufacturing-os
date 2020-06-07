import enum
from threading import Thread, Event, Timer
import logging
import random
import multiprocessing
from operations import Operations as Op
from time import sleep
from nodes import NodeState
import schedule
import time

log = logging.getLogger()
manager = multiprocessing.Manager()
dead_node_list = manager.list()


def get_random_node_to_kill(cluster):
    nodes = cluster.nodes
    active_nodes = [node for node in nodes if node.state == NodeState.active]
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

    random.shuffle(dead_node_list)
    recover_node = dead_node_list.pop(0)
    return recover_node


def kill_node(cluster, queues, failure_prob_per_sec):
    if random.random() < failure_prob_per_sec:
        node_to_kill = get_random_node_to_kill(cluster)
        if node_to_kill is not None:
            if node_to_kill not in dead_node_list:
                queues[node_to_kill.node_id].put(Op.Kill)
                log.warning("Node %d to be killed", node_to_kill.node_id)
            else:
                return None


def recover_node(cluster, queues, recover_prob_per_sec):
    if random.random() < recover_prob_per_sec:
        node_to_recover = get_random_node_to_recover(cluster)
        if node_to_recover is not None:
            queues[node_to_recover.node_id].put(Op.Recover)
            log.warning("Node %d to be recovered", node_to_recover.node_id)


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

def generator(queues, cluster, failure_rate=3, recover_rate=3):
    '''
    :param queues:
    :param cluster:
    :param failure_rate: how many nodes to kill every minutes
    :param recover_rate: how many nodes to cover every minutes
    :param update_dep_rate: how many update_dep to send every minutes
    :return:
    '''
    if not failure_rate and not recover_rate:
        return

    failure_interval = max(1, int(round(60 / failure_rate)))
    recover_interval = max(1, int(round(60 / recover_rate)))
    failure_prob_per_sec = min(1.0, failure_rate / 60.0)
    recover_prob_per_sec = min(1.0, recover_rate / 60.0)
    update_dep_prob_per_sec = min(1.0, update_dep_rate / 60.0)

    schedule.every().second.do(kill_node, cluster, queues, failure_prob_per_sec)
    sleep(2)
    schedule.every().second.do(send_update_dep, cluster, queues, update_dep_prob_per_sec)
    schedule.every().second.do(recover_node, cluster, queues, recover_prob_per_sec)

    while True:
        schedule.run_pending()
        time.sleep(1)

