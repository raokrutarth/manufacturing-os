import asyncio
import logging
import os
import processes
import operations
import basecases
import argparse
import cluster as ctr

from time import sleep
from multiprocessing import Process


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
    level=os.environ.get("LOGLEVEL", "DEBUG"),
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    format='%(levelname)-6s  %(asctime)s %(threadName)-12s %(filename)s:%(lineno)s::'
           '%(funcName)-20s | %(message)s',
)
log = logging.getLogger()


def main(args):

    # determine nodes (of type single item node) and operations for the demo cluster
    # TODO: Add more fine-grained control over the exact topology and number of nodes
    if args.num_nodes == 3:
        nodes = basecases.bootstrap_dependencies_three_nodes()
    elif args.num_nodes == 6:
        nodes = basecases.bootstrap_dependencies_six_nodes()
    elif args.num_nodes == 7:
        nodes = basecases.bootstrap_dependencies_seven_nodes()
    else:
        nodes = None

    ops = {n.node_id: [operations.Op.SendUpdateDep] for n in nodes}

    # build the cluster object
    blueprint = ctr.ClusterBlueprint(nodes, ops)
    cluster = ctr.Cluster(blueprint)

    log.info("Starting %s", cluster)

    # start the nodes with operations runner based on what's specified
    flags = {'runOps': args.run_test_ops}

    process_set = set()

    try:
        for node in nodes:
            node_args = (node, cluster, flags)
            p = Process(target=processes.run_node_process, args=node_args)
            log.info("Started process for node: %r", node)

            p.start()
            process_set.add(p)

        while processes:
            for process in tuple(process_set):
                process.join()
                process_set.remove(process)
    finally:
        for process in process_set:
            if process.is_alive():
                log.warning('Terminating %r', process)
                process.terminate()

    log.critical("All node processes exiting")

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
    parser.add_argument('--num_nodes', default=3, type=int)
    parser.add_argument('--topology', default="simple", type=str, help='Type of graph topology to use')

    # Options to interact and simulate the system
    parser.add_argument('--run_test_ops', default=True, type=str2bool, help='Whether to run test ops or not')
    parser.add_argument('--run_cli', default=False, type=str2bool, help='Whether to run the interative cli')
    parser.add_argument('--ops_to_run', default=[], type=str2list, help='Which ops to allow running for tests')

    # Execution level arguments
    parser.add_argument('--log_level', default="debug", type=str, help='Logging level to set')
    return parser


if __name__ == "__main__":
    parser = get_cluster_run_args()
    args = parser.parse_args()

    # Init log level according to what's specified
    logging.getLogger().setLevel(args.log_level.upper())

    main(args)

    log.critical("All nodes exited")
