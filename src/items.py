import logging

from typing import List
from copy import deepcopy


log = logging.getLogger()


# Structure for item: Each item has a name and id
class Item:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __repr__(self):
        return "{}-{}".format(self.name, self.id)


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

    def __init__(self, input_item_reqs: List[ItemReq], result_item_req: ItemReq):
        """
            input_item_reqs: List of input items required (Can be empty for source node)
            result_item_req: end item produced
        """
        self.result_item_req = result_item_req
        self.input_item_reqs = input_item_reqs

    def __repr__(self):
        return "{}->{}".format(self.input_item_reqs, self.result_item_req)
