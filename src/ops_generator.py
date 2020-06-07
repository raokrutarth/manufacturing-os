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

    recover_node = dead_node_list.pop(0)
    return recover_node


def kill_node(cluster, queues):
    node_to_kill = get_random_node_to_kill(cluster)
    if node_to_kill is not None:
        queues[node_to_kill.node_id].put(Op.Kill)
        log.warning("Node %d to be killed", node_to_kill.node_id)


def recover_node(cluster, queues):
    node_to_recover = get_random_node_to_recover(cluster)
    if node_to_recover is not None:
        queues[node_to_recover.node_id].put(Op.Recover)
        log.warning("Node %d to be recovered", node_to_recover.node_id)


def generator(queues, cluster, failure_rate, recover_rate):
    '''
    :param queues:
    :param cluster:
    :param failure_rate: how many nodes to kill every minutes
    :param recover_rate: how many nodes to cover every minutes
    :return:
    '''
    if not failure_rate and not recover_rate:
        return

    failure_interval = max(1, int(round(60 / failure_rate)))
    half_failure_interval = max(1, int(round(60 / failure_rate / 2)))
    recover_interval = max(1, int(round(60 / recover_rate)))

    schedule.every(failure_interval).seconds.do(kill_node, cluster, queues)
    sleep(half_failure_interval)
    schedule.every(recover_interval).seconds.do(recover_node, cluster, queues)

    while True:
        schedule.run_pending()
        time.sleep(1)
