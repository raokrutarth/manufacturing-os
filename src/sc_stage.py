from threading import Thread
from queue import Queue
from time import sleep
import logging

from items import Item, ItemDependency, ItemReq

log = logging.getLogger()

class SuppyChainStage(Thread):

    '''
        SuppyChainStage (SCG) implements the business logic needed
        by the production stage. Each node maintains a SuppyChainStage that
        is given a stream of parts/items that get converted into a stream of
        outputs.

        i.e. SCG mocks a physical production stage that consums and creates
        products like a stage in production would.
    '''

    def __init__(self, name, item_dependency: ItemDependency,
                time_per_unit=1, has_inbound=True, has_outbound=True):
        '''
            name: debugging purposes only.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_unit: time in seconds it takes to make one unit.
            has_inbound:  the stage has incoming raw materials in the supplychain.
                if not, it mocks an coming stream of raw materials it can
                consume. e.g. an aluminium plant.
            has_outbound: the stage has outbound edges. i.e if the resulting product of
                the stage is consumed by another stage. if not, the inventory
                count increases indefinitely.
        '''
        super(SuppyChainStage, self).__init__()
        self.name = "sc-stage-{}".format(name)
        self.item_dep = item_dependency
        self.has_inbound = has_inbound
        self.has_outbound = has_outbound
        self.inbound_material = Queue() if has_inbound else None
        self.outbound_material = Queue() if has_outbound else None
        self.time_per_unit = time_per_unit
        self.manufacture_count = 0

    def get_outbound_queue(self):
        return self.outbound_material

    def accept_material(self, material: Item):
        '''
            is a function called as a callback by the node-process
            when it receives material from an in inbound edge.
        '''
        if not self.item_dep.is_valid_material(material):
            return False
        if not self.has_inbound:
            log.error("Attempting to add material to stage %s " \
                "while stage is of non-inbound type", self.name)
            return False

        self.inbound_material.put(material)
        return True


    def send_product(self):
        '''
            TODO
            logic to poll/query/update the inbound queue until it can make one unit of
            the output using the right quantities by reffering to the item_dep
        '''
        # item <- created by material in self.inbound_queue
        new_item_name = "%s-%d" % (self.name, self.manufacture_count)

        self.inbound_material.get() # FIXME: Hack to deplete the inbound pipeline

        # TODO remove below with actual logic
        self.outbound_material.put(Item(name=new_item_name, id=hash(new_item_name)))
        self.manufacture_count += 1
        return


    def run(self):

        while True:
            self.send_product()
            sleep(self.time_per_unit)
