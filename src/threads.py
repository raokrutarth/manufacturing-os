import zmq
import logging
import pickle
import messages

from time import sleep
from threading import Thread
from queue import Queue


log = logging.getLogger()


class SubscribeThread(Thread):
    def __init__(self, node_process: 'SocketBasedNodeProcess', cluster: 'Cluster', callback: 'onMessage'):
        super(SubscribeThread, self).__init__()

        self.node_process = node_process
        self.cluster = cluster
        self.callback = callback
        self.node_id = node_process.node.get_name()
        self.DELAY = 0.01

    def run(self):
        log.debug('node %s starting subscriber thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # set the subscriber socket to listen to all messages
        # by any publisher. (can be optimized later)
        socket.setsockopt(zmq.SUBSCRIBE, b'')

        other_node_ports = \
            [spec.port for spec in self.cluster.process_specs.values() if spec.port != self.node_process.port]
        log.debug("subscriber in node %d connecting to sockets %s", self.node_id, other_node_ports)

        for port in other_node_ports:
            # NOTE:
            # - connect() can be called on multiple ports in zmq.
            # - a subscriber shouldn't connect to itself
            socket.connect("tcp://127.0.0.1:%d" % port)

        while True:
            message = socket.recv()
            message = pickle.loads(message)
            log.debug("subscriber in node %s got message %s", self.node_id, message)
            self.callback(message)

            # Polling based approach to receive messages. Can convert to blocking call if needed
            sleep(self.DELAY)


class PublishThread(Thread):

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay=0.1):
        super(PublishThread, self).__init__()

        self.node_process = node_process
        self.delay = delay
        self.node_id = node_process.node.get_name()

    def run(self):
        log.debug('node %s starting publisher thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://127.0.0.1:%d" % self.node_process.port)

        while True:
            if not self.node_process.message_queue.empty():
                message = self.node_process.message_queue.get()
                log.debug("publisher in node %s sending message %s", self.node_id, message)
                socket.send(pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL))
            else:
                sleep(self.delay)


class HeartbeatThread(Thread):

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay=5.0):
        super(HeartbeatThread, self).__init__()

        self.node_process = node_process
        self.delay = delay
        self.node = node_process.node
        self.node_id = node_process.node.get_name()

    def send_message_for_dead_nodes(self):
        dead_nodes = self.node_process.detect_and_fetch_dead_nodes()
        for node in dead_nodes:
            # Send message to leader to notify of death
            log.debug('Detected death of node %s by %s', node, self.node_id)

    def run(self):
        log.debug('node %s starting heartbeat thread', self.node_id)

        while True:
            # TODO: Currently this is a broadcast, change it to P2P communication
            message = messages.MessageHandler.getMsgForAction(
                source=self.node.node_id, action=messages.Action.Heartbeat, type=messages.MsgType.Request
            )
            log.debug("node %s sending heartbeat %s", self.node_id, message)
            self.node_process.sendMessage(message)
            self.send_message_for_dead_nodes()
            sleep(self.delay)
