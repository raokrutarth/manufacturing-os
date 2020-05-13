import logging
import items

from typing import List
from collections import defaultdict

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

def bootstrap_all_paths(nodes: List[BaseNode]):
    """
    Create a flow with all possible dependency paths
    """
    cluster_flow = ClusterWideFlow(nodes)
    # Iterate over all nodes
    for node_input in cluster_flow.nodes:
        # Iterate over their input requirements
        for input in node_input.dependency.input_item_reqs:
            # Iterate over all nodes
            for node_output in cluster_flow.nodes:
                # Iterate over their output requirements
                result = node_output.dependency.result_item_req
                # add flow if item id in result = item id in input
                if result.item.id == input.item.id:
                    cluster_flow.addFlow(node_output.node_id, node_input.node_id, result.item)

    return cluster_flow

class ClusterWideFlow(object):
    """
    Object storing details of the cluster wide flow
    All nodes should interact e.g. get requests through this interface
    """

    def __init__(self, nodes: List[BaseNode]): # Shouldn't that be ItemNodes?
        self.node_ids = [n.node_id for n in nodes]
        self.nodes = nodes
        self.outgoing_flows = {n: [] for n in self.node_ids}
        self.incoming_flows = {n: [] for n in self.node_ids}

    def addNode(self, node_id):
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)
            self.outgoing_flows[node_id] = []
            self.incoming_flows[node_id] = []

    def addFlow(self, source, dst, item: items.ItemReq):
        assert (source in self.node_ids) and (dst in self.node_ids), "Source: {}, Dst: {}".format(source, dst)
        self.outgoing_flows[source].append((dst, item))
        self.incoming_flows[dst].append((source, item))

    def getOutgoingFlowsForNode(self, node_id):
        """
        Outgoing flows i.e. nodes to which node_id is supposed to give items
        """
        return self.outgoing_flows[node_id]

    def getIncomingFlowsForNode(self, node_id):
        """
        Incoming flows i.e. nodes from which node_id is supposed to recieve items
        """
        return self.incoming_flows[node_id]

    def clearAll(self):
        self.node_ids = []
        self.outgoing_flows = {}
        self.incoming_flows = {}

    def __repr__(self):
        return "{}".format(self.outgoing_flows)
