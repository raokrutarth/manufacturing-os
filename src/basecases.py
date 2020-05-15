import operations
import items
from collections import defaultdict 

import graph_funcs
from nodes import BaseNode, SingleItemNode, DependencyNode
from cluster import ClusterBlueprint

import logging

log = logging.getLogger()

'''
    TODO
    the purpose of base cases is to return a cluster object that is ready for
    specific instance of testing/development/etc. instead of having the developer
    specify the note types, operations, etc.
'''


def dummyNodes(n):
    return [BaseNode(node_id=i) for i in range(n)]


def dummyOperationsAllocateCase(nodes):
    return {n.node_id: [operations.Op.Allocate] for n in nodes}


def dummyBlueprintCase0():
    """
    Base case containing 3 empty nodes without any production details
    """
    nodes = dummyNodes(3)
    return ClusterBlueprint(nodes)


def dummyBlueprintCase1():
    """
    Base case containing 3 nodes with basic production details
    """
    nodes = dummyNodes(3)
    ops = dummyOperationsAllocateCase(nodes)
    return ClusterBlueprint(nodes, ops)


def fiveDummyItemNodes():
    """
    Creating 5 itemnodes that have the following dependencies
       |-> 1 -> |
    0--|-> 2 -> | -> 4 -> |   
       |-> 3------------> | -> 5 

    """
    itemnodes = []
    itemnodes.append(DependencyNode(node_id=0, dependency=[]))
    itemnodes.append(DependencyNode(node_id=1, dependency=[0]))
    itemnodes.append(DependencyNode(node_id=2, dependency=[0]))
    itemnodes.append(DependencyNode(node_id=3, dependency=[0]))
    itemnodes.append(DependencyNode(node_id=4, dependency=[1, 2]))
    itemnodes.append(DependencyNode(node_id=5, dependency=[3, 4]))
    return itemnodes


def bootstrap_dependencies_three_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> 1 -> 2
    """
    demo_nodes = [
        SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(3)
    ]

    wood = items.ItemReq(items.Item('wood', 0), 1)
    door = items.ItemReq(items.Item('door', 1), 1)
    house = items.ItemReq(items.Item('house', 2), 1)

    demo_nodes[0].dependency = items.ItemDependency([], wood)
    demo_nodes[1].dependency = items.ItemDependency([wood], door)
    demo_nodes[2].dependency = items.ItemDependency([door], house)

    return demo_nodes


def bootstrap_dependencies_five_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> | ->  1 -----> | -> 3 -> | -> 4 -> | -> 5
           ->  2 -> |-> |         |
                 -> |-----------> |
    """
    demo_nodes = [
        SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(6)
    ]

    start = items.ItemReq(items.Item('start', 0), 1)
    wood = items.ItemReq(items.Item('wood', 1), 1)  # There is always only one node starting the whole graph!
    timber = items.ItemReq(items.Item('timber', 2), 1)
    premium_timber = items.ItemReq(items.Item('premium_timber', 3), 1)
    door = items.ItemReq(items.Item('door', 4), 1)
    house = items.ItemReq(items.Item('house', 5), 1)

    demo_nodes[0].dependency = items.ItemDependency([], start)
    demo_nodes[1].dependency = items.ItemDependency([start], wood)
    demo_nodes[2].dependency = items.ItemDependency([start], timber)
    demo_nodes[3].dependency = items.ItemDependency([wood, timber], premium_timber)
    demo_nodes[4].dependency = items.ItemDependency([timber, premium_timber], door)
    demo_nodes[5].dependency = items.ItemDependency([door], house)

    return demo_nodes


def dummyBlueprintCase2():
    """
    Creating ClusterBlueprint for 5 itemnodes defined in fiveDummyItemNodes()
    """
    itemnodes = fiveDummyItemNodes()
    ops = dummyOperationsAllocateCase(itemnodes)
    return ClusterBlueprint(itemnodes, ops)


def createDependencyGraph_BlueprintCase2():
    """
    Creating a graph with all the possible connections
    """
    graph = defaultdict(list) 
    blueprint = dummyBlueprintCase2()
    for node in blueprint.nodes:
        for dep in node.dependency:
            graph_funcs.addEdge(graph, dep, node.node_id)
    return graph, blueprint


def createFlowGraphAllPaths_BlueprintCase2():
    graph, blueprint = createDependencyGraph_BlueprintCase2()
    return graph_funcs.find_all_paths(graph, blueprint.nodes[0].node_id, blueprint.nodes[len(blueprint.nodes)-1].node_id)


def createFlowGraphShortestPaths_BlueprintCase2():
    graph, blueprint = createDependencyGraph_BlueprintCase2()
    return graph_funcs.find_shortest_path(graph, blueprint.nodes[0].node_id, blueprint.nodes[len(blueprint.nodes)-1].node_id)


# TODO: Remove testing from this class, otherwise let's use unittest for this

if __name__ == "__main__":
    graph, blueprint = createDependencyGraph_BlueprintCase2()
    
    print("Printing nodes in cluster blueprint")
    print(blueprint.nodes)

    print("Printing all edges in graph -- Dependency Graph")
    print(graph_funcs.generate_edges(graph))

    print("Printing all paths in graph from first to last node -- Flow Graph V1")
    print(createFlowGraphAllPaths_BlueprintCase2())

    print("Printing shortest paths in graph from first to last node -- Flow Graph V2")
    print(createFlowGraphShortestPaths_BlueprintCase2())
