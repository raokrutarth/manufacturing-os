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

