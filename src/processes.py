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
from collections import defaultdict
from sc_stage import SuppyChainStage
from metrics import Metrics
from file_dict import FileDict

log = logging.getLogger()


class NodeProcess(object):
    """
    Base class for NodeProcess.
    All implementations: whether socket based or dummy classes extend from this
    """

    def __init__(self, node, cluster):
        self.node = node
        self.cluster = cluster

        # use a thread-safe queue as message queue to
        # transfer messages from thread __ to the publisher thread
        self.message_queue = Queue()

    def sendMessage(self, message):
        pass

    def broadcastMessage(self, message):
        pass

    def onMessage(self, message):
        pass


class SocketBasedNodeProcess(NodeProcess):

    def __init__(self, node: BaseNode, cluster: Cluster, queue: mp.Queue, flags=defaultdict(lambda: False)):
        """
            Takes node info as input
            cluster provides the state of the whole cluster, process_specs for other nodes
        """
        super(SocketBasedNodeProcess, self).__init__(node, cluster)

        # Execution constants for the process
        self.heartbeat_delay = 1.0
        self.num_unresponded_heartbeats_for_death = 5

        self.process_spec = self.cluster.get_node_process_spec(self.node.node_id)
        self.port = self.process_spec.port
        self.flags = flags
        self.op_queue = queue
        self.metrics = Metrics(self.node.node_id)

        self.state_helper = FileBasedStateHelper(self.node, self.cluster)
        self.sc_stage = SuppyChainStage(self)
        self.msg_handler = messages.MessageHandler(self)
        self.subscriber = threads.SubscribeThread(self, self.cluster)
        self.publisher = threads.PublishThread(self)

        # Manage heartbeats and liveness between nodes
        self.last_known_heartbeat_log = FileDict(abspath("./tmp/node_" + str(self.node.node_id) + ".last_known_heartbeat.log"))
        self.heartbeat = threads.HeartbeatThread(self, delay=self.heartbeat_delay)
        self.init_liveness_state()

        if self.flags['runOps']:
            # run the ops runner, a testing utility. See doc for OpsRunnerThread class
            self.testOpRunner = ops_runner.OpsRunnerThread(self)

    def startThread(self, thread, suffix):
        thread.name = suffix + '-' + str(self.node.node_id)
        thread.daemon = True
        thread.start()

    def perform_leader_election(self):
        # Apply for leadership
        self.state_helper.apply_for_leadership()
        # Wait for confirmation of new leader

    def init_cluster_flow(self):
        new_flow = ctr.bootstrap_flow(self.cluster.nodes)
        self.state_helper.update_flow(new_flow)

    def get_leader(self):
        return self.state_helper.get_leader()

    def start(self):
        log.info("Starting node %s", self.node.get_id())

        # Apply for leadership
        self.state_helper.apply_for_leadership()

        self.startThread(self.subscriber, 'subscriber')
        self.startThread(self.publisher, 'publisher')
        self.startThread(self.heartbeat, 'heartbeat')
        self.startThread(self.sc_stage, 'production-stage')
        if self.flags['runOps']:
            self.startThread(self.testOpRunner, 'test ops runner')

        # Wait for leader to be elected
        while not self.get_leader():
            time.sleep(0.1)

        # Initialize the flow if this node is the leader
        if self.state_helper.am_i_leader():
            self.init_cluster_flow()

        log.warning("Successfully started node %s", self.node.get_id())

    def sendMessage(self, message):
        if self.node.state == NodeState.inactive:
            # no threads of the node should be sending messages
            # if the node is inactive.
            raise Exception
        self.msg_handler.sendMessage(message)

    def onMessage(self, message):
        if self.node.state == NodeState.inactive:
            # if the node is inactive (i.e. a simulated crash state) then
            # it should not reply to any messages
            log.warning("Node {} got message {} but node is marked inactive so ignoring message".format(self.node.node_id, message))
            return
        self.msg_handler.onMessage(message)

    """
    Functions for heartbeats, maintaining and changing the states, etc
    """

    def init_liveness_state(self):
        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {
            node.node_id: time.time() for node in self.cluster.nodes if node != self.node
        }

        for node in self.cluster.nodes:
            if node != self.node:
                self.last_known_heartbeat_log[node.node_id] = self.last_known_heartbeat[node.node_id]

    def update_heartbeat(self, node_id):
        # NOTE: This is a VERY strong assumption; we usually don't have
        # precise synced distributed clocks
        curr_time = time.time()
        self.last_known_heartbeat[node_id] = curr_time
        self.last_known_heartbeat_log[node_id] = self.last_known_heartbeat[node_id]

    def detect_and_fetch_dead_nodes(self):
        """
        Goes over the last_known_heartbeat dict and finds which nodes are probably dead
        """
        curr_time = time.time()
        margin = self.num_unresponded_heartbeats_for_death * self.heartbeat_delay

        for nid, lt in self.last_known_heartbeat.items():
            if (lt < (curr_time - margin)) and (lt >= 0):
                log.warning(
                    'Node: {} detected node: {} to be dead, last heartbeat: {}, current time: {}'.format(
                        self.node.node_id, nid, lt, curr_time))

        return [
            nid for nid, lt in self.last_known_heartbeat.items() if (lt < (curr_time - margin)) and (lt >= 0)
        ]

    def on_kill(self):
        log.warning("Killing node %s", self.node.get_id())
        self.node.state = NodeState.inactive
        self.stop()

    def on_recover(self):
        log.warning("Recovering node %s", self.node.get_id())
        self._attempt_log_recovery()
        self.subscriber.recover()
        self.publisher.recover()
        self.heartbeat.recover()
        self.node.state = NodeState.active
        log.warning("Recovering node %s", self.node.get_id())
        self.sc_stage.restart()

    def update_flow(self):
        new_flow = ctr.bootstrap_flow_with_active_nodes(self.cluster.nodes)
        self.state_helper.update_flow(new_flow)

    def stop(self):
        # flush in-memory state
        self.last_known_heartbeat = None
        self.subscriber.stop()
        self.publisher.stop()
        self.heartbeat.stop()
        self.sc_stage.stop()

    def _attempt_log_recovery(self):
        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {node: -1 for node in self.cluster.nodes if node != self.node}

        if not len(self.last_known_heartbeat):
            log.info("Node %d's Heartbeat status WALs are empty. Recount neighbor's heartbeat", self.node_id)
            return

        for node in self.cluster.nodes:
            if node != self.node:
                try:
                    self.last_known_heartbeat[node] = self.last_known_heartbeat_log[node]
                except:
                    log.warning("### Node %d has issues to recovery from log ", self.node.node_id)
        log.debug("Node %d succeeds in recovery heartbeat from log ", self.node.node_id)
