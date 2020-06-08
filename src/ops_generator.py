import logging
import random
import multiprocessing
from operations import Operations as Op
from time import sleep
from nodes import NodeState
import schedule
import time
import state


log = logging.getLogger()
manager = multiprocessing.Manager()
dead_node_list = manager.list()


def get_random_node_to_kill(cluster, leader_can_fail=False):
    nodes = cluster.nodes
    active_nodes = [node for node in nodes if node.state == NodeState.active]

    if not leader_can_fail:
        for node in active_nodes:
            # TODO (Chen): We CANNOT initialize one state helper per call
            # We do not need state_helper for this
            state_helper = state.FileBasedStateHelper(node)
            if state_helper.am_i_leader():
                active_nodes.remove(node)

    if len(active_nodes) == 0:
        return None
    else:
        kill_node = random.choice(active_nodes)
        dead_node_list.append(kill_node)
        return kill_node


def get_random_node_to_recover(cluster):
    if len(dead_node_list) == 0:
        return None

    recovered_node = dead_node_list.pop(0)
    return recovered_node


def kill_node(cluster, queues, failure_prob_per_sec, leader_can_fail=False):
    if random.random() < failure_prob_per_sec:
        node_to_kill = get_random_node_to_kill(cluster, leader_can_fail)
        if node_to_kill is not None:
            if node_to_kill not in dead_node_list:
                metrics.increase_metric(node_to_kill.node_id, "num_crash_signals_recv")
                # queues[node_to_kill.node_id].put(Op.Kill)

                pub_pipe, _ = queues[node_to_kill.node_id]
                pub_pipe.send(Op.Kill)

                log.critical("Node %d to be killed", node_to_kill.node_id)
            else:
                return None


def recover_node(cluster, queues, recover_prob_per_sec):
    if random.random() < recover_prob_per_sec:
        node_to_recover = get_random_node_to_recover(cluster)
        if node_to_recover is not None:

            pub_pipe, _ = queues[node_to_recover.node_id]
            pub_pipe.send(Op.Recover)

            log.critical("Node %d to be recovered", node_to_recover.node_id)


def send_update_dep(cluster, queues, update_dep_prob_per_sec):
    if random.random() < update_dep_prob_per_sec:
        nodes = cluster.nodes
        active_nodes = [node for node in nodes if node.state == NodeState.active]
        if len(active_nodes) == 0:
            return None
        else:
            node = random.choice(active_nodes)
            pub_pipe, _ = queues[node.node_id]
            pub_pipe.send(Op.SendUpdateDep)
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

    if recover_rate < failure_rate:
        log.critical("CRITICAL: Cluster may eventually die! Check this is what you want..")

    # Turn off schedules massive logging
    logging.getLogger('schedule').propagate = False

    # Recovery happens every K seconds instead of 1 second, we want nodes to stay killed for a while
    recover_step = 4

    # TODO (Chen): Use the state reader initialized here to get cluster object
    reader = state.StateReader()

    failure_prob_per_sec = min(1.0, failure_rate / 60.0)
    update_dep_prob_per_sec = min(1.0, update_dep_rate / 60.0)
    recover_prob_per_step = min(1.0, recover_rate / 60.0) * recover_step

    schedule.every(recover_step).seconds.do(recover_node, cluster, queues, recover_prob_per_step)
    schedule.every(1).seconds.do(send_update_dep, cluster, queues, update_dep_prob_per_sec)
    schedule.every(1).seconds.do(kill_node, cluster, queues, failure_prob_per_sec, leader_can_fail)

    while True:
        schedule.run_pending()
        time.sleep(1)
