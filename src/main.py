import asyncio
import logging
from typing import List
import os
from multiprocessing import Process
from time import sleep

import nodes
import processes
import operations
import cluster
import basecases


# configure logging with filename, function name and line numbers
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "DEBUG"),
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    format='%(levelname)s [%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s] %(message)s',
)
log = logging.getLogger()


def spawn_cluster_processes(cluster, flags):
    for node in cluster.nodes:
        Process(target=processes.SocketBasedNodeProcess, args=(node, cluster, flags)).start()
        log.debug("Node %d started", node.node_id)


def main():
    # determine nodes (of type single item node) and operations for the demo cluster
    demo_nodes = basecases.bootstrap_dependencies_three_nodes()

    demo_ops = {n.node_id: [operations.Op.UpdateDep] for n in demo_nodes}

    # build the cluster object
    demo_blueprint = cluster.ClusterBlueprint(demo_nodes, demo_ops)
    demo_cluster = cluster.Cluster(demo_blueprint)

    log.info("Starting %s", demo_cluster)

    # TODO (Krutarth): Make this truly asynchronous, we have barriers due to await at the moment so our current
    #  design doesn't have independent threads operating

    # start the nodes with operations enabled
    flags = {'runOps': True}
    spawn_cluster_processes(demo_cluster, flags)

    # for node in demo_cluster.nodes:
    #     # since start() for the node is an async, non-blocking method, use await
    #     # to make sure the node is started successfully.
    #     await processes.SocketBasedNodeProcess(node, demo_cluster, flags).start()
    #
    # for node in demo_cluster.nodes:
    #     await processes.SocketBasedNodeProcess(node, demo_cluster, flags).bootstrap()
    #     log.debug("Node %d started", node.node_id)

    log.info("All nodes started")
    while 1:
        sleep(60)


if __name__ == "__main__":
    main()
    log.critical("All nodes exited")
