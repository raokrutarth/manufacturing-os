import logging

from typing import Set
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

    def __init__(self, input_item_reqs: Set[ItemReq], result_item_req: ItemReq):
        """
            input_item_reqs: List of input items required (Can be empty for source node)
            result_item_req: End item produced
        """
        self.result_item_req = result_item_req
        self.input_item_reqs = input_item_reqs

    def is_valid_material(self, new_item: Item):
        '''
            TODO
            return true if new_item is a valid raw material to produce
            self.result_item_req type items
        '''
        return new_item in self.input_item_reqs

    def __repr__(self):
        return "{} -> {}".format(self.input_item_reqs, self.result_item_req)
