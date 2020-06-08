import zmq
import logging
import pickle
import messages

from time import sleep
from threading import Thread
from nodes import NodeState

log = logging.getLogger()


class SubscribeThread(Thread):
    def __init__(self, node_process: 'SocketBasedNodeProcess'):
        super(SubscribeThread, self).__init__()

        self.node_process = node_process
        self.node_id = node_process..node_id
        self.DELAY = 0.01

    def recover(self):
        self._attempt_log_recovery()

    def stop(self):
        # flush in-memory state
        pass

    def _attempt_log_recovery(self):
        pass

    def run(self):
        log.debug('node %s starting subscriber thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        # set the subscriber socket to listen to all messages
        # by any publisher. (can be optimized later)
        socket.setsockopt(zmq.SUBSCRIBE, b'')

        cluster = self.node_process.cluster()

        other_node_ports = \
            [spec.port for spec in cluster.process_specs.values() if spec.port != self.node_process.port]
        log.debug("subscriber in node %d connecting to sockets %s", self.node_id, other_node_ports)

        for port in other_node_ports:
            # NOTE:
            # - connect() can be called on multiple ports in zmq.
            # - a subscriber shouldn't connect to itself
            socket.connect("tcp://127.0.0.1:%d" % port)

        while True:
            if self.node_process.node().state == NodeState.inactive:
                continue

            message = socket.recv()
            message = pickle.loads(message)
            self.node_process.onMessage(message)

            # Polling based approach to receive messages. Can convert to blocking call if needed
            sleep(self.DELAY)


class PublishThread(Thread):

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay=0.1):
        super(PublishThread, self).__init__()

        self.node_process = node_process
        self.delay = delay
        self.node_id = node_process..node_id

    def recover(self):
        self._attempt_log_recovery()

    def stop(self):
        # flush in-memory state
        pass

    def _attempt_log_recovery(self):
        pass

    def run(self):
        log.debug('node %s starting publisher thread', self.node_id)

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        binded = False
        while not binded:
            try:
                socket.bind("tcp://127.0.0.1:%d" % self.node_process.port)
                binded = True
            except Exception:
                self.node_process.port += 1

        while True:
            if self.node_process.node().state == NodeState.inactive:
                sleep(0.01)
                continue

            if not self.node_process.message_queue.empty():
                message = self.node_process.message_queue.get()
                socket.send(pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL))
            else:
                sleep(self.delay)


class HeartbeatThread(Thread):

    '''
        Thread to keep sending out messages to neighbors and keep
        track of neighbors that have not responded. For neighbors
        that appear inactive,
    '''

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay):
        super(HeartbeatThread, self).__init__()

        self.node_process = node_process
        self.delay = delay
        self.node_id = node_process..node_id
        self.metrics = node_process.metrics

    def send_message_for_dead_nodes(self):
        dead_node_ids = self.node_process.detect_and_fetch_dead_nodes()
        for node_id in dead_node_ids:
            # Send a request to the leader informing of death
            message = messages.MessageHandler.getMsgForAction(
                source=self.node_id,
                action=messages.Action.InformLeaderOfDeath,
                msg_type=messages.MsgType.Request,
                dest=self.node_process.get_leader(),
                ctx=node_id
            )
            log.info("Node %s informing leader of death %s", self.node_id, message)
            self.node_process.sendMessage(message)

    def recover(self):
        self._attempt_log_recovery()

    def stop(self):
        # flush in-memory state
        pass

    def _attempt_log_recovery(self):
        pass

    def run(self):
        log.debug('Node %s starting heartbeat thread', self.node_id)

        while True:
            if self.node_process.node().state == NodeState.inactive:
                sleep(0.01)
                continue

            message = messages.MessageHandler.getMsgForAction(
                source=self.node_id, action=messages.Action.Heartbeat, msg_type=messages.MsgType.Request
            )
            log.info("Node %s sending heartbeat %s", self.node_id, message)
            self.node_process.sendMessage(message)
            self.metrics.increase_metric(self.node_id, "heartbeats_sent")
            self.send_message_for_dead_nodes()
            sleep(self.delay)
