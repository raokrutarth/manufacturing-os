import asyncio
import raftos
import logging
from os.path import abspath

import graph_funcs

log = logging.getLogger()

LEADER_WAL_DIR = abspath("./tmp")
GRAPH_NAME = 'sc_graph'

class RaftHelper():
    def __init__(self, node, cluster):
        self.graph = None
        self.node = node

        # extract addresses of other nodes in the cluster
        self.cluster = [
            "127.0.0.1:%d" % (port_spec.port) \
                for port_spec in cluster.process_specs \
                    if port_spec.port != node.port
        ]
        self.node_address = "127.0.0.1:%d" % node.port

    async def register_node(self):
        '''
            Adds the node with node ID = node_id to the raftos
            based cluster.
            FIXME:
                node_id has to be an integer in the range [0, len(cluster.process_specs))
        '''
        log.debug("registering node with port %s in cluster %s with raft helper",
            self.node_address, self.cluster)

        raftos.configure({
            'log_path': LEADER_WAL_DIR,
            'serializer': raftos.serializers.JSONSerializer,
        })

        await raftos.register(self.node_address, cluster=self.cluster)

        # Dict-like object: data.update(), data['key'] etc
        self.graph = raftos.ReplicatedDict(name=GRAPH_NAME)

    async def request_leader_based_restructure(self, added_edges, deleted_edges):
        '''
            Each node can make a call to request_leader_based_restructure to make the
            leader peform updates on the system state and modify the edges connected
            to the calling node.

            The function returns true when the calling node is the leader.
        '''
        if raftos.get_leader() == self.node_address:
            
            current_graph = await self.graph.get()
        
            # Adding edges
            # Check whether edges are not already connected
            for edge in added_edges:
                if edge not in current_graph[self.node.node_id]:
                    graph_funcs.addEdge(current_graph, self.node.node_id, edge)

            # Deleted edges
            # Check whether edges are connected
            for edge in deleted_edges:
                if edge not in current_graph[self.node.node_id]:
                    # TODO: Check whether without the edge a flow is still possible??? 
                    graph_funcs.deleteEdge(current_graph, self.node.node_id, edge)
                    
            # TODO: This only displays the dependency graph, i.e. the flow is not being created here. Where should we do that???
            await self.graph.update(current_graph)

            return True

        return False

