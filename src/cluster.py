from typing import List
from collections import defaultdict
import logging

from nodes import BaseNode, ProcessSpec

log = logging.getLogger()


class ClusterBlueprint(object):
    """
    Represents the cluster blueprint to create Clusters from
    Useful for unit tests and designing test cases we want to operate on.
    """

    def __init__(self, nodes: List[BaseNode], ops=defaultdict(lambda: [])):
        # Set of nodes to be used by this cluster
        self.nodes = nodes
        # Stores any node specific operations we want to perform during execution e.g.
        # injecting node specific random failures, delays, etc
        self.node_specific_ops = ops
        # Stores the flags and options we'd be using finally in our setup
        self.flags = {}


class Cluster(object):
    """
    Represents the set of nodes interacting
    """

    def __init__(self, blueprint, port_range_start=5000):
        self.blueprint = blueprint
        self.nodes = self.blueprint.nodes
        self.node_ids = [n.node_id for n in self.nodes]
        self.process_specs = None
        self.init_process_specs(port_range_start)

    def init_process_specs(self, port_range_start):
        # assign a process name and port to process
        self.process_specs = {
            node.node_id: ProcessSpec('process-{}'.format(i), port_range_start + i) for i, node in enumerate(self.nodes)
        }

    def __repr__(self):
        return 'Cluster:\n\tNodes: {}\n\tProcesses: {}'.format(self.nodes, self.process_specs.values())
