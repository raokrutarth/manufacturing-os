import asyncio
import logging
import os
from multiprocessing import Process

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

NUM_NODES = 5

async def main():
    # determine nodes (of type single item node) and operations for the demo cluster
    demo_nodes = [
        nodes.SingleItemNode({
            'node_id': i,

            # TODO determine bootstrap dependency per node
            'dependency': items.ItemDependency([], ""),
            }) for i in range(NUM_NODES)
    ]
    demo_ops = {n.node_id: [operations.Op.Allocate] for n in demo_nodes}

    # build the cluster object
    demo_blueprint = cluster.ClusterBlueprint(demo_nodes, demo_ops)
    demo_cluster = cluster.Cluster(demo_blueprint)

    log.info("Starting %s", demo_cluster)

    # start the nodes with operations enabled
    flags = {'runOps': True}
    running_nodes = []
    for node in demo_cluster.nodes:
        rn = asyncio.ensure_future(
            processes.SocketBasedNodeProcess(node, demo_cluster, flags).start()
        )
        running_nodes.append(rn)
    log.info("All nodes started")

    # log exits as nodes crash, if they crash/exit
    for rn in running_nodes:
        await rn
        log.critical("a node exited")

    log.critical("All nodes exited")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
