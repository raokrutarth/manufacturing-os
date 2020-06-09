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
dead_node_id_list = manager.list()


def get_random_node_to_kill_id(state_helper, leader_can_fail):
    flow = state_helper.get_flow()
    nodes = state_helper.get_cluster().nodes
    active_node_ids = [node.node_id for node in nodes if node.state == NodeState.active]

    if not leader_can_fail:
        for node_id in active_node_ids:
            if state_helper.get_leader() == node_id:
                active_node_ids.remove(node_id)

    start_node_id = nodes[0].node_id
    end_node_id = nodes[-1].node_id
    if start_node_id in active_node_ids:
        active_node_ids.remove(start_node_id)
    if end_node_id in active_node_ids:
        active_node_ids.remove(end_node_id)

    active_node_ids = [nid for nid in active_node_ids if flow.is_node_part_of_flow(nid)]

    if len(active_node_ids) == 0:
        return None
    else:
        kill_node_id = random.choice(active_node_ids)
        return kill_node_id


def get_random_node_id_to_recover():
    if len(dead_node_id_list) == 0:
        return None

    recovered_node_id = dead_node_id_list.pop(0)
    return recovered_node_id


def kill_node(state_helper, queues, failure_prob_per_sec, leader_can_fail):
    if random.random() < failure_prob_per_sec:
        node_to_kill_id = get_random_node_to_kill_id(state_helper, leader_can_fail)
        if node_to_kill_id is not None:
            if node_to_kill_id not in dead_node_id_list:
                queues[node_to_kill_id].put(Op.Kill)
                log.critical("Node %d to be killed", node_to_kill_id)
                dead_node_id_list.append(node_to_kill_id)
            else:
                return None


def recover_node(queues, recover_prob_per_sec):
    if random.random() < recover_prob_per_sec:
        node_to_recover_id = get_random_node_id_to_recover()
        if node_to_recover_id is not None:
            queues[node_to_recover_id].put(Op.Recover)
            log.critical("Node %d to be recovered", node_to_recover_id)


def send_update_dep(state_helper, queues, update_dep_prob_per_sec):
    if random.random() < update_dep_prob_per_sec:
        nodes = state_helper.get_cluster().nodes
        active_nodes = [node for node in nodes if node.state == NodeState.active]
        if len(active_nodes) == 0:
            return None
        else:
            node = random.choice(active_nodes)
            queues[node.node_id].put(Op.SendUpdateDep)
            log.warning("Node %d to update dependency", node.node_id)


def run_generator(queues, failure_rate=0, recover_rate=0, update_dep_rate=0, leader_can_fail=False):
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

    failure_prob_per_sec = min(1.0, failure_rate / 60.0)
    update_dep_prob_per_sec = min(1.0, update_dep_rate / 60.0)
    recover_prob_per_step = min(1.0, recover_rate / 60.0) * recover_step

    # Delay before starting ops
    sleep(2.0)

    state_helper = state.StateReader()

    schedule.every(recover_step).seconds.do(recover_node, queues, recover_prob_per_step)
    schedule.every(1).seconds.do(send_update_dep, state_helper, queues, update_dep_prob_per_sec)
    schedule.every(1).seconds.do(kill_node, state_helper, queues, failure_prob_per_sec, leader_can_fail)

    while True:
        schedule.run_pending()
        time.sleep(1)
