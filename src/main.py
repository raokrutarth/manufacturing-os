import logging
import os
import argparse
import sys
from time import sleep

import processes
import operations
import cluster
import basecases
from multiprocessing import Process
from metrics import Metrics


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


def run_node_routine(node, demo_cluster, flags):
    node_process = processes.SocketBasedNodeProcess(node, demo_cluster, flags)
    node_process.start()
    log.debug("Node %d started", node.node_id)
    while 1:
        sleep(60)


def main(args):

    # determine nodes (of type single item node) and operations for the demo cluster
    # TODO: Add more fine-grained control over the exact topology and number of nodes
    if args.num_nodes == 3:
        demo_nodes = basecases.bootstrap_dependencies_three_nodes()
    elif args.num_nodes == 6:
        demo_nodes = basecases.bootstrap_dependencies_six_nodes()
    elif args.num_nodes == 7:
        demo_nodes = basecases.bootstrap_dependencies_seven_nodes()
    else:
        log.error("%d node count not supported by any demo/test scenerio", args.num_nodes)
        demo_nodes = None

    SU, BD = operations.Op.SendUpdateDep, operations.Op.BroadcastDeath
    demo_ops = {n.node_id: [SU, SU, BD, BD, BD, BD, BD, BD] for n in demo_nodes}

    metrics = Metrics()

    # build the cluster object
    demo_blueprint = cluster.ClusterBlueprint(demo_nodes, demo_ops)
    demo_cluster = cluster.Cluster(metrics, demo_blueprint)

    log.critical("Starting %s", demo_cluster)

    # start the nodes with operations runner based on what's specified
    flags = {'runOps': args.run_test_ops}

    process_set = set()
    try:
        for node in demo_cluster.nodes:
            node_args = (node, demo_cluster, flags)
            p = Process(target=run_node_routine, args=node_args)
            p.start()
            process_set.add(p)

        log.critical("All nodes started")

        while process_set:
            for process in tuple(process_set):
                process.join()
                process_set.remove(process)
    finally:
        for process in process_set:
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
        '--num_nodes',
        default=3,
        type=int,
    )
    parser.add_argument(
        '--topology',
        default="simple",
        type=str,
        help='Type of graph topology to use',
    )

    # Options to interact and simulate the system
    parser.add_argument(
        '--run_test_ops',
        default=True,
        type=str2bool,
        help='Whether to run test ops or not',
    )
    parser.add_argument(
        '--run_cli',
        default=False,
        type=str2bool,
        help='Whether to run the interative cli',
    )
    parser.add_argument(
        '--ops_to_run',
        default=[],
        type=str2list,
        help='Which ops to run on each node during test bootstrap. Seperated by "_"',
    )
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
