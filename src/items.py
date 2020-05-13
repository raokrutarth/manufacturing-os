import logging

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
        return cls([], [ItemReq(Item('null', -1), 0)])

    def __init__(self, input_item_reqs: List[ItemReq], result_item_reqs: List[ItemReq]):
        """
            input_item_reqs: List of input items required (Can be empty for source node)
            result_item_req: List of end items produced (can be one or many)
        """
        self.result_item_reqs = result_item_reqs
        self.input_item_reqs = input_item_reqs

    def __repr__(self):
        return "{} -> {}".format(self.input_item_reqs, self.result_item_reqs)
