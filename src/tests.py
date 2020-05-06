import unittest
from time import sleep
from multiprocessing import Process

import logging
log = logging.getLogger()


import basecases
from cluster import Cluster
import processes

log = logging.getLogger()

class BootstrapCluster(unittest.TestCase):

    def setUp(self):
        self.blueprint = basecases.dummyBlueprintCase0()
        self.cluster = Cluster(self.blueprint)
        self.TIMEOUT = 3.0

    def spawn_cluster_process(self, runOps):
        flags = {'runOps': runOps}
        for node in self.cluster.nodes:
            Process(target=processes.SocketBasedNodeProcess, args=(node, self.cluster, flags)).start()


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

if __name__ == '__main__':
    unittest.main()