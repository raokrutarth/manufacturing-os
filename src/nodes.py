"""
- Base Case Blueprint class to represent all nodes and their types in the graph
    - Node:
        - Represents details for each node
        - Contains the item id that it produces, along with quantity (float/int)
        - Contains the input items required to produce that quantity
    - Blueprint:
        - Set of all nodes
        - Consists of some operations which need to be done by each node eventually
    - Execution flags:
        - Store the information of which algorithms to use
        - Dictionary - easiest to implement for now
    - Standard factory methods:
        - Provide templates for common base cases
"""

from typing import List
from utils import ProcessSpec
from collections import namedtuple


# Structure for item: Each item has a name and id
Item = namedtuple('Item', ['name', 'id'])
# Item requirement - Item, Quantity
ItemReq = namedtuple('ItemReq', ['item', 'quantity'])


class ItemDependency(object):

    def __init__(self, input_item_reqs: List[ItemReq], result_item_req: ItemReq):
        """
            input_item_reqs: List of input items required (Can be empty for source node)
            result_item_req: End item produced
        """
        self.result_item_req = result_item_req
        self.input_item_reqs = input_item_reqs

    def __repr__(self):
        return "{}->{}".format(self.input_item_reqs, self.result_item_req)


class BaseNode(object):

    def __init__(self, args):
        self.node_id = args["node_id"]

    def __repr__(self):
        return str(self.node_id)


class SingleItemNode(BaseNode):
    """
    Implementation of single item node. Each node can produce only one type of item.
        - Contains the item id that it produces, along with quantity (float/int)
        - Contains the input items required to produce that quantity
    """

    def __init__(self, args):
        super(SingleItemNode, self).__init__(args)
        self.dependency = args["dependency"]

    def __repr__(self):
        return "{}::{}".format(self.node_id, self.dependency)


class ClusterBlueprint(object):
    """
    Represents the cluster blueprint to create Clusters from
    Useful for unit tests and designing test cases we want to operate on.
    """

    def __init__(self, nodes: List[BaseNode]):
        # Set of nodes to be used by this cluster
        self.nodes = nodes
        # Stores any node specific operations we want to perform during execution e.g.
        # injecting node specific random failures, delays, etc
        self.node_specific_ops = {}
        # Stores the flags and options we'd be using finally in our setup
        self.flags = {}


class Cluster(object):
    """
    Represents the set of nodes interacting
    """

    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.nodes = self.blueprint.nodes
        self.process_specs = None
        self.init_process_specs()

    def init_process_specs(self):
        self.process_specs = [ProcessSpec('node{}'.format(i), 5000 + i) for i in range(len(self.nodes))]

    def __repr__(self):
        return 'Nodes: {}; ProcessSpecs: {}'.format(self.nodes, self.process_specs)
