import asyncio
import raftos
import logging
from os.path import abspath

log = logging.getLogger()

LEADER_WAL_DIR = abspath("./tmp")
GRAPH_NAME = 'sc_graph'


class RaftHelper():
    def __init__(self, node, cluster):
        self.graph = None

        # extract addresses of other nodes in the cluster
        self.cluster = [
            "127.0.0.1:%d" % port_spec.port \
                for port_spec in cluster.process_specs.values() if port_spec.port != node.port
        ]
        self.node_address = "127.0.0.1:%d" % node.port

    async def register_node(self):
        '''
            Adds the node with node ID = node_id to the raftos
            based cluster.
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

    async def request_leader_based_restructure(self, updated_edges):
        '''
            Each node can make a call to request_leader_based_restructure to make the
            leader peform updates on the system state and modify the edges connected
            to the calling node.

            The function returns true when the calling node is the leader.
        '''
        if raftos.get_leader() == self.node_address:
            current_graph = await self.graph.get()
            # TODO
            # logic to look at current graph and check if it can be modified,
            # adding edges to the graph, removing edges should be done/called from here.

            new_edges = {} # REMOVE once TODO above is complete

            await self.graph.update(new_edges)

            return True

        return False

