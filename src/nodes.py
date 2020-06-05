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

from items import ItemDependency
from collections import namedtuple
import enum

# Process Specification - port
ProcessSpec = namedtuple('ProcessSpec', ['name', 'port'])

class NodeState(enum.Enum):
    inactive = 0
    active = 1

class BaseNode(object):

    def __init__(self, node_id):
        self.node_id = node_id
        self.state = NodeState.active

    def __repr__(self):
        return "BaseNode(id:{})".format(self.node_id)

    def get_id(self):
        return self.node_id


class SingleItemNode(BaseNode):
    """
    Implementation of single item node. Each node can produce only one type of item.
        - Contains the item id that it produces, along with quantity (float/int)
        - Contains the input items required to produce that quantity
    """

    def __init__(self, node_id: int, dependency: ItemDependency):
        super(SingleItemNode, self).__init__(node_id)
        self.dependency = dependency

    def get_dependency(self):
        return self.dependency

    def __repr__(self):
        return "SingleItemNode(id: {}, deps: {})".format(self.node_id, self.dependency)


class DependencyNode(BaseNode):

    def __init__(self, node_id: int, dependency):
        super(DependencyNode, self).__init__(node_id)
        self.dependency = dependency

    def get_dependency(self):
        return self.dependency

    def __repr__(self):
        return "DependencyNode(id: {}, deps: {})".format(self.node_id, self.dependency)
