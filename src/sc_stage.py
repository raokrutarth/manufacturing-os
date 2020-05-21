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

class StageStatus():
    IN_QUEUE = "in-queue"  # ready to be consumed or sent
    DELIVERED = "delivered"  # item was delivered downstream
    CONSUMED = "consumed"  # item was consumed in present node
    IN_TRANSIT = "in-transit"

class SuppyChainStage(Thread):

    '''
        SuppyChainStage (SCG) implements the business logic needed
        by the production stage. Each node maintains a SuppyChainStage that
        is given a stream of parts/items that get converted into a stream of
        outputs.

        i.e. SCG mocks a physical production stage that consumes and creates
        products like a stage in a factory would.
    '''


    def __init__(self, node_process, time_per_batch=1):
        '''
            name: unique name of stage. Used to identify log file.
            requirements: the set of items the stage can use as raw material.
            produces: the item the stage produces.
            time_per_batch: time in seconds it takes to make one unit.
            inbound_node_fetcher: function implemented by node that allows fetching incoming nodes
        '''
        super(SuppyChainStage, self).__init__()
        self.name = "sc-stage-{}".format(node_process.node.get_id())
        self.item_dep = node_process.node.get_dependency()
        self.inbound_material = Queue() if self.item_dep else None
        self.outbound_material = Queue()
        self.time_per_batch = time_per_batch
        self.raft_helper = node_process.raft_helper
        self.cluster = node_process.cluster

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
            if state == StageStatus.IN_QUEUE:
                self.inbound_material.put(item)

        for item, state in self.outbound_log.items():
            if state == StageStatus.IN_QUEUE:
                self.outbound_material.put(item)
            elif state == StageStatus.IN_TRANSIT:
                # TODO check with neighbors if this item was delivered
                pass

            self.manufacture_count += 1

        return

    def stop(self):
        '''
            - Stop the stage's priduction & consumption loop.
            - Destory the inbound and outbound queues.

            Used for testing.
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

    async def _acquire_needed_materials(self):
        '''
            Identifies the nodes from where parts are to be requested
            and makes a request for the parts from that node.
        '''
        if not self.item_dep.has_prereq():
            # stage requires no inbound material.
            return True

        flow = await self.raft_helper.get_flow()

        for node_id in flow.get_inbound_node_ids():
            node = self.cluster.get_node(node_id)
            # TODO send material request message and retry
            # until materials are acquired. reply with waiting,
            # then delivered.
            # Then mark consumed in log.

        return True


    def _verify_material(self, material: Item):
        '''
            is a function called as a callback by the node-process
            when it receives material from an inbound edge/node.
        '''
        if self.item_dep.is_valid_material(material):
            self.inbound_log[material] = StageStatus.IN_QUEUE
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
            node. updates the persistant log.
        '''
        self.outbound_log[item] = StageStatus.DELIVERED


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
            self.inbound_log[material] = StageStatus.CONSUMED
        except Empty:
            # queue is empty, need to wait till it's not.
            pass

        # TODO add to outbound only when the inbound queue has been pop()'d correctly
        new_item = Item(type=self.get_stage_result_type(), id=new_item_id)
        self.outbound_log[new_item] = StageStatus.IN_QUEUE
        self.outbound_material.put(new_item)
        self.manufacture_count += 1

        return


    def run(self):

        while self.running.is_set():

            self.manufacture_batch_and_enqueue()
            sleep(self.time_per_batch)
