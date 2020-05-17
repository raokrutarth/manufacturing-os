import logging

from typing import Set
from copy import deepcopy
from collections import defaultdict

log = logging.getLogger()


class Item:
    '''
        Item represents a single indivisible production unit.
        type: there can be many units of the same type. e.g. blue-door
        id: unique to the specific instance of the item. e.g. YHG87
            there can only be one item per id and given type
    '''

    def __init__(self, type, id):
        self.type = type
        self.id = id

    def __repr__(self):
        return "{}-{}".format(self.type, self.id)


# Item requirement - Item, Quantity
class ItemReq:
    def __init__(self, item: Item, quantity):
        self.item = item
        self.quantity = quantity

    def __repr__(self):
        return "{}({})".format(self.item, self.quantity)


class ItemDependency(object):

    @classmethod
    def newNullDependency(cls):
        """
        returns a null item dependency i.e. [] -> []
        """
        return cls([], ItemReq(Item('null', -1), 0))

    @staticmethod
    def halveDependency(itemDep):
        """
        returns a halved item dependency where requirements are reduced
        """
        newItemDep = deepcopy(itemDep)
        for idx in range(len(newItemDep.input_item_reqs)):
            newItemDep.input_item_reqs[idx].quantity //= 2
        return newItemDep

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
        return "{}->{}".format(self.input_item_reqs, self.result_item_req)
