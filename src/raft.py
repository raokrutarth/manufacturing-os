import raftos
import logging
import jsonpickle
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

    # NOTE:
    # the ports passed in __init__ are used by the zmq protocols.
    # Need to give raftos different ports to operate on.
    # Should verify the raftos ports do not overlap with
    # zmq ports.
    PORT_OFFSET = -50

    def __init__(self, node_process, cluster):
        # extract addresses of other nodes in the cluster
        self.cluster = [
            "127.0.0.1:%d" % (port_spec.port + self.PORT_OFFSET)
            for port_spec in cluster.process_specs.values() if port_spec.port != node_process.port
        ]
        self.node_address = "127.0.0.1:%d" % (node_process.port + self.PORT_OFFSET)
        self.nodes = cluster.nodes
        self.node_id = node_process.node.node_id

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

        log.info("Registered node with address %s in raft cluster %s",
                  self.node_address, self.cluster)

        # Create replicated dict which can contain different items we want shared amongst nodes
        # Dict-like object: data.update(), data['key'] etc
        self.cluster_flow = raftos.Replicated(name='cluster_flow')

    async def _get_leader(self):
        '''
            returns the leader of the raftos cluster. Is a blocking call
        '''
        log.debug("Node %s waiting for leader election to complete", self.node_address)
        await raftos.State.wait_for_election_success()
        leader = raftos.get_leader()
        log.debug("Node %s detected %s as leader node",
            self.node_address, leader)
        return leader

    async def am_i_leader(self):
        leader = await self._get_leader()
        return leader == self.node_address

    async def init_flow(self):
        '''
            Registers a replicated raftos collection and sets initial values
            for the initial flow state of the supplychain.
        '''
        is_leader = await self.am_i_leader()
        if is_leader:
            cluster_flow_obj = ctr.bootstrap_shortest_path(self.nodes)            
            log.debug("Starting to init cluster flow: {} on leader: {}".format(self.node_address, cluster_flow_obj))
            self.cluster_flow = raftos.Replicated(name='cluster_flow')
            await self.cluster_flow.set(cluster_flow_obj)
            log.info("Finished init cluster flow on leader: {}".format(self.node_address))

    async def update_flow(self, new_cluster_flow: ctr.ClusterWideFlow):
        """
            Utility to persist flow used by leader
        """
        is_leader = await self.am_i_leader()
        if is_leader:
            await self.cluster_flow.set(new_cluster_flow)
            return True
        return False

    async def get_flow(self):
        flow = await self.cluster_flow.get()
        return flow

    def __repr__(self):
        return str({
            'RaftHelper': {
                "node ID": self.node_id,
                "Raft Node address": self.node_address,
                "Raft cluster": self.cluster,
                # TODO add flow and nodes if necessary
            }
        })
