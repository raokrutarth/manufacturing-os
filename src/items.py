import logging
import nodes as nd

from typing import List
from collections import namedtuple

log = logging.getLogger()


# Structure for item: Each item has a name and id
Item = namedtuple('Item', ['name', 'id'])
# Item requirement - Item, Quantity
ItemReq = namedtuple('ItemReq', ['item', 'quantity'])


class ItemDependency(object):

    @classmethod
    def newNullDependency(cls):
        """
        returns a null item dependency i.e. [] -> []
        """
        return cls([], ItemReq(Item('null', -1), 0))

    def __init__(self, input_item_reqs: List[ItemReq], result_item_req: ItemReq):
        """
            input_item_reqs: List of input items required (Can be empty for source node)
            result_item_req: End item produced
        """
        self.result_item_req = result_item_req
        self.input_item_reqs = input_item_reqs

    def __repr__(self):
        return "{} -> {}".format(self.input_item_reqs, self.result_item_req)


class ClusterWideFlow(object):
    """
    Object storing details of the cluster wide flow
    All nodes should interact e.g. get requests through this interface
    """

    def __init__(self, nodes: List[nd.BaseNode]):
        self.node_ids = [n.node_id for n in nodes]
        self.outgoing_flows = {n: [] for n in self.node_ids}
        self.incoming_flows = {n: [] for n in self.node_ids}

    def addNode(self, node_id):
        if node_id not in self.node_ids:
            self.node_ids.append(node_id)
            self.outgoing_flows[node_id] = []
            self.incoming_flows[node_id] = []

    def addFlow(self, source, dst, item: ItemReq):
        assert (source in self.node_ids) and (dst in self.node_ids), "Source: {}, Dst: {}".format(source, dst)
        self.outgoing_flows[source].append((dst, item))
        self.incoming_flows[dst].append((source, item))

    def getOutgoingFlowsForNode(self, node_id):
        """
        Outgoing flows i.e. nodes to which node_id is supposed to give items
        """
        return self.outgoing_flows[node_id]

    def getIncomingFlowsForNode(self, node_id):
        """
        Incoming flows i.e. nodes from which node_id is supposed to recieve items
        """
        return self.incoming_flows[node_id]

    def clearAll(self):
        self.node_ids = []
        self.outgoing_flows = {}
        self.incoming_flows = {}

    def __repr__(self):
        return "{}".format(self.outgoing_flows)
