import operations
from items import Item, ItemReq, ItemDependency

from nodes import BaseNode, SingleItemNode
from cluster import ClusterBlueprint, Cluster

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
    return {n.node_id: [operations.Op.TriggerAllocate] for n in nodes}


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

def get_2_node_single_items_cluster():
    '''
        Returns a single 2 node cluster with one edge between nodes:
            node-0 -> node-1

        - node-0 supplies 1 window-type-y to node-1.
        - node-1 creates 1 door-type-z.

        Used to test SC stage.
    '''

    # define node 1 and it's deps
    input_materials = set() # no inputs to node-0
    result_materials = ItemReq(item=Item(type="window-type-y", id=""), quantity=1)
    node_zero_deps = ItemDependency(input_item_reqs=input_materials, result_item_req=result_materials)
    node_zero = SingleItemNode(node_id=0, dependency=node_zero_deps)

    # define node 2 and it's deps
    input_materials = set([
        ItemReq(item=Item(type="window-type-y", id=""), quantity=1)
    ])
    result_materials = ItemReq(item=Item(type="door-type-z", id=""), quantity=1)
    node_one_deps = ItemDependency(input_item_reqs=input_materials, result_item_req=result_materials)
    node_one = SingleItemNode(node_id=1, dependency=node_one_deps)

    # define per node bootstrap ops with cluster blueprint
    # i.e. no bootstrap ops are run in the nodes
    b = ClusterBlueprint(nodes=[node_zero, node_one])
    cluster = Cluster(b)  # define cluster using blueprint

    # TODO
    # implement a cluster.start() function.
    # After which this method will return the cluster object and
    # the caller can start/stop the cluster as needed.

    return cluster

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
    awesomeness = ItemReq(Item('awesomeness', 3), 1)

    demo_nodes[0].dependency = ItemDependency([], start)
    demo_nodes[1].dependency = ItemDependency([start], wood)
    demo_nodes[2].dependency = ItemDependency([start], wood)
    demo_nodes[3].dependency = ItemDependency([start], wood)
    demo_nodes[4].dependency = ItemDependency([wood], screws)
    demo_nodes[5].dependency = ItemDependency([wood], screws)
    demo_nodes[6].dependency = ItemDependency([screws], awesomeness)

    return demo_nodes
