from typing import List
from collections import namedtuple
import logging

log = logging.getLogger()


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
        return "{} -> {}".format(self.input_item_reqs, self.result_item_req)
