import unittest
import logging
import basecases
import random
import time
from raft import FileHelper

from cluster import Cluster
import processes as proc
from time import sleep
from multiprocessing import Process


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger()


class BootstrapCluster(unittest.TestCase):

    def setUp(self):
        self.blueprint = basecases.dummyBlueprintCase0()
        self.cluster = Cluster(self.blueprint)
        self.TIMEOUT = 3.0

    def spawn_cluster_process(self, runOps):
        flags = {'runOps': runOps}
        for node in self.cluster.nodes:
            Process(target=proc.SocketBasedNodeProcess, args=(node, self.cluster, flags)).start()

    def spawn_process(self, cluster, target):
        processes = set()
        try:
            for node in cluster.nodes:
                node_args = (node, cluster)
                p = Process(target=target, args=node_args)
                p.start()
                processes.add(p)

            while processes:
                for process in tuple(processes):
                    process.join()
                    processes.remove(process)
        finally:
            for process in processes:
                if process.is_alive():
                    log.warning('Terminating %r', process)
                    process.terminate()


class TestBootstrapCluster(BootstrapCluster):

    def test_bootstrap_cluster(self):
        log.info(self.cluster)
        self.spawn_cluster_process(runOps=False)
        sleep(self.TIMEOUT)

    def test_bootstrap_cluster_with_ops(self):
        self.blueprint = basecases.dummyBlueprintCase1()
        self.cluster = Cluster(self.blueprint)
        log.info(self.cluster)
        self.spawn_cluster_process(runOps=True)
        sleep(self.TIMEOUT)


class TestFileBasedLeaderElection(BootstrapCluster):

    DELAY = 3

    def run_leader_election(self, node, file_helper):
        # Random sleep before applying for leadership
        sleep(random.random() * self.DELAY)
        file_helper.apply_for_leadership()
        log.info("Node {} applied for leadership on: {}".format(node, time.time()))

    def get_elected_leader(self, node, file_helper):
        leader = file_helper.get_leader()
        log.info("Node {} detected leader: {}".format(node, leader))

    def run_node(self, node, cluster):
        print("node %s started" % (node))
        file_helper = FileHelper(node, cluster)
        self.run_leader_election(node, file_helper)
        time.sleep(self.DELAY)
        self.get_elected_leader(node, file_helper)
        log.info("%s : exited" % (node))

    def test_leader_election(self):
        self.blueprint = basecases.dummyBlueprintCase1()
        self.cluster = Cluster(self.blueprint)
        log.info(self.cluster)
        self.spawn_process(cluster=self.cluster, target=self.run_node)
        sleep(self.TIMEOUT)


if __name__ == '__main__':
    unittest.main()