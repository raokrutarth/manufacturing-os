import asyncio
import logging
import messages
import threads
import time
import raftos
import operations

from queue import Queue
from nodes import BaseNode
from cluster import Cluster
from raft import RaftHelper
from sc_stage import SuppyChainStage


log = logging.getLogger()


class NodeProcess(object):
    """
    Base class for NodeProcess.
    All implementations: whether socket based or dummy classes extend from this
    """

    def __init__(self, node, cluster):
        self.node = node
        self.node_id = node.node_id
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

    def __init__(self, node: BaseNode, cluster: Cluster, loop, flags):
        """
            Takes node info as input
            cluster provides the state of the whole cluster, process_specs for other nodes
        """
        super(SocketBasedNodeProcess, self).__init__(node, cluster)

        # Execution constants for the process
        self.heartbeat_delay = 10.0
        self.num_unresponded_hearbeats_for_death = 5

        self.process_spec = self.cluster.process_specs[self.node.node_id]
        self.port = self.process_spec.port
        self.flags = flags
        self.loop = loop

        self.msg_handler = messages.MessageHandler(self)
        self.subscriber = threads.SubscribeThread(self, self.cluster)
        self.publisher = threads.PublishThread(self)
        self.raft_helper = RaftHelper(self, self.cluster, self.loop)
        self.sc_stage = SuppyChainStage(
            self.node.get_name(),
            self.node.get_dependency(),
        )

        # Manage heartbeats and liveness between nodes
        self.heartbeat = threads.HeartbeatThread(self, delay=self.heartbeat_delay)
        self.init_liveness_state()

        if self.flags['runOps']:
            # run the ops runner, a testing utility. See doc for OpsRunnerThread class
            self.testOpRunner = operations.OpsRunnerThread(
                self, self.cluster.blueprint.node_specific_ops[self.node.node_id]
            )

    def startThread(self, thread, suffix):
        thread.name = suffix + '-' + str(self.node.node_id)
        thread.daemon = True
        thread.start()

    async def start(self):
        log.warning("Starting node %s", self.node.get_name())

        await self.raft_helper.register_node()

        # self.startThread(self.subscriber, 'subscriber')
        # self.startThread(self.publisher, 'publisher')
        # self.startThread(self.heartbeat, 'heartbeat')
        # self.startThread(self.sc_stage, 'supplyChain')
        # if self.flags['runOps']:
        #     self.startThread(self.testOpRunner, 'heartbeat')

        log.warning("Successfully started node %s", self.node.get_name())

    async def bootstrap(self):
        log.warning("Bootstrapping node %s", self.node.get_name())
        await self.raft_helper.init_flow()
        log.warning("Successfully bootstrapped node %s", self.node.get_name())

    def sendMessage(self, message: 'Message'):
        self.msg_handler.sendMessage(message)

    def onMessage(self, message: 'Message'):
        self.msg_handler.onMessage(message, loop=self.loop)

    """
    Functions for heartbeats, maintaining and changing the states, etc
    """

    def init_liveness_state(self):
        # -1 means no last known connection timestamp
        self.last_known_heartbeat = {node: -1 for node in self.cluster.nodes if node != self.node}

    def update_heartbeat(self, node):
        # NOTE: This is a VERY strong assumption; we usually don't have precise synced distributed clocks
        curr_time = time.time()
        self.last_known_heartbeat[node] = curr_time

    def detect_and_fetch_dead_nodes(self):
        """
        Goes over the last_known_heartbeat dict and finds which nodes are probably dead
        """
        curr_time = time.time()
        margin = self.num_unresponded_hearbeats_for_death * self.heartbeat_delay
        return [n for n, lt in self.last_known_heartbeat.items() if (lt < (curr_time - margin)) and (lt >= 0)]


async def node_process_routine(node_process: SocketBasedNodeProcess):
    await node_process.start()
    log.debug("Node %d started", node_process.node_id)

    await node_process.bootstrap()
    log.debug("Node %d bootstrapped", node_process.node_id)


def run_node_process(node: BaseNode, cluster: Cluster, flags):
    loop = asyncio.new_event_loop()

    node_process = SocketBasedNodeProcess(node, cluster, loop, flags)

    log.debug("Starting loop to init node %d", node_process.node_id)
    loop.run_until_complete(node_process_routine(node_process))
    log.debug("Finished loop to init node %d", node_process.node_id)

    # Run for 600 seconds
    for _ in range(10):
        time.sleep(60)

    log.info("Node %s : exited" % node)
