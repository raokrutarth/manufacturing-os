import asyncio
import raftos
import logging
import pickle, jsonpickle
import cluster as ctr

from os.path import abspath

log = logging.getLogger()

LEADER_WAL_DIR = abspath("./tmp")
GRAPH_NAME = 'sc_graph'


class ComplexJSONSerializer:
    @staticmethod
    def pack(data):
        return jsonpickle.dumps(data).encode()

    @staticmethod
    def unpack(data):
        decoded = data.decode() if isinstance(data, bytes) else data
        return jsonpickle.loads(decoded)


class RaftHelper(object):
    """
    Helper class abstracting out the underlying raftos configuration
    """

    def __init__(self, node, cluster):
        # extract addresses of other nodes in the cluster
        self.cluster = [
            "127.0.0.1:%d" % port_spec.port
            for port_spec in cluster.process_specs.values() if port_spec.port != node.port
        ]
        self.node_address = "127.0.0.1:%d" % node.port
        self.nodes = cluster.nodes

        self.cluster_flow = None

    async def register_node(self):
        '''
            Adds the node with node ID = node_id to the raftos
            based cluster.
        '''
        log.debug("registering node with port %s in cluster %s with raft helper",
                  self.node_address, self.cluster)

        raftos.configure({
            'log_path': LEADER_WAL_DIR,
            'serializer': ComplexJSONSerializer,
        })

        await raftos.register(self.node_address, cluster=self.cluster)

        log.debug("registering node with port %s in cluster %s with raft helper",
                  self.node_address, self.cluster)

        # Create replicated dict which can contain different items we want shared amongst nodes
        # Dict-like object: data.update(), data['key'] etc
        self.cluster_flow = raftos.Replicated(name='cluster_flow')

    @staticmethod
    def get_leader():
        return raftos.get_leader()

    async def init_flow(self):
        if raftos.get_leader() == self.node_address:
            cluster_flow_obj = ctr.ClusterWideFlow(nodes=self.nodes)
            log.debug("Starting to init cluster flow: {} on leader: {}".format(self.node_address, cluster_flow_obj))
            self.cluster_flow = raftos.Replicated(name='cluster_flow')
            await self.cluster_flow.set(cluster_flow_obj)
            log.debug("Finished init cluster flow on leader: {}".format(self.node_address))

    async def update_flow(self, new_cluster_flow: ctr.ClusterWideFlow):
        """
        Utility to persist flow used by leader
        """
        if raftos.get_leader() == self.node_address:
            await self.cluster_flow.set(new_cluster_flow)
            return True
        return False

    async def request_leader_based_restructure(self, updated_edges):
        '''
            Each node can make a call to request_leader_based_restructure to make the
            leader peform updates on the system state and modify the edges connected
            to the calling node.

            The function returns true when the calling node is the leader.
        '''
        if raftos.get_leader() == self.node_address:
            current_graph = await self.data.get()
            # TODO
            # logic to look at current graph and check if it can be modified,
            # adding edges to the graph, removing edges should be done/called from here.

            new_edges = {}  # REMOVE once TODO above is complete

            await self.data.update(new_edges)

            return True

        return False
