import enum
from threading import Thread, Event, Timer
import logging
import random
import messages
import copy

from operations import Operations as Op

from threading import Thread
from time import sleep
from typing import List
from nodes import SingleItemNode, NodeState
import schedule
import time

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
        log.info("Node %d to be killed", node_to_kill.node_id)


def recover_node(cluster, queues):
    node_to_recover = get_random_node_to_recover(cluster)
    if node_to_recover is not None:
        queues[node_to_recover.node_id].put(Op.Recover)
        log.info("Node %d to be recovered", node_to_recover.node_id)


def generator(queues, cluster, failure_rate=3, recover_rate=3):
    '''
    :param queues:
    :param cluster:
    :param failure_rate: how many nodes to kill every minutes
    :param recover_rate: how many nodes to cover every minutes
    :return:
    '''
    failure_interval = max(1, int(round(60 / failure_rate)))
    half_failure_interval = max(1, int(round(60 / failure_rate / 2)))
    recover_interval = max(1, int(round(60 / recover_rate)))

    schedule.every(failure_interval).seconds.do(kill_node, cluster, queues)
    sleep(half_failure_interval)
    schedule.every(recover_interval).seconds.do(recover_node, cluster, queues)

    while True:
        schedule.run_pending()
        time.sleep(1)

