import zmq
import nodes

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

    def __init__(self, node: BaseNode, cluster: Cluster):
        """
        Takes node info as input
        cluster provides the state of the whole cluster, process_specs for other nodes
        """
        super(SocketBasedNodeProcess, self).__init__(node, cluster)

        self.cluster = cluster
        self.process_spec = self.cluster.process_specs[node.node_id]
        self.port = self.process_spec.port

        self.DELAY = 0.1

        # Inspired from https://github.com/streed/simpleRaft
        class SubscribeThread(Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.SUB)
                for p_spec in self.cluster.process_specs:
                    socket.connect("tcp://%s:%d" % (p_spec.name, p_spec.port))

                while True:
                    message = socket.recv()
                    self.onMessage(message)

        # TODO: Need to allow talking to multiple clients
        class PublishThread(Thread):
            def run(thread):
                context = zmq.Context()
                socket = context.socket(zmq.PUB)
                socket.bind("tcp://*:%d" % self.port)

                while True:
                    message = self.messageQueue.pop()
                    if not message:
                        sleep(self.DELAY)
                    else:
                        socket.send(message)

        self.subscriber = SubscribeThread()
        self.publisher = PublishThread()

        self.start()

    def start(self):
        print("Starting process..", self.node)
        self.subscriber.daemon = True
        self.subscriber.start()
        self.publisher.daemon = True
        self.publisher.start()
        print("Finished starting process..", self.node)

    def sendMessage(self, message):
        self.messageQueue.append(message)

    def onMessage(self, message):
        print("Recv:", message)


import unittest
import basecases


class BootstrapCluster(unittest.TestCase):

    def setUp(self):
        self.blueprint = basecases.dummyBlueprintCase0()
        self.cluster = nodes.Cluster(self.blueprint)
        self.TIMEOUT = 3.0

    def spawn_cluster_process(self):
        for node in self.cluster.nodes:
            Process(target=SocketBasedNodeProcess, args=(node, self.cluster)).start()


class TestBootstrapCluster(BootstrapCluster):

    def test_bootstrap_cluster(self):
        print(self.cluster)
        self.spawn_cluster_process()
        sleep(self.TIMEOUT)


if __name__ == '__main__':
    unittest.main()