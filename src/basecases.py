import testUtils

from nodes import BaseNode, ClusterBlueprint


def dummyNodes(n):
    return [BaseNode({'node_id': i}) for i in range(n)]


def dummyOperationsAllocateCase(nodes):
    return {n.node_id: [testUtils.Op.Allocate] for n in nodes}


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


