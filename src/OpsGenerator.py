import enum
from threading import Thread, Event
import logging
import random
import messages
import copy

from op import Op

from threading import Thread
from time import sleep
from typing import List
from nodes import SingleItemNode
import operations

log = logging.getLogger()

class OpsGenerator(Thread):
    # random_ops to be dynamically set according to use cases
    SU, KILL, RECOVER = Op.SendUpdateDep, Op.Kill, Op.Recover
    random_ops = [KILL, RECOVER]

    def __init__(self, cluster, queues, delay=1):
        '''
            name: unique name of stage. Used to identify log file.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_batch: time in seconds it takes to make one unit.
            inbound_node_fetcher: function implemented by node that allows fetching incoming nodes
        '''
        super(OpsGenerator, self).__init__()
        self.name = "Operation Generator"
        self.cluster = cluster
        self.queues = queues
        self.delay = delay

        self.running = Event()
        self.running.set()  # set the stage to run by default

    def getRandomOperation(self):
        if random.random()>0:
            return random.choice(OpsGenerator.random_ops)
        else:
            return None

    def is_node_part_of_flow(node_id):
        # Only kills a node if they are part of the supply chain
        leader = self.node_process.state_helper.get_leader()
        flow = self.node_process.state_helper.get_flow()
        if leader == self.node_id:
            return False
        elif flow is not None:
            try:
                ins = len(flow.getIncomingFlowsForNode(str(node_id)))
                outs = len(flow.getOutgoingFlowsForNode(str(node_id)))
                if (ins * outs) > 0:
                    if random.random() < 0.5:
                        log.warning("Killing node: {}".format(node_id))
                        return True
                    else:
                        return False
            except Exception:
                return False
        else:
            return False

    def run(self):
        failure_rate = 0.2
        while self.running.is_set():
            op = self.getRandomOperation()
            if op != None:
                for node in self.cluster.nodes:
                    if random.random() < failure_rate:
                        self.queues[node.node_id].put(op)
            sleep(self.delay)

            #for node in cluster.nodes:
            #    node.node_id

# for testing purposes
def _test():
    print(OpsGenerator.getRandomOperation())

if __name__ == "__main__":
    _test()