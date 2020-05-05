import operations

from nodes import BaseNode
from cluster import ClusterBlueprint

'''
    TODO
    the purpose of base cases is to return a cluster object that is ready for
    specific instance of testing/development/etc. instead of having the developer
    specify the note types, operations, etc.
'''

def dummyNodes(n):
    return [BaseNode({'node_id': i}) for i in range(n)]


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
