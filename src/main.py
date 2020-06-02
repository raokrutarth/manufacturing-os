import code
import logging
import os
import argparse
import sys
from time import sleep

import processes
import operations
import cluster as ctr
import basecases
from multiprocessing import Process
from metrics import Metrics

from time import sleep
from operations import Op
from multiprocessing import Process, Queue


"""
Logging guidelines are provided here. Importance increases while going down
@ DEBUG
    - Every log e.g. ops inside nodes, debug statements, etc
@ INFO
    - Every informative log e.g. connection established, message received, etc
    - Messages sent and received by nodes
    - New operations being run
@ WARNING
    - Missed heartbeats
    - Cluster Flow changes
@ ERROR
    - Node deaths
@ CRITICAL
    - N/A
"""

# configure logging with filename, function name and line numbers
logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "DEBUG"),
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    format='%(levelname)-6s  %(asctime)s %(threadName)-12s %(filename)s:%(lineno)s::'
           '%(funcName)-20s | %(message)s',
)
log = logging.getLogger()


def run_node_routine(node, cluster, queue, flags):
    node_process = processes.SocketBasedNodeProcess(node, cluster, queue, flags)
    node_process.start()
    log.debug("Node %d started", node.node_id)
    while 1:
        sleep(60)


def run_cluster_client(queues):
    """
    Create client to interact with all clusters with simple
    """
    
    def execute(node_id, op: Op):
        """
        Executes the provided command by adding the operation to the queue
        """
        queues[node_id].put(op)

    code.interact(banner='Interactive client to perform operations on the cluster',
                  local=dict(globals(), **locals()),
                  exitmsg='Performed all interactions. exiting and continuing...')


def main(args):

    log.info("""Nodes are being created through bootstrap_ranodom_dag() with %s number of types, 
    %s complexity of the graph, and max. %s nodes with the same type""", args.num_types, args.complexity, args.nodes_per_type)    
    # nodes = basecases.bootstrap_dependencies_three_nodes()
    # nodes = basecases.bootstrap_dependencies_six_nodes()
    # nodes = basecases.bootstrap_dependencies_seven_nodes()
    nodes = basecases.bootstrap_random_dag(args.num_types, args.complexity, args.nodes_per_type)
    log.info("The following nodes have been created %s", nodes)

    SU, BD = operations.Op.SendUpdateDep, operations.Op.BroadcastDeath
    demo_ops = {n.node_id: [SU, SU, BD] for n in nodes}

    metrics = Metrics()

    # build the cluster object
    blueprint = ctr.ClusterBlueprint(nodes, demo_ops)
    cluster = ctr.Cluster(metrics, blueprint)

    log.critical("Starting %s", cluster)

    # start the nodes with operations runner based on what's specified
    flags = {'runOps': args.run_test_ops}

    process_list = list()
    queues = {}

    # Create messaging queues to interact with cluster
    for node in cluster.nodes:
        queue = Queue()
        # Add the pre-planned operations
        for op in cluster.blueprint.node_specific_ops[node.node_id]:
            queue.put(op)
        queues[node.node_id] = queue

    try:
        for node in cluster.nodes:
            node_args = (node, cluster, queues[node.node_id], flags)
            p = Process(target=run_node_routine, args=node_args)
            p.start()
            process_list.append(p)

        log.critical("All nodes started")

        if args.run_client:
            # Wait for the client thread to exit
            run_cluster_client(queues)

        # Stopping the queue worker
        for queue in queues.values():
            queue.close()
            queue.join_thread()

        while process_list:
            for process in tuple(process_list):
                process.join()
                process_list.remove(process)
    finally:
        for process in process_list:
            if process.is_alive():
                log.warning('Terminating %r', process)
                process.terminate()


"""
Utilities for argument parsing. Helps provide easy running of experiments.
"""


def str2bool(s):
    """Convert string to bool (in argparse context)."""
    if s.lower() not in ['true', 'false']:
        raise ValueError('Need bool; got %r' % s)
    return {'true': True, 'false': False}[s.lower()]


def str2list(s):
    """Convert string to list of strs, split on _"""
    return s.split('_')


def get_cluster_run_args():
    parser = argparse.ArgumentParser()

    # General global training parameters
    parser.add_argument(
        '--num_types',
        default=4,
        type=int,
    )
    parser.add_argument(
        '--complexity', 
        default="medium", 
        type=str
    )
    parser.add_argument(
        '--nodes_per_type', 
        default=2, 
        type=int
    )
    parser.add_argument(
        '--topology',
        default="simple",
        type=str,
        help='Type of graph topology to use',
    )

    # Options to interact and simulate the system
    parser.add_argument('--run_test_ops', default=True, type=str2bool, help='Whether to run test ops or not')
    parser.add_argument('--run_client', default=False, type=str2bool, help='Whether to run the interative cli')
    parser.add_argument('--ops_to_run', default=[], type=str2list, help='Which ops to allow running for tests')

    # Execution level arguments
    parser.add_argument(
        '--log_level',
        default="debug",
        type=str,
        help='Logging level to set'
    )

    return parser


if __name__ == "__main__":
    p = get_cluster_run_args()
    main_args = p.parse_args()

    # Init log level according to what's specified
    logging.getLogger().setLevel(main_args.log_level.upper())

    main(main_args)

    log.critical("All nodes exited")
