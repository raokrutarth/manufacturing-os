
import logging
from collections import defaultdict
from queue import Queue

import operations
from nodes import BaseNode
from cluster import Cluster
from raft import RaftHelper
from pub_sub import SubscribeThread, PublishThread
from messages import Action, MsgType

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

        # FIXME:
        # self.cluster.process_specs is a list, not a map, if node_id
        # becomes a non-int or too large, this crashes. I.e. node_id has to be an integer
        # in the range [0, len(cluster.process_specs))
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

    def sendMessage(self, message):
        log.debug("sending message %s from node %s", message, self.node.node_id)
        self.message_queue.put_nowait(message)

    def onMessage(self, message: 'Message'):
        # de-serialize message
        log.debug("Received: %s from %s", message, message.source)
        '''
            TODO
            add logic to take an action based on the message object that
            is expected to be one of the sub-classes of the Message class
            in messages.py
        '''
        if message.action == Action.Heartbeat and message.type == MsgType.Request:
            #TODO: update liveness status in global dictionary
            # I am waiting to discuss who will take action of overall liveness exception.
            # Is the publisher of heartbeat or the leader? If leader takes action,
            # then there are no need for message to send back to the publisher, instead we can
            # just update global dictionary of liveness status.
            log.debug("%s: I am live!!!", self.node.get_name())

        return
