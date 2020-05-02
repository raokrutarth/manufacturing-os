import zmq
import nodes
import testUtils

from collections import defaultdict
from time import sleep
from threading import Thread
from multiprocessing import Process
from nodes import Cluster, BaseNode


class NodeProcess(object):
    """
    Base class for NodeProcess.
    All implementations: whether socket based or dummy classes extend from this
    """

    def __init__(self, node, cluster):
        self.node = node
        self.cluster = cluster
        self.messageQueue = []

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

        self.DELAY = 0.1

        # For testing, dummy runs
        self.ops_to_run = self.cluster.blueprint.node_specific_ops[self.node.node_id]

        # Inspired from https://github.com/streed/simpleRaft
        class SubscribeThread(Thread):
            def run(thread):
                print('Subscribe thread: {}'.format(self.node))

                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                for p_spec in self.cluster.process_specs:
                    socket.connect("tcp://%s:%d" % (p_spec.name, p_spec.port))

                while True:
                    message = socket.recv()
                    self.onMessage(message)

        class PublishThread(Thread):
            def run(thread):
                print('Publish thread: {}'.format(self.node))

                context = zmq.Context()
                socket = context.socket(zmq.PUB)
                socket.bind("tcp://*:%d" % self.port)

                while True:
                    if len(self.messageQueue):
                        message = self.messageQueue.pop(0)
                        if not message:
                            sleep(self.DELAY)
                        else:
                            socket.send(message)

        class OpsRunnerThread(Thread):
            @staticmethod
            def getMsgForOp(op):
                print('Constructing messsage for {} on {}'.format(op, self.node))
                return testUtils.OpHandler.getMsgForOp(self.node, op)

            def run(thread):
                print('Op runner thread: {}'.format(self.node))
                OPS_DELAY = 1.0
                print('Ops:', self.ops_to_run)
                for op in self.ops_to_run:
                    msg = thread.getMsgForOp(op)
                    self.sendMessage(msg)
                    sleep(OPS_DELAY)

        self.subscriber = SubscribeThread()
        self.publisher = PublishThread()

        if self.flags['runOps']:
            self.opRunner = OpsRunnerThread()

        self.start()

    def startThread(self, thread):
        thread.daemon = True
        thread.start()

    def start(self):
        print("Starting process..", self.node)
        self.startThread(self.subscriber)
        self.startThread(self.publisher)
        if self.flags['runOps']:
            self.startThread(self.opRunner)
        print("Finished starting process..", self.node)

    def sendMessage(self, message):
        self.messageQueue.append(message)

    def onMessage(self, message):
        print("Recv: {} from {}".format(message, message.source))


import unittest
import basecases


class BootstrapCluster(unittest.TestCase):

    def setUp(self):
        self.blueprint = basecases.dummyBlueprintCase0()
        self.cluster = nodes.Cluster(self.blueprint)
        self.TIMEOUT = 3.0

    def spawn_cluster_process(self, runOps):
        flags = {'runOps': runOps}
        for node in self.cluster.nodes:
            Process(target=SocketBasedNodeProcess, args=(node, self.cluster, flags)).start()


class TestBootstrapCluster(BootstrapCluster):

    def test_bootstrap_cluster(self):
        print(self.cluster)
        self.spawn_cluster_process(runOps=False)
        sleep(self.TIMEOUT)

    def test_bootstrap_cluster_with_ops(self):
        self.blueprint = basecases.dummyBlueprintCase1()
        self.cluster = nodes.Cluster(self.blueprint)
        print(self.cluster)
        self.spawn_cluster_process(runOps=True)
        sleep(self.TIMEOUT)

if __name__ == '__main__':
    unittest.main()