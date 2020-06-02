import operations
from items import Item, ItemReq, ItemDependency
from collections import defaultdict 
import random 
import networkx as nx

import graph_funcs
from nodes import BaseNode, SingleItemNode, DependencyNode

import logging

log = logging.getLogger()

'''
    TODO
    the purpose of base cases is to return a cluster object that is ready for
    specific instance of testing/development/etc. instead of having the developer
    specify the note types, operations, etc.
'''

def bootstrap_dependencies_three_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> 1 -> 2
    """
    demo_nodes = [
        SingleItemNode(node_id=i, dependency=ItemDependency([], "")) for i in range(3)
    ]

    wood = ItemReq(Item('wood', None), 1)
    door = ItemReq(Item('door', None), 1)
    house = ItemReq(Item('house', None), 1)

    demo_nodes[0].dependency = ItemDependency([], wood)
    demo_nodes[1].dependency = ItemDependency([wood], door)
    demo_nodes[2].dependency = ItemDependency([door], house)

    return demo_nodes


def bootstrap_dependencies_six_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> | ->  1 -----> | -> 3 -> | -> 4 -> | -> 5
           ->  2 -> |-> |         |
                 -> |-----------> |
    """
    demo_nodes = [
        SingleItemNode(node_id=i, dependency=ItemDependency([], "")) for i in range(6)
    ]

    start = ItemReq(Item('start', None), 1)
    wood = ItemReq(Item('wood', None), 1)  # There is always only one node starting the whole graph!
    timber = ItemReq(Item('timber', None), 1)
    premium_timber = ItemReq(Item('premium_timber', None), 1)
    door = ItemReq(Item('door', None), 1)
    house = ItemReq(Item('house', None), 1)

    demo_nodes[0].dependency = ItemDependency([], start)
    demo_nodes[1].dependency = ItemDependency([start], wood)
    demo_nodes[2].dependency = ItemDependency([start], timber)
    demo_nodes[3].dependency = ItemDependency([wood, timber], premium_timber)
    demo_nodes[4].dependency = ItemDependency([timber, premium_timber], door)
    demo_nodes[5].dependency = ItemDependency([door], house)

    return demo_nodes

def bootstrap_dependencies_seven_nodes():
    """
    initialize demo_node with the following dependencies
    0 -> | 1 | 4 | -> 6
         | 2 | 5 |
         | 3 |
    """

    # All item reqs here involve 1 unit of product. So we have redundant sources of materials.

    demo_nodes = [
        SingleItemNode(node_id=i, dependency=ItemDependency([], "")) for i in range(7)
    ]

    start = ItemReq(Item('start', None), 1)
    wood = ItemReq(Item('wood', None), 1) 
    screws = ItemReq(Item('screws', None), 1)
    awesomeness = ItemReq(Item('awesomeness', None), 1)
    
    demo_nodes[0].dependency = ItemDependency([], start)
    demo_nodes[1].dependency = ItemDependency([start], wood)
    demo_nodes[2].dependency = ItemDependency([start], wood)
    demo_nodes[3].dependency = ItemDependency([start], wood)
    demo_nodes[4].dependency = ItemDependency([wood], screws)
    demo_nodes[5].dependency = ItemDependency([wood], screws)
    demo_nodes[6].dependency = ItemDependency([screws], awesomeness)

    return demo_nodes

