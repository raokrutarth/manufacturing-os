from nodes import BaseNode, ClusterBlueprint


def dummyNodes(n):
    return [BaseNode({'node_id': i}) for i in range(n)]


def dummyBlueprintCase0():
    """
    Base case containing 3 empty nodes without any production details
    """
    nodes = dummyNodes(3)
    return ClusterBlueprint(nodes)
