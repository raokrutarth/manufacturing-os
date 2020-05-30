import unittest
from time import sleep
from multiprocessing import Process

import logging
log = logging.getLogger()

import basecases
from cluster import Cluster
import processes


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


import asyncio
from random import randint
from time import sleep
import logging
from os.path import abspath
from multiprocessing import Process


def node_routine(node, cluster):

    TIME = 3
    num_lives = randint(3, 8)
    while True:
        sleep(TIME)

        leader = raftos.get_leader()
        print("Leader is: {}", leader)
        if leader == node:
            num_lives -= 3
            log.info("%s : I am leader" % (node))

        log.info("%s : exiting in %d sec" % (node, num_lives*TIME))

        num_lives -= 1
        if num_lives <= 0:
            break


def run_node(log_dir, node, cluster):
    print("node %s started" % (node))
    node_routine(node, cluster)
    log.info("%s : exited" % (node))


def test():

    cluster = set(['127.0.0.1:{}'.format(port) for port in range(30000, 30034, 2)])
    print(cluster)

    processes = set([])
    log_dir = abspath("./tmp")

    try:
        for node in cluster:
            node_args = (log_dir, node, cluster - {node})
            p = Process(target=run_node, args=node_args)
            log.info("%r", node_args)

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


if __name__ == '__main__':
    unittest.main()