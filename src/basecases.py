import operations
import items
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
        SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(3)
    ]

    wood = items.ItemReq(items.Item('wood', 0), 1)
    door = items.ItemReq(items.Item('door', 1), 1)
    house = items.ItemReq(items.Item('house', 2), 1)

    demo_nodes[0].dependency = items.ItemDependency([], wood)
    demo_nodes[1].dependency = items.ItemDependency([wood], door)
    demo_nodes[2].dependency = items.ItemDependency([door], house)

    return demo_nodes


def bootstrap_dependencies_six_nodes():
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

def bootstrap_dependencies_six_nodes_node_death():
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
    #demo_nodes[2].dependency = items.ItemDependency([start], timber)
    demo_nodes[3].dependency = items.ItemDependency([wood, timber], premium_timber)
    demo_nodes[4].dependency = items.ItemDependency([timber, premium_timber], door)
    demo_nodes[5].dependency = items.ItemDependency([door], house)

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
        SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(7)
    ]

    start = items.ItemReq(items.Item('start', 0), 1)
    wood = items.ItemReq(items.Item('wood', 1), 1) 
    screws = items.ItemReq(items.Item('screws', 2), 1)
    awesomeness = items.ItemReq(items.Item('awesomeness', 3), 1)
    
    demo_nodes[0].dependency = items.ItemDependency([], start)
    demo_nodes[1].dependency = items.ItemDependency([start], wood)
    demo_nodes[2].dependency = items.ItemDependency([start], wood)
    demo_nodes[3].dependency = items.ItemDependency([start], wood)
    demo_nodes[4].dependency = items.ItemDependency([wood], screws)
    demo_nodes[5].dependency = items.ItemDependency([wood], screws)
    demo_nodes[6].dependency = items.ItemDependency([screws], awesomeness)

    return demo_nodes

# Problems with the algorithm -> very sparse because only one path
# def bootstrap_random(nodes, edges, max, number_dependencies):
#     graph = random_dag(nodes, edges)
#     print(graph.edges())
#     demo_nodes = [
#         SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(nodes)
#     ]

#     id = ""

#     demo_nodes[0].dependency = items.ItemDependency([], items.ItemReq(items.Item(0, id), 1))
#     demo_nodes[1].dependency = items.ItemDependency([items.ItemReq(items.Item(0, id), 1)], items.ItemReq(items.Item(1, id), 1))
#     demo_nodes[2].dependency = items.ItemDependency([items.ItemReq(items.Item(0, id), 1)], items.ItemReq(items.Item(2, id), 1))

#     end_node_dependency = []
#     for i in range(number_dependencies):
#         end_node_dependency.append(items.ItemReq(items.Item(max-2-i, id), 1))

#     demo_nodes[nodes-1].dependency = items.ItemDependency(end_node_dependency, items.ItemReq(items.Item(max-1, id), 1))

#     for i in range(3, nodes-1):
#         rdm_start = []
#         rdm_start_type = []

#         for j in range(random.randint(1, number_dependencies)):
#             rdm_i = random.randint(1, max-2)
#             # Make sure all types in rdm_start are distinct
#             while rdm_i in rdm_start_type:
#                 rdm_i = random.randint(1, max-2)
#             rdm_start_type.append(rdm_i)
#             rdm_start.append(items.ItemReq(items.Item(rdm_i, id), 1))

#         rdm_end = random.randint(1, max-1) 
#         # Make sure type in output is different from each input        
#         while rdm_end in rdm_start_type:
#                 rdm_end = random.randint(1, max-2)
#         demo_nodes[i].dependency = items.ItemDependency(rdm_start, items.ItemReq(items.Item(rdm_end, id), 1))

#     return demo_nodes 

# Creates Random DAG!
def bootstrap_random_dag(nodes_num, edges_num):
    
    # Create random dag, using helper function
    graph = random_dag(nodes_num-2, edges_num)
    
    # There is one start_node (id=0) and one end_node (id = nodes_num-1)
    # Find als start & end nodes in graph and point them to the new start or end_node
    node_list = set(range(1, nodes_num-1)) # set with all node_ids in graph
    graph_list_end = set() 
    graph_list_start = set() 
    for edge in graph.edges:
        graph_list_end.add(edge[0])
        graph_list_start.add(edge[1])
    end_nodes = list(node_list.difference(graph_list_end)) # list with all node_ids without outgoing edge
    start_nodes = list(node_list.difference(graph_list_start)) # list with all node_ids without incoming_edge

    # Create nodes_num demo_nodes
    demo_nodes = [
        SingleItemNode(node_id=i, dependency=items.ItemDependency([], "")) for i in range(nodes_num)
    ]

    id = 0 # dummy_id
    
    for nodes in demo_nodes:
        # if node_id == 0, no incoming dependencies
        if nodes.node_id == 0:
            nodes.dependency = items.ItemDependency([], items.ItemReq(items.Item(nodes.node_id, id), 1))
        # if node_id in start_nodes, incoming dependency is node_id == 0   
        elif nodes.node_id in start_nodes:
            nodes.dependency = items.ItemDependency([items.ItemReq(items.Item(0, id), 1)], items.ItemReq(items.Item(nodes.node_id, id), 1))
        # if node_id == nodes_num-1, incoming dependency all node_ids in end_nodes
        elif nodes.node_id == nodes_num-1:
            node_dependency = []
            for end_node in end_nodes:
                node_dependency.append(items.ItemReq(items.Item(end_node, id), 1))
            nodes.dependency = items.ItemDependency(node_dependency, items.ItemReq(items.Item(nodes_num-1, id), 1))
        # add all other dependencies according to the random dag that was created
        else:
            node_dependency = []
            for tup in graph.edges():
                if tup[1] == nodes.node_id:
                    node_dependency.append(items.ItemReq(items.Item(tup[0], id), 1))
            nodes.dependency = items.ItemDependency(node_dependency, items.ItemReq(items.Item(nodes.node_id, id), 1))

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

