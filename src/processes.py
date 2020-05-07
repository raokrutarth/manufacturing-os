import zmq
import operations
import logging
from collections import defaultdict
from time import sleep
from threading import Thread
from multiprocessing import Process

from nodes import BaseNode
from cluster import Cluster
from raft import RaftHelper

log = logging.getLogger()

class NodeProcess(object):
    """
    Base class for NodeProcess.
    All implementations: whether socket based or dummy classes extend from this
    """

    def __init__(self, node, cluster):
        self.node = node
        self.cluster = cluster
        self.messageQueue = [""] # zmq cannot send "None" messages out of the box -- only strings and bytes!

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
        # self.cluster.process_specs is a list not a map, if node_id
        # becomes a non-int or too large, this crashes. I.e. node_id has to be an integer
        # in the range [0, len(cluster.process_specs))
        self.process_spec = self.cluster.process_specs[self.node.node_id]
        self.port = self.process_spec.port
        self.flags = flags

        self.DELAY = 0.1

        # For testing, dummy runs
        self.ops_to_run = self.cluster.blueprint.node_specific_ops[self.node.node_id]

        # Inspired from https://github.com/streed/simpleRaft
        class SubscribeThread(Thread):
            def run(thread):
                log.debug('%s starting subscriber thread', self.node.get_name())
                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                
                for p_spec in self.cluster.process_specs:
                    # Node shouldn't connect to itself, right?
                    if p_spec.name != "process-" + str(self.node.get_name()):
                        socket.connect("tcp://%s:%d" % (p_spec.name, p_spec.port))

                while True:
                    sleep(2)
                    message = socket.recv()
                    self.onMessage(message)

        class PublishThread(Thread):
            def run(thread):
                log.debug('%s starting publisher thread', self.node.get_name())

                context = zmq.Context()
                socket = context.socket(zmq.PUB)
                socket.bind("tcp://*:%d" % self.port)

                while True:
                    if self.messageQueue:
                        message = self.messageQueue.pop(0)
                        if not message:
                            sleep(self.DELAY)
                        else:
                            socket.send(message)

        class OpsRunnerThread(Thread):
            '''
                Operation runner allows the node instinatiator to declare
                the operations the node should take without having any influence
                from any other node.

                E.g. during a test, we want a specific node to run reallocate.

                NOTE:
                    Not to be used during actual demo unless an operation needs to
                    be simulated.
            '''
            @staticmethod
            def getMsgForOp(op):
                log.info('%s constructing message for operation %s', self.node.get_name(), op)
                return operations.OpHandler.getMsgForOp(self.node, op)

            def run(thread):
                log.debug('%s starting operation thread with operations %s', self.node.get_name(), self.ops_to_run)
                OPS_DELAY = 1.0
                for op in self.ops_to_run:
                    msg = thread.getMsgForOp(op)
                    self.sendMessage(msg)
                    sleep(OPS_DELAY)

        self.subscriber = SubscribeThread()
        self.publisher = PublishThread()
        
        self.raft_helper = RaftHelper(self, self.cluster) # shared dictionary

        if self.flags['runOps']:
            self.opRunner = OpsRunnerThread()

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
        log.info("Started node %s", self.node.get_name())

    def sendMessage(self, message):
        self.messageQueue.append(message)

    def onMessage(self, message):
        log.debug("Received: %s from %s", message, message.source)