# Creates Random DAG!
def bootstrap_random_dag(type_num=4, complexity="low", nodes_per_type=2):
    '''
    input:
    type_num        = number of different item types that the whole cluster has
    complexity      = "low", "medium" or "high" indiciating how complex the DAG, i.e. how many edges it has!
    nodes_per_type  = maximum number of nodes one type can have  

    output: nodes that form a random DAG
    '''
    log.info("Creating random DAG with %d types of items, with max. %d nodes per type and cluster complexity %s", type_num, nodes_per_type, complexity)

    if type_num < 4:
        type_num = 4
    
    edges_num = 0

    if complexity == "low":
        edges_num = type_num - 2

    elif complexity == "medium":
        edges_num = int((type_num - 2) * ((type_num - 3) / 2) / 2 )
        if edges_num < 1:
            edges_num = 1

    elif complexity == "high":
        edges_num = int((type_num - 2) * (type_num - 3) / 2)


    # Create random dag, using helper function
    graph = random_dag(type_num-2, edges_num)
    log.debug("Initial Random DAG without start and end node created: %s", graph)
    
    # There is one start_node (id=0) and one end_node (id = nodes_num-1)
    # Find als start & end nodes in graph and point them to the new start or end_node
    node_list = set(range(1, type_num-1)) # set with all node_ids in graph
    graph_list_end = set() 
    graph_list_start = set() 
    for edge in graph.edges:
        graph_list_end.add(edge[0])
        graph_list_start.add(edge[1])
    end_nodes = list(node_list.difference(graph_list_end)) # list with all node_ids without outgoing edge
    start_nodes = list(node_list.difference(graph_list_start)) # list with all node_ids without incoming_edge
    log.debug("The start node will point to all nodes in Random DAG without incoming edges: %s", start_nodes)
    log.debug("All nodes in Random DAG without outgoing edges %s will point to the end node", end_nodes)

    demo_nodes = []     # Create nodes_num demo_nodes

    for i in range(type_num):
        if i == 0:
            node_tmp = SingleItemNode(node_id=i, dependency=None)
            node_tmp.dependency = ItemDependency([], ItemReq(Item(i, None), 1))
            demo_nodes.append(node_tmp)

        elif i == type_num-1:
            node_tmp = SingleItemNode(node_id=i*nodes_per_type, dependency=None)
            node_tmp.dependency = ItemDependency([], ItemReq(Item(i, None), 1))
            demo_nodes.append(node_tmp)

        else:
            for j in range(1, random.randint(2, nodes_per_type)):
                node_tmp = SingleItemNode(node_id=i*j, dependency=None)
                node_tmp.dependency = ItemDependency([], ItemReq(Item(i, None), 1))
                demo_nodes.append(node_tmp)
    
    log.debug("Nodes created without any input requirements:  %s", demo_nodes)

    for nodes in demo_nodes:
        # if node_id == 0, no incoming dependencies
        if nodes.node_id == 0:
            pass
        # if node_id in start_nodes, incoming dependency is item type == 0   
        elif nodes.dependency.result_item_req.item.type in start_nodes:
            nodes.dependency.input_item_reqs = [ItemReq(Item(0, None), 1)]
        # if item type == type_num-1, incoming dependency all item types in variable end_nodes
        elif nodes.dependency.result_item_req.item.type == type_num-1:
            node_dependency = []
            for end_node in end_nodes:
                node_dependency.append(ItemReq(Item(end_node, None), 1))
            nodes.dependency.input_item_reqs = node_dependency
        # add all other dependencies according to the random dag that was created
        else:
            node_dependency = []
            for tup in graph.edges():
                if tup[1] == nodes.dependency.result_item_req.item.type:
                    node_dependency.append(ItemReq(Item(tup[0], None), 1))
            nodes.dependency.input_item_reqs = node_dependency

    log.info("Final nodes created:  %s", demo_nodes) 
    return demo_nodes

def random_dag(nodes, edges):
    """Generate a random Directed Acyclic Graph (DAG) with a given number of nodes and edges."""
    G = nx.DiGraph()
    for i in range(1, nodes+1):
        G.add_node(i)
    while edges > 0:
        a = random.randint(1,nodes)
        b=a
        while b==a:
            b = random.randint(1,nodes)
        G.add_edge(a,b)
        if nx.is_directed_acyclic_graph(G):
            edges -= 1
        else:
            # we closed a loop!
            G.remove_edge(a,b)
    return G

