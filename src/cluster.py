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

    def update_deps(self, node: SingleItemNode, new_dependency: items.ItemDependency):
        for idx in range(len(self.nodes)):
            if self.nodes[idx].node_id == node:
                self.nodes[idx].dependency = new_dependency

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
                if result and input and result.item.id == input.item.id:
                    cluster_flow.addFlow(node_output.node_id, node_input.node_id, result)

    return cluster_flow

def output_possible_path(cluster_flow: ClusterWideFlow, start_node_id, end_node_id, path=[]):
    """
    Find one possible path for a given ClusterWideFlow. It is a recursive depth-first algorithm 
    that tries to find the start_node to validate whether a given path is valid.
    """
    #print("Next Loop with start_node: " + str(start_node_id) + " and end_node: " + str(end_node_id))
    
    # This is the return function -> when arriving at the starting node.
    if (start_node_id == end_node_id):
        return [(start_node_id, start_node_id)]
    
    requirements = [] # Stores only ids of the required item types. 
    end_node = next((x for x in cluster_flow.nodes if x.node_id == end_node_id), None) # find the end node based off of its id

    if end_node:
        for input in end_node.dependency.input_item_reqs:
            requirements.append(input.item.id)
    
    # Loop over all incoming edges
    for incoming in cluster_flow.incoming_flows[end_node_id]:
        node = next((x for x in cluster_flow.nodes if x.node_id == incoming[0]), None)

        # Only check node out if its type is in requirements, i.e. some items have already been delivered.
        if node and node.dependency.result_item_req.item.id in requirements:
            # Recursive function starts here -> end_node is changed to current node.
            new_path = output_possible_path(cluster_flow, start_node_id, node.node_id, path)    
            boolean = [item for item in new_path if item[0] == start_node_id] # Check if start_node in path
        
            # print("NEW PATH: " + str(new_path))
            # print("Requirements: " + str(requirements))
            # print("Incoming Node: " + str(node.node_id))
            # print("Current Node: " + str(end_node_id))
            # print("Boolean: " + str(boolean))

            # If start_node in path, the path is viable -> append it to the path + remove the item type from the requirements
            if boolean:
                path.append((node.node_id, end_node_id))
                requirements.remove(node.dependency.result_item_req.item.id)
    
    # print("Current Path at " + str(end_node_id))
    # print("Path " + str(path))
    # print("Requirements " + str(requirements))
    if requirements: # If still some item types in the requirements, path is not viable
        path = []
    return path

def bootstrap_flow(nodes: List[SingleItemNode]):
    """
    Create a flow with a possible path
    """
    # Create a cluster_flow with all possible paths first
    cluster_flow = bootstrap_all_paths(nodes)
    start_node = nodes[0].node_id
    end_node = nodes[len(nodes)-1].node_id

    log.debug("Cluster flow with all possible paths created: {}".format(cluster_flow))

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

    log.debug("Cluster flow with one specific path created: {}".format(cluster_flow_final))

    return cluster_flow_final
     



# For testing purposes
def main():
    demo_nodes = basecases.bootstrap_dependencies_six_nodes_node_death()
    cluster_flow_obj = bootstrap_flow(demo_nodes)

    print(cluster_flow_obj)
    return cluster_flow_obj

if __name__ == "__main__":
    main()