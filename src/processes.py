import logging
import messages
import threads
import time
import cluster as ctr
import multiprocessing as mp
import ops_runner
from os.path import abspath

from multiprocessing import Queue
from nodes import BaseNode, NodeState
from cluster import Cluster
from state import FileBasedStateHelper
from sc_stage import SuppyChainStage
from metrics import Metrics
from file_dict import FileDict
from typing import Dict

log = logging.getLogger()


class FileDictBasedNodeProcess(object):
    """
    Base class for NodeProcess.
    All implementations: whether socket based or dummy classes extend from this
    """

    def __init__(self, node, cluster):
        self.node_id = node.node_id

        self.state_helper = FileBasedStateHelper(self.node_id)

        # Persist the initial version of cluster
        self.set_cluster(cluster)

        # use a thread-safe queue as message queue to
        # transfer messages from inter-node threads to the node's publisher
        self.message_queue = Queue()

    def node(self):
        cluster = self.cluster()
        return cluster.nodes[self.node_id]

    def set_cluster(self, cluster):
        self.state_helper.set_cluster(cluster)

    def cluster(self):
        return self.state_helper.get_cluster()


class SocketBasedNodeProcess(FileDictBasedNodeProcess):

    def __init__(self, node: BaseNode, cluster: Cluster, queue: mp.Queue, comm_queues: Dict[int, mp.Queue]):
        """
            Takes node info as input
            cluster provides the state of the whole cluster, process_specs for other nodes
        """
        super(SocketBasedNodeProcess, self).__init__(node, cluster)

        # Represents whether the node is simulating a crash
        self.is_active = True

        # Execution constants for the process
        self.heartbeat_delay = 3.0
        self.num_unresponded_heartbeats_for_death = 5

        self.process_spec = cluster.get_node_process_spec(self.node_id)
        self.port = self.process_spec.port
        self.op_queue = queue
        self.metrics = Metrics(self.node_id)
        self.comm_queues = comm_queues
        self.node_ids = [n.node_id for n in cluster.nodes]

        self.sc_stage = SuppyChainStage(self)
        self.msg_handler = messages.MessageHandler(self)
        self.subscriber = threads.SubscribeThread(self)
        self.publisher = threads.PublishThread(self)
        self.op_runner = ops_runner.OpsRunnerThread(self)

        # Manage heartbeats and liveness between nodes
        self.metrics.set_metric(self.node_id, "nodes_determined_crashed", 0)
        self.last_known_heartbeat_log = FileDict(abspath("./tmp/node_" + str(self.node_id) + ".last_known_heartbeat.log"))
        self.heartbeat = threads.HeartbeatThread(self, delay=self.heartbeat_delay)
        self.init_liveness_state()

    def startThread(self, thread, suffix):
        thread.name = suffix + '-' + str(self.node_id)
        thread.daemon = True
        thread.start()

    def perform_leader_election(self):
        # Apply for leadership
        self.state_helper.apply_for_leadership()
        # Wait for confirmation of new leader

    def init_cluster_flow(self):
        new_flow = ctr.bootstrap_flow(self.cluster().nodes, self.metrics, self.node_id)
        self.state_helper.update_flow(new_flow)

    def get_leader(self):
        return self.state_helper.get_leader()

    def start(self):
        log.info("Starting node %s", self.node_id)

        # Apply for leadership
        self.state_helper.apply_for_leadership()

        self.startThread(self.subscriber, 'subscriber')
        self.startThread(self.publisher, 'publisher')
        self.startThread(self.heartbeat, 'heartbeat')
        self.startThread(self.sc_stage, 'sc-stage')
        self.startThread(self.op_runner, 'ops-runner')

        # Wait for leader to be elected
        while not self.get_leader():
            time.sleep(0.1)

        # Initialize the flow if this node is the leader
        if self.state_helper.am_i_leader():
            self.init_cluster_flow()

        log.warning("Successfully started node %s", self.node_id)

    def sendMessage(self, message):
        if not self.is_active:
            # no threads of the node should be sending messages
            # if the node is inactive.
            log.warning("Race conditions hit: Skipping sending of message.")
            return
        self.msg_handler.sendMessage(message)

    def onMessage(self, message):
        if not self.is_active:
            # if the node is inactive (i.e. a simulated crash state) then
            # it should not reply to any messages
            log.warning("Node {} got message {} but node is marked inactive so ignoring message".format(self.node_id, message))
            return
        self.msg_handler.onMessage(message)

    """
    Functions for heartbeats, maintaining and changing the states, etc
    """

    def init_liveness_state(self):
        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {
            node.node_id: time.time() for node in self.cluster().nodes if node.node_id != self.node_id
        }

        for node in self.cluster().nodes:
            if node.node_id != self.node_id:
                self.last_known_heartbeat_log[node.node_id] = self.last_known_heartbeat[node.node_id]

    def update_heartbeat(self, node_id: int):
        # NOTE: This is a VERY strong assumption; we usually don't have
        # precise synced distributed clocks
        assert type(node_id) == int
        curr_time = time.time()
        log.debug("Node {} received a heartbeat response at {} from {}"
                  .format(self.node_id, curr_time, node_id))
        self.last_known_heartbeat[node_id] = curr_time
        # Removing as it takes a lot of time
        self.last_known_heartbeat_log[node_id] = self.last_known_heartbeat[node_id]

    def reinit_last_timestamp(self, node_id: int):
        assert type(node_id) == int
        curr_time = time.time()
        self.last_known_heartbeat[node_id] = curr_time
        # Removing as it takes a lot of time
        # self.last_known_heartbeat_log[node_id] = self.last_known_heartbeat[node_id]

    def detect_and_fetch_dead_nodes(self):
        """
        Goes over the last_known_heartbeat dict and finds which nodes are probably dead
        """
        curr_time = time.time()
        margin = self.num_unresponded_heartbeats_for_death * self.heartbeat_delay

        return [
            (nid, lt) for nid, lt in self.last_known_heartbeat.items() if (lt < (curr_time - margin)) and (lt >= 0)
        ]

    def on_kill(self):
        log.warning("Crashing node %s", self.node_id)
        self.is_active = False
        self.stop()

    def on_recover(self):
        log.warning("Restarting node %s", self.node_id)
        self.is_active = True
        self._attempt_log_recovery()

        self.subscriber.recover()
        self.publisher.recover()
        self.heartbeat.recover()

        self.sc_stage.restart()

    def update_node_deps(self, node_id, new_deps):
        cluster: ctr.Cluster = self.cluster()
        cluster.update_deps(node_id, new_deps)
        self.set_cluster(cluster)

    def update_death_of_node(self, dead_node_id: int):
        cluster: ctr.Cluster = self.cluster()
        cluster.nodes[dead_node_id].state = NodeState.inactive
        self.set_cluster(cluster)

    def update_flow(self):
        new_flow = ctr.bootstrap_flow_with_active_nodes(self.cluster().nodes, self.metrics, self.node_id)
        self.state_helper.update_flow(new_flow)

    def stop(self):
        # flush in-memory state
        self.last_known_heartbeat = {}
        self.subscriber.stop()
        self.publisher.stop()
        self.heartbeat.stop()
        self.sc_stage.stop()

    def _attempt_log_recovery(self):
        log.debug("Node %d starting heartbeat WAL recovery", self.node_id)

        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {
            node.node_id: time.time() for node in self.cluster().nodes if node.node_id != self.node_id}

        if not len(self.last_known_heartbeat):
            log.info("Node %d's Heartbeat status WALs are empty. Recount neighbor's heartbeat", self.node_id)
            return

        for node in self.cluster().nodes:
            node_id = node.node_id
            if node_id != self.node_id:
                try:
                    self.last_known_heartbeat[node_id] = self.last_known_heartbeat_log[node_id]
                except Exception:
                    log.warning(
                        "Node %d unable to recover heartbeat details from WAL for node %s", self.node_id, node_id)

        log.debug("Node %d completed heartbeat WAL recovery", self.node_id)
