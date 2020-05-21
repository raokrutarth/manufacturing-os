import logging
import items

from typing import List
from collections import defaultdict

from nodes import BaseNode, ProcessSpec, SingleItemNode

log = logging.getLogger()


class ClusterBlueprint(object):
    """
    Represents the cluster blueprint to create Clusters from
    Useful for unit tests and designing test cases we want to operate on.
    """

    def __init__(self, nodes: List[SingleItemNode], ops=defaultdict(lambda: [])):
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

    def __init__(self, blueprint: ClusterBlueprint, port_range_start=5000):
        self.blueprint = blueprint
        self.nodes = self.blueprint.nodes
        self.process_specs = None
        self.init_process_specs(port_range_start)

    def init_process_specs(self, port_range_start: int):
        # assign a process name and port to process
        self.process_specs = {}

        for node in self.nodes:
            self.process_specs[node.node_id] = ProcessSpec(
                'process-{}'.format(node.node_id),
                port_range_start + node.node_id,
            )

    def update_deps(self, node_id: int, new_dependency: items.ItemDependency):
        self.nodes[node_id].dependency = new_dependency

    def get_node(self, node_id):
        '''
            Given a node_id, returns the node object that contains
        '''
        return self.nodes[node_id]

    def get_node_process_spec(self, node_id: int):
        '''
            returns the process metadata object for a given node ID
        '''
        return self.process_specs[node_id]

    def get_node_ops(self, node_id):
        '''
            returns the process metadata object for a given node ID
        '''
        return self.blueprint.node_specific_ops[node_id]

    def __repr__(self):
        return 'Cluster:\n\tNodes: {}\n\tProcesses: {}'.format(self.nodes, self.process_specs.values())


class ClusterWideFlow(object):
    """
    Object storing details of the cluster wide flow
    All nodes should interact e.g. get requests through this interface
    """

    def __init__(self, nodes: List[SingleItemNode]):
        self.nodes = nodes
        self.node_ids = [n.node_id for n in nodes]
        self.outgoing_flows = {n: [] for n in self.node_ids}
        self.incoming_flows = {n: [] for n in self.node_ids}

    def addNode(self, node_id):
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)
            self.outgoing_flows[node_id] = []
            self.incoming_flows[node_id] = []

    def removeNode(self, node_id):
        if node_id in self.node_ids:
            self.node_ids.remove(node_id)
            self.outgoing_flows.pop(node_id)
            self.incoming_flows.pop(node_id)
            for node in self.outgoing_flows:
                for tup in node:
                    if node_id in tup:
                        node.remove(tup)
            for node in self.incoming_flows:
                for tup in node:
                    if node_id in tup:
                        node.remove(tup)

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

    def get_inbound_node_ids(self):
        return self.incoming_flows

    def __repr__(self):
        return "{}".format(self.outgoing_flows)


def bootstrap_all_paths(nodes: List[SingleItemNode]):
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
                    cluster_flow.addFlow(node_output.node_id, node_input.node_id, result)

    return cluster_flow


def shortest_path_helper(outgoing_flows, start_node, end_node, path=[]):
    '''
    Helper function that finds the shortest path in a graph.
    Output in the form of e.g. [0, 2, 4], i.e. node_id= 0 -> 2 -> 4
    '''
    path = path + [start_node]
    if start_node == end_node:
        return path
    shortest = []
    for node in outgoing_flows[start_node]:
        if node[0] not in path:
            newpath = shortest_path_helper(outgoing_flows, node[0], end_node, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


def bootstrap_shortest_path(nodes: List[SingleItemNode]):
    """
    Create a flow with the shortest path
    """
    # Create a cluster_flow with all possible paths first
    cluster_flow = bootstrap_all_paths(nodes)
    start_node = nodes[0].node_id
    end_node = nodes[len(nodes)-1].node_id

    log.debug("Cluster flow created: {}".format(cluster_flow))

    # Create a new ClusterWideFlow object containing only the shortest paths.
    cluster_flow_shortest = ClusterWideFlow(nodes)

    # Output the shortest path
    shortest = shortest_path_helper(cluster_flow.outgoing_flows, start_node, end_node)

    for i in range(len(shortest)-1):
        cluster_flow_shortest.addFlow(
            nodes[shortest[i]].node_id,
            nodes[shortest[i+1]].node_id,
            nodes[shortest[i+1]].dependency.result_item_req
        )

    log.debug("Cluster flow created: {}".format(cluster_flow_shortest))

    return cluster_flow_shortest
