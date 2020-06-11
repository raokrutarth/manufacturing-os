import code
import logging
import os
import argparse
import sys
import shutil
import processes
import operations
import basecases
import time
import cluster as ctr
import plotter as pltr

from time import sleep
from multiprocessing import Process, Queue
from threading import Thread
from metrics import Metrics
from operations import Operations as Op
from ops_generator import run_generator
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
TMP_PATH = os.path.abspath("./tmp")
shutil.rmtree(TMP_PATH, ignore_errors=True)  # Remove tmp to remove old WALs
os.makedirs(TMP_PATH, exist_ok=True)

# configure logging with filename, function name and line numbers
logFormatter = logging.Formatter(
    datefmt='%H:%M:%S',
    # add %(process)s to the formatter to see PIDs
    fmt='%(levelname)-6s  %(asctime)s %(threadName)-12s %(filename)s:%(lineno)s::'
        '%(funcName)-20s | %(message)s',
)
fileHandler = logging.FileHandler(TMP_PATH + "/manufacturing-os.log", mode="w+")
fileHandler.setFormatter(logFormatter)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(fileHandler)
log.addHandler(consoleHandler)


def run_node_routine(node, cluster, queue, cqueues):
    node_process = processes.SocketBasedNodeProcess(node, cluster, queue, cqueues)
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


def run_cluster_plotter(cluster: ctr.Cluster):
    num_nodes = len(cluster.nodes)
    delay = 0.25 * (num_nodes ** 0.3)
    sleep(delay)
    plotter = pltr.ClusterPlotter()
    while 1:
        plotter.plot_current_state()
        sleep(delay)
        log.debug("Completed plotting step...")


def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]


def main(args):

    # nodes = basecases.bootstrap_demo()
    nodes = basecases.bootstrap_demo_mid_2()
    # nodes = basecases.bootstrap_random_dag(args.num_types, args.complexity, args.nodes_per_type)

    # build the cluster object
    blueprint = ctr.ClusterBlueprint(nodes)
    cluster = ctr.Cluster(blueprint)

    log.critical("Starting %s", cluster)

    process_list = list()
    queues = {}
    comm_queues = {}

    # Create messaging queues to interact with cluster
    for node in cluster.nodes:
        queue = Queue()
        queues[node.node_id] = queue
        cqueue = Queue()
        comm_queues[node.node_id] = cqueue

    # Contain multiple misc threads which are useful
    ops_args = (queues, args.failure_rate, args.recover_rate, args.update_dep_rate, args.leader_can_fail)
    ops_generator_thread = Thread(target=run_generator, args=ops_args)
    plotter_thread = Thread(target=run_cluster_plotter, args=(cluster,))
    threads = {}

    if args.run_plotter:
        threads['cluster-plotter'] = plotter_thread
    if args.run_random_ops:
        threads['ops-runner'] = ops_generator_thread

    # Start all the threads
    for k, thread in threads.items():
        thread.name = k
        thread.daemon = True
        thread.start()

    try:
        metrics = Metrics("main")
        for node in cluster.nodes:
            node_args = (node, cluster, queues[node.node_id], comm_queues)
            p = Process(target=run_node_routine, args=node_args)
            p.start()
            process_list.append(p)
            metrics.increase_metric(-1, "num_nodes")

        log.critical("All nodes started")

        if args.run_client:
            # Wait for the client thread to exit
            run_cluster_client(queues)

        # Join the threads spawned in a safe manner
        while has_live_threads(threads.values()):
            try:
                for _, thread in threads.items():
                    if thread is not None and thread.is_alive():
                        thread.join()
            except KeyboardInterrupt:
                # Handle Ctrl-C and send kill to threads
                for p in process_list:
                        p.terminate()
                sys.exit()

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
        default=5,
        type=int,
    )
    parser.add_argument(
        '--complexity',
        default="high",
        type=str
    )
    parser.add_argument(
        '--nodes_per_type',
        default=3,
        type=int
    )

    parser.add_argument(
        '--leader_can_fail',
        default=False,
        type=str2bool,
        help='kill leader or not'
    )

    parser.add_argument(
        '--failure_rate',
        default=0,
        type=float,
        help='# of failed nodes per minute'
    )
    parser.add_argument(
        '--recover_rate',
        default=0,
        type=float,
        help='# of recovered nodes per minute'
    )

    parser.add_argument(
        '--update_dep_rate',
        default=0,
        type=int,
        help='# of update dependence per minute'
    )

    # Options to interact and simulate the system
    parser.add_argument('--run_plotter', default=False, type=str2bool, help='Whether to run the GUI plotter')
    parser.add_argument('--run_client', default=False, type=str2bool, help='Whether to run the interactive cli')
    parser.add_argument('--run_random_ops', default=True, type=str2bool, help='Whether to run random operations')
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
