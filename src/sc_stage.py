from threading import Thread, Event
from queue import Queue, Empty
from time import sleep
import logging
from string import ascii_uppercase, digits
from random import choice
from os.path import abspath

from items import Item, ItemDependency
from file_dict import FileDict

log = logging.getLogger()

class SuppyChainStage(Thread):

    '''
        SuppyChainStage (SCG) implements the business logic needed
        by the production stage. Each node maintains a SuppyChainStage that
        is given a stream of parts/items that get converted into a stream of
        outputs.

        i.e. SCG mocks a physical production stage that consumes and creates
        products like a stage in a factory would.
    '''
    IN_QUEUE_STAGE = "in-queue"
    DELIVERED_STAGE = "delivered"
    CONSUMED_STAGE = "consumed"

    def __init__(self, name, item_dependency: ItemDependency, time_per_batch=1):
        '''
            name: debugging purposes only.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_batch: time in seconds it takes to make one unit.
        '''
        super(SuppyChainStage, self).__init__()
        self.name = "sc-stage-{}".format(name)
        self.item_dep = item_dependency
        self.inbound_material = Queue() if item_dependency else None
        self.outbound_material = Queue()
        self.time_per_batch = time_per_batch

        self.inbound_log = FileDict(abspath("./tmp/" + self.name + ".inbound.log"))
        self.outbound_log = FileDict(abspath("./tmp/" + self.name + ".outbound.log"))

        # hack to stop stage
        self.running = Event()
        self.running.set() # set the stage to run by default

        self.manufacture_count = 0
        self._attempt_log_recovery()

    def _attempt_log_recovery(self):
        '''
            attempts to populate the in-memory data structures from
            data in the disk log if there is any.

            uses raftos

            The log is unique to the stage using the stage-name as the key.

            TODO
        '''
        for item, state in self.inbound_log.items():
            if state == self.IN_QUEUE_STAGE:
                self.inbound_material.put(item)

        for item, state in self.outbound_log.items():
            if state == self.IN_QUEUE_STAGE:
                self.outbound_material.put(item)
            elif state == self.DELIVERED_STAGE:
                self.manufacture_count += 1

        return

    def stop(self):
        '''
            Stop the stage's loop. used for testing.
        '''
        # stop the production loop
        self.running.clear()
        # flush & invalidate the queues
        self.inbound_material = self.outbound_material = None
        # leave the logs for the next stage instance with the same
        # name to pick up

    def clear_logs(self):
        '''
            used for testing
        '''
        self.inbound_log.clear()
        self.outbound_log.clear()


    def get_outbound_queue(self):
        return self.outbound_material

    def get_stage_result_type(self):
        return self.item_dep.result_item_req.item.type

    def get_manufacture_count(self):
        '''
            returns the count of items produced by the stage since the
            first time the stage was created.
        '''
        return self.manufacture_count

    def get_inbound_waiting_items_count(self):
        return self.inbound_material.qsize()

    def get_outbound_waiting_items_count(self):
        return self.outbound_material.qsize()

    def accept_material(self, material: Item):
        '''
            is a function called as a callback by the node-process
            when it receives material from an inbound edge/node.
        '''
        if self.item_dep.is_valid_material(material):
            self.inbound_log[material] = self.IN_QUEUE_STAGE
            self.inbound_material.put(material)
            return True

        return False

    def _generate_new_item_id(self):
        return ''.join(choice(ascii_uppercase) for _ in range(5)) + \
            ''.join(choice(digits) for _ in range(3))

    def mark_item_delivered(self, item: Item):
        '''
            callback invoked by the node to mark
            an result item delivered to a downstream
            node
        '''
        self.outbound_log[item] = self.DELIVERED_STAGE


    def manufacture_batch_and_enqueue(self):
        '''
            TODO
            logic to poll/query/update the inbound queue until it can make one unit of
            the output using the right quantities by reffering to the item_dep.

            This is a blocking call since it has to wait on the inbound queue.
        '''
        new_item_id = self.get_stage_result_type() + '-' + self._generate_new_item_id()


        try:
            # TODO deplete only when there is enough material to produce the result item
            material = self.inbound_material.get_nowait()
            self.inbound_log[material] = self.CONSUMED_STAGE
        except Empty:
            # queue is empty, need to wait till it's not.
            pass

        # TODO add to outbound only when the inbound queue has been pop()'d correctly
        new_item = Item(type=self.get_stage_result_type(), id=new_item_id)
        self.outbound_log[new_item] = self.IN_QUEUE_STAGE
        self.outbound_material.put(new_item)
        self.manufacture_count += 1

        return


    def run(self):

        while self.running.is_set():

            self.manufacture_batch_and_enqueue()
            sleep(self.time_per_batch)
