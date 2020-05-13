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
import items

# configure logging with filename, function name and line numbers
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "DEBUG"),
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    format='%(levelname)s [%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s] %(message)s',
)
log = logging.getLogger()

async def bootstrap_dependencies_three_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> 1 -> 2
    """ 
    demo_nodes = [
        nodes.SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(3)
    ]

    wood = items.ItemReq(items.Item('wood', 0), 1)
    door = items.ItemReq(items.Item('door', 1), 1)
    house = items.ItemReq(items.Item('house', 2), 1)

    demo_nodes[0].dependency = items.ItemDependency([], wood)
    demo_nodes[1].dependency = items.ItemDependency([wood], door)
    demo_nodes[2].dependency = items.ItemDependency([door], house)

    return demo_nodes

async def bootstrap_dependencies_five_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> | ->  1 -----> | -> 3 -> | -> 4 -> | -> 5
           ->  2 -> |-> |         |
                 -> |-----------> |
    """
    demo_nodes = [
        nodes.SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(6)
    ]

    start = items.ItemReq(items.Item('start', 0), 1)
    wood = items.ItemReq(items.Item('wood', 1), 1)  # There is always only one node starting the whole graph!
    timber = items.ItemReq(items.Item('timber', 2), 1)
    premium_timber = items.ItemReq(items.Item('premium_timber', 3), 1)
    door = items.ItemReq(items.Item('door', 4), 1)
    house = items.ItemReq(items.Item('house', 5), 1)

    demo_nodes[0].dependency = items.ItemDependency([], start)
    demo_nodes[1].dependency = items.ItemDependency([start], wood)
    demo_nodes[2].dependency = items.ItemDependency([start], timber)
    demo_nodes[3].dependency = items.ItemDependency([wood, timber], premium_timber)
    demo_nodes[4].dependency = items.ItemDependency([timber, premium_timber], door)
    demo_nodes[5].dependency = items.ItemDependency([door], house)

    return demo_nodes

async def main():
    # determine nodes (of type single item node) and operations for the demo cluster
    #demo_nodes = await bootstrap_dependencies_three_nodes()
    demo_nodes = await bootstrap_dependencies_five_nodes()

    demo_ops = {n.node_id: [operations.Op.Allocate, operations.Op.UpdateDep] for n in demo_nodes}

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
