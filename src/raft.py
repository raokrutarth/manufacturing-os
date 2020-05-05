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

    async def add_outgoing_edge(self, receiver):
        '''
            Adds an edge in the distributed graph from the
            caller node to the receiver. receiver is a string
            with ip address and port.
            e.g. 127.0.0.1:433
        '''
        log.debug("adding edge from %s to %s", self.node_address, receiver)
        existing_edges = self.graph.get()[self.node_address]
        if not existing_edges:
            edges = {
                self.node_address: set(receiver)
            }
        else:
            edges = {
                self.node_address: existing_edges.add(receiver)
            }

        await self.graph.update(edges)

    async def remove_outgoing_edge(self, receiver):
        '''
            Adds an edge in the distributed graph from the
            caller node to the receiver
        '''
        log.debug("removing edge from %s to %s", self.node_address, receiver)
        existing_edges = self.graph.get()[self.node_address]
        if not existing_edges:
            return
        else:
            edges = {
                self.node_address: existing_edges.remove(receiver)
            }

        await self.graph.update(edges)

