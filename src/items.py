import logging

from typing import Set
from collections import namedtuple, defaultdict

log = logging.getLogger()


'''
    Item represents a single indivisible production unit.
    type: there can be many units of the same type. e.g. blue-door
    id: unique to the specific instance of the item. e.g. YHG87
        there can only be one item per id and given type
'''
Item = namedtuple('Item', ['type', 'id'])

# Item requirement - item: Item, quantity: int
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
            result_item_req: end item produced
        """
        self.result_item_req = result_item_req
        self.input_item_reqs = input_item_reqs

    def is_valid_material(self, new_item: Item):
        '''
            TODO
            return true if new_item is a valid raw material to produce
            self.result_item_req type items
        '''
        for item_req in self.input_item_reqs:
            if new_item.type == item_req.item.type:
                # NOTE:
                # quantity is not being checked
                return True
        return False

    def can_make_result(self, materials: Set[Item]):
        '''
            returns true if the materials can make the
            result
        '''
        needed = defaultdict(int)
        for item in self.input_item_reqs:
            needed[item.type] = item.quantity

        for item in materials:
            needed[item.type] -= 1

        for remaining_count in needed.values():
            if remaining_count > 0:
                return False
        return True


    def __repr__(self):
        return "{} -> {}".format(self.input_item_reqs, self.result_item_req)
