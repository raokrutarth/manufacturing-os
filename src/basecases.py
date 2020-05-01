from nodes import BaseNode, ClusterBlueprint


def dummyNodes(n):
    return [BaseNode({'node_id': i}) for i in range(n)]


def dummyBlueprintCase(n):
    """
    Base case containing n empty nodes without any production details
    """
    nodes = dummyNodes(n)
    return ClusterBlueprint(nodes)


def dummySendMessagesToEveryone(n):
    """
    Base case containing n empty nodes without any production details and sending messages to each node
    """
    blueprint = dummyBlueprintCase(n)
    cluster = nodes.Cluster(blueprint)

    for node in self.cluster.nodes:
            node.process = Process(target=processes.SocketBasedNodeProcess, args=(node, self.cluster)).start()
    
    # TODO: Implement Sending Logic
