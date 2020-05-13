import asyncio
import logging
import os
from multiprocessing import Process
from time import sleep

import nodes
import processes
import operations
import cluster
import items

# configure logging with filename, function name and line numbers
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "DEBUG"),
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    format='%(levelname)s [%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s] %(message)s',
)
log = logging.getLogger()

NUM_NODES = 3


async def main():
    # determine nodes (of type single item node) and operations for the demo cluster
    # TODO determine bootstrap dependency per node --
    demo_nodes = [
        nodes.SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(NUM_NODES)
    ]
    demo_ops = {n.node_id: [operations.Op.Allocate, operations.Op.UpdateDep] for n in demo_nodes}
    #demo_ops = {n.node_id: [operations.Op.Heartbeat] for n in demo_nodes}
    #demo_ops = {n.node_id: [operations.Op.Allocate, operations.Op.UpdateDep, operations.Op.Heartbeat] for n in demo_nodes}

    # build the cluster object
    demo_blueprint = cluster.ClusterBlueprint(demo_nodes, demo_ops)
    demo_cluster = cluster.Cluster(demo_blueprint)

    log.info("Starting %s", demo_cluster)

    # start the nodes with operations enabled
    flags = {'runOps': True}
    for node in demo_cluster.nodes:
        # since start() for the node is an async, non-blocking method, use await
        # to make sure the node is started successfully.
        await processes.SocketBasedNodeProcess(node, demo_cluster, flags).start()
        log.debug("Node %d started", node.node_id)

    for node in demo_cluster.nodes:
        await processes.SocketBasedNodeProcess(node, demo_cluster, flags).bootstrap()
        log.debug("Node %d started", node.node_id)

    log.info("All nodes started")
    while 1:
        sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    log.critical("All nodes exited")
