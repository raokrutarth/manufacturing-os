import logging
import items

from typing import List
from collections import defaultdict

from nodes import BaseNode, ProcessSpec, SingleItemNode
import basecases

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

    def __init__(self, metrics, blueprint, port_range_start=40000):
        self.blueprint = blueprint
        self.nodes = self.blueprint.nodes
        self.process_specs = None
        self.init_process_specs(port_range_start)
        self.metrics = metrics

    def init_process_specs(self, port_range_start: int):
        # assign a process name and port to process
        self.process_specs = {}

        for node in self.nodes:
            self.process_specs[node.node_id] = ProcessSpec(
                'process-{}'.format(node.node_id),
                port_range_start + node.node_id,
            )

    def update_deps(self, node_id: int, new_dependency: items.ItemDependency):
        for idx in range(len(self.nodes)):
            if self.nodes[idx].node_id == node_id:
                self.nodes[idx].dependency = new_dependency

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
        if node_id not in self.outgoing_flows:
            log.error("Node %d's outgoing edges not found in cluster flow", node_id)
            return {}
        return self.outgoing_flows[node_id]

    def getIncomingFlowsForNode(self, node_id):
        """
        Incoming flows i.e. nodes from which node_id is supposed to recieve items
        """
        if node_id not in self.incoming_flows:
            log.error("Node %d's incoming edges not found in cluster flow", node_id)
            return {}
        return self.incoming_flows[node_id]

    def clearAll(self):
        self.node_ids = []
        self.outgoing_flows = {}
        self.incoming_flows = {}

    def __repr__(self):
        return "ClusterWideFlow(\n\tincoming edges:{}\n\toutgoing edges:{}\n\tnode IDs: {}\n)".format(
            self.incoming_flows, self.outgoing_flows, self.node_ids,
        )


def bootstrap_all_paths(nodes: List[SingleItemNode]):
    """
    Create a flow with all possible dependency paths
    """

    cluster_flow = ClusterWideFlow(nodes)
    # Iterate over all nodes
    for node_input in cluster_flow.nodes:
        # Iterate over their input requirements
        for input_req in node_input.dependency.input_item_reqs:
            # Iterate over all nodes
            for node_output in cluster_flow.nodes:
                # Iterate over their output requirements
                result_req = node_output.dependency.result_item_req
                # add flow if item type in result = item type in input
                if result_req and input_req and result_req.item.type == input_req.item.type:
                    cluster_flow.addFlow(node_output.node_id, node_input.node_id, result_req)

    return cluster_flow


def output_possible_path(cluster_flow: ClusterWideFlow, start_node_id, end_node_id, path=[]):
    """
    Find one possible path for a given ClusterWideFlow. It is a recursive depth-first algorithm
    that tries to find the start_node to validate whether a given path is valid.
    """
    # This is the return function -> when arriving at the starting node.
    if (start_node_id == end_node_id):
        return [(start_node_id, start_node_id)]

    requirements = []  # Stores only ids of the required item types.
    end_node = next((x for x in cluster_flow.nodes if x.node_id == end_node_id), None)  # find the end node based off of its id

    if end_node:
        for input in end_node.dependency.input_item_reqs:
            requirements.append(input.item.type)

    # Loop over all incoming edges
    for incoming in cluster_flow.incoming_flows[end_node_id]:
        node = next((x for x in cluster_flow.nodes if x.node_id == incoming[0]), None)

        # Only check node out if its type is in requirements, i.e. some items have already been delivered.
        if node and node.dependency.result_item_req.item.type in requirements:
            # Recursive function starts here -> end_node is changed to current node.
            new_path = output_possible_path(cluster_flow, start_node_id, node.node_id, path)
            boolean = [item for item in new_path if item[0] == start_node_id] # Check if start_node in path

            # If start_node in path, the path is viable -> append it to the path + remove the item type from the requirements
            if boolean:
                path.append((node.node_id, end_node_id))
                requirements.remove(node.dependency.result_item_req.item.type)

    if requirements:  # If still some item types in the requirements, path is not viable
        path = []
    return path


def bootstrap_flow(nodes: List[SingleItemNode]):
    """
    Create a flow with a possible path
    """
    # Create a cluster_flow with all possible paths first
    log.debug("Bootstrapping flow has started.")
    cluster_flow = bootstrap_all_paths(nodes)
    start_node = nodes[0].node_id
    end_node = nodes[len(nodes)-1].node_id

    log.info("Cluster flow with all possible paths created: {}".format(cluster_flow))

    # Create a new ClusterWideFlow object containing only one possible paths.
    cluster_flow_final = ClusterWideFlow(nodes)

    # Output one possible path
    possible_path = output_possible_path(cluster_flow, start_node, end_node)
    possible_path_set = list(set(possible_path))

    # Add all edges to ClusterWideFlow object
    for edge in possible_path_set:
        node = next((x for x in cluster_flow.nodes if x.node_id == edge[0]), None)
        cluster_flow_final.addFlow(
            edge[0], edge[1], node.dependency.result_item_req
        )

    log.info("Cluster flow with one specific path created: {}".format(cluster_flow_final))

    return cluster_flow_final


# for testing purposes
def _test():
    number_types = 10
    complexity = "medium"
    nodes_per_type = 10
    demo_nodes = basecases.bootstrap_random_dag(number_types, complexity, nodes_per_type)
    print("Nodes have been created.")
    print(demo_nodes)
    cluster_flow_obj = bootstrap_flow(demo_nodes)
    print("ClusterWideFlow Object has created.")
    print(cluster_flow_obj)
    return cluster_flow_obj


if __name__ == "__main__":
    _test()
