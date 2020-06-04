import logging
import messages
import threads
import time
import operations
import cluster as ctr
import multiprocessing as mp

from multiprocessing import Queue
from nodes import BaseNode
from cluster import Cluster
from state import FileBasedStateHelper
from collections import defaultdict
from sc_stage import SuppyChainStage


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
        self.heartbeat_delay = 10.0
        self.num_unresponded_hearbeats_for_death = 5

        self.process_spec = self.cluster.get_node_process_spec(self.node.node_id)
        self.port = self.process_spec.port
        self.flags = flags
        self.op_queue = queue
        self.metrics = self.cluster.metrics

        self.state_helper = FileBasedStateHelper(self.node, self.cluster)
        self.sc_stage = SuppyChainStage(self)
        self.msg_handler = messages.MessageHandler(self)
        self.subscriber = threads.SubscribeThread(self, self.cluster)
        self.publisher = threads.PublishThread(self)


        # Manage heartbeats and liveness between nodes
        self.heartbeat = threads.HeartbeatThread(self, delay=self.heartbeat_delay)
        self.init_liveness_state()

        if self.flags['runOps']:
            # run the ops runner, a testing utility. See doc for OpsRunnerThread class
            ops = self.cluster.get_node_ops(self.node.node_id)
            self.testOpRunner = operations.OpsRunnerThread(
                self, ops,
            )
            self.testOpRunner = operations.OpsRunnerThread(self)

    def startThread(self, thread, suffix):
        thread.name = suffix + '-' + str(self.node.node_id)
        thread.daemon = True
        thread.start()

    def perform_leader_election(self):
        # Apply for leadership
        self.state_helper.apply_for_leadership()
        # Wait for confirmation of new leader

    def init_cluster_flow(self):
        new_flow = ctr.bootstrap_shortest_path(self.cluster.nodes)
        self.state_helper.update_flow(new_flow)

    def start(self):
        log.warning("Starting node %s", self.node.get_id())

        # Apply for leadership
        self.state_helper.apply_for_leadership()

        self.startThread(self.subscriber, 'subscriber')
        self.startThread(self.publisher, 'publisher')
        self.startThread(self.heartbeat, 'heartbeat')
        self.startThread(self.sc_stage, 'production-stage')
        if self.flags['runOps']:
            self.startThread(self.testOpRunner, 'heartbeat')

        log.warning("Successfully started node %s", self.node.get_id())

    def sendMessage(self, message):
        self.metrics.increase_metric(self.node.node_id, "sent_messages")
        self.msg_handler.sendMessage(message)

    def onMessage(self, message):
        self.metrics.increase_metric(self.node.node_id, "received_messages")
        self.msg_handler.onMessage(message)

    """
    Functions for heartbeats, maintaining and changing the states, etc
    """

    def init_liveness_state(self):
        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {node: -1 for node in self.cluster.nodes if node != self.node}

    def update_heartbeat(self, node):
        # NOTE: This is a VERY strong assumption; we usually don't have
        # precise synced distributed clocks
        curr_time = time.time()
        self.last_known_heartbeat[node] = curr_time

    def detect_and_fetch_dead_nodes(self):
        """
        Goes over the last_known_heartbeat dict and finds which nodes are probably dead
        """
        curr_time = time.time()
        margin = self.num_unresponded_hearbeats_for_death * self.heartbeat_delay
        return [
            n for n, lt in self.last_known_heartbeat.items()
            if (lt < (curr_time - margin)) and (lt >= 0)
        ]

    def onKill(self):
        log.warning("Killing node %s", self.node.get_id())
        pass

    def onRecover(self):
        log.warning("Recovering node %s", self.node.get_id())
        pass
