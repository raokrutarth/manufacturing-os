
import logging
from collections import defaultdict
from queue import Queue

import operations
from nodes import BaseNode
from cluster import Cluster
from raft import RaftHelper
from pub_sub import SubscribeThread, PublishThread
from messages import Action, MsgType, HeartbeatResp
from operations import OpHandler

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

        self.subscriber = SubscribeThread(self, self.cluster, self.onMessage)
        self.publisher = PublishThread(self, self.message_queue)
        self.raft_helper = RaftHelper(self, self.cluster)

        if self.flags['runOps']:
            # run the ops runner, a testing utility. See doc for OpsRunnerThread class
            self.opRunner = operations.OpsRunnerThread(
                self,
                self.cluster.blueprint.node_specific_ops[self.node.node_id],
                self.sendMessage,
            )

        self.start()

    def startThread(self, thread):
        thread.daemon = True
        thread.start()

    async def start(self):
        log.debug("Starting node %s", self.node.get_name())

        await self.raft_helper.register_node()

        self.startThread(self.subscriber)
        self.startThread(self.publisher)
        if self.flags['runOps']:
            self.startThread(self.opRunner)

        log.info("Successfully started node %s", self.node.get_name())

    async def bootstrap(self):
        log.debug("Bootstrapping node %s", self.node.get_name())
        await self.raft_helper.init_flow()
        log.info("Successfully bootstrapped node %s", self.node.get_name())

    def sendMessage(self, message):
        log.debug("sending message %s from node %s", message, self.node.node_id)
        self.message_queue.put_nowait(message)

    def onMessage(self, message: 'Message'):
        log.debug("Received: %s from %s", message, message.source)
        '''
            TODO
            add logic to take an action based on the message object that
            is expected to be one of the sub-classes of the Message class
            in messages.py
        '''
        if message.action == Action.Heartbeat and message.type == MsgType.Request:
            response = OpHandler.getMsgForOp(source=self.node, op=Action.Heartbeat, type = MsgType.Response, dest = message.source)
            self.sendMessage(response)
        elif message.action == Action.Heartbeat and message.type == MsgType.Response:
            log.debug("%s : Heartbeat Resp: Roger that!", message.source)

        return
