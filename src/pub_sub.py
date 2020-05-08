import zmq
import logging
import pickle
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

    def run(self):
        log.debug('node %s starting subscriber thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # set the subscriber socket to listen to all messages
        # by any publisher. (can be optimized later)
        socket.setsockopt(zmq.SUBSCRIBE, b'')

        other_node_ports = [port for port in self.cluster.process_specs if port != self.node_process.port]
        log.debug("connecting to sockets %s in subscriber thread for node %d",
            other_node_ports, self.node_id)

        for p_spec in self.cluster.process_specs:
            # NOTE:
            # - connect() can be called on multiple ports in zmq.
            # - a subscriber shouldn't connect to itself
            if p_spec.port != self.node_process.port:
                socket.connect("tcp://127.0.0.1:%d" %  (p_spec.port))

        # FIXME
        # instead of having an infinite loop that can be inefficent,
        # use async, event based method to invoke the onMessage function.
        while True:
            message = socket.recv()
            message = pickle.loads(message)
            log.debug("subscriber in node %s got message %s", self.node_id, message)
            self.callback(message)

class PublishThread(Thread):

    def __init__(self, node_process: 'SocketBasedNodeProcess', message_queue: Queue, delay=0.1):
        super(PublishThread, self).__init__()

        self.node_process = node_process
        self.message_queue = message_queue
        self.delay = delay
        self.node_id = node_process.node.get_name()

    def run(self):
        log.debug('node %s starting publisher thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://127.0.0.1:%d" % (self.node_process.port))

        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                log.debug("publisher in node %s sending message %s",
                    self.node_id, message)

                socket.send(pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL))
            else:
                sleep(self.delay)
