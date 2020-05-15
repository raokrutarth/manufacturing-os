import logging
import messages
import threads

import operations

from queue import Queue
from nodes import BaseNode
from cluster import Cluster
from raft import RaftHelper
from collections import defaultdict


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

    def __init__(self, node: BaseNode, cluster: Cluster, flags=defaultdict(lambda: False)):
        """
            Takes node info as input
            cluster provides the state of the whole cluster, process_specs for other nodes
        """
        super(SocketBasedNodeProcess, self).__init__(node, cluster)

        self.process_spec = self.cluster.process_specs[self.node.node_id]
        self.port = self.process_spec.port
        self.flags = flags

        self.msg_handler = messages.MessageHandler(self)
        self.subscriber = threads.SubscribeThread(self, self.cluster, self.onMessage)
        self.publisher = threads.PublishThread(self)
        self.heartbeat = threads.HeartbeatThread(self)
        self.raft_helper = RaftHelper(self, self.cluster)

        if self.flags['runOps']:
            # run the ops runner, a testing utility. See doc for OpsRunnerThread class
            self.testOpRunner = operations.OpsRunnerThread(
                self, self.cluster.blueprint.node_specific_ops[self.node.node_id]
            )

    def startThread(self, thread):
        thread.daemon = True
        thread.start()

    async def start(self):
        log.debug("Starting node %s", self.node.get_name())

        await self.raft_helper.register_node()

        self.startThread(self.subscriber)
        self.startThread(self.publisher)
        self.startThread(self.heartbeat)
        if self.flags['runOps']:
            self.startThread(self.testOpRunner)

        log.info("Successfully started node %s", self.node.get_name())

    async def bootstrap(self):
        log.debug("Bootstrapping node %s", self.node.get_name())
        await self.raft_helper.init_flow()
        log.info("Successfully bootstrapped node %s", self.node.get_name())

    def sendMessage(self, message: 'Message'):
        self.msg_handler.sendMessage(message)

    def onMessage(self, message: 'Message'):
        self.msg_handler.onMessage(message)
