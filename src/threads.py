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
        self.node_id = node_process.node_id
        self.DELAY = 0.001

    def recover(self):
        self._attempt_log_recovery()

    def stop(self):
        # flush in-memory state
        pass

    def _attempt_log_recovery(self):
        pass

    def run(self):
        log.debug('node %s starting subscriber thread', self.node_id)

        while True:
            if not self.node_process.is_active:
                continue

            message = self.node_process.comm_queues[self.node_id].get()
            message = pickle.loads(message)
            self.node_process.onMessage(message)


class PublishThread(Thread):

    def __init__(self, node_process: 'SocketBasedNodeProcess', delay=0.001):
        super(PublishThread, self).__init__()

        self.node_process = node_process
        self.delay = delay
        self.node_id = node_process.node_id

    def recover(self):
        self._attempt_log_recovery()

    def stop(self):
        # flush in-memory state
        pass

    def _attempt_log_recovery(self):
        pass

    def run(self):
        log.debug('node %s starting publisher thread', self.node_id)

        while True:
            if not self.node_process.is_active:
                sleep(0.01)
                continue

            message = self.node_process.message_queue.get()
            bmsg = pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL)
            if message.dest == -1:
                for nid in self.node_process.node_ids:
                    self.node_process.comm_queues[nid].put(bmsg)
            else:
                self.node_process.comm_queues[message.dest].put(bmsg)


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
        self.node_id = node_process.node_id
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
            if not self.node_process.is_active:
                sleep(0.05)
                continue

            message = messages.MessageHandler.getMsgForAction(
                source=self.node_id, action=messages.Action.Heartbeat, msg_type=messages.MsgType.Request
            )
            self.node_process.sendMessage(message)
            self.metrics.increase_metric(self.node_id, "heartbeats_sent")
            self.send_message_for_dead_nodes()
            sleep(self.delay)
