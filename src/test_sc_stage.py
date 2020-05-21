import unittest
from time import sleep
import logging
import sys

from sc_stage import SuppyChainStage
from items import Item, ItemDependency, ItemReq

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
log = logging.getLogger()

'''
    Run unit tests in root dir with command:
        python -m unittest discover -v -s src/ -p "*sc_stage.py"
'''


class TestSupplyChainStage(unittest.TestCase):

    def start_stage(self, stage):
        stage.daemon = True
        stage.start()

    def setUp(self):
        '''
            This is called immediately before calling the test method.
            gathers the stages necessary for the tests.
        '''
        self.internal_stage = self.get_internal_node_single_unit_stage()
        self.start_stage(self.internal_stage)

    def tearDown(self):
        self.internal_stage.clear_logs()
        return

    def test_invalid_insert_into_inbound(self):
        self.assertFalse(
            self.internal_stage.accept_material(Item("window-type-t", "OPO91")),
            "Stage accepted incorrect item"
        )

    def test_valid_insert_into_inbound(self):
        self.assertTrue(
            self.internal_stage.accept_material(Item("door-frame-type-x", "OPO91")),
            "Stage did not accept correct item"
        )

        self.assertTrue(
            self.internal_stage.inbound_material.qsize() == 1,
            "Inbound queue size incorrect after valid insert attempt"
        )

    def test_internal_stage_production(self):
        # insert first required material
        self.assertTrue(
            self.internal_stage.accept_material(Item("door-frame-type-x", "OPO91")),
            "Stage did not accept correct item"
        )
        # insert second required material
        self.assertTrue(
            self.internal_stage.accept_material(Item(type="window-type-y", id="UYI95")),
            "Stage did not accept correct item"
        )

        # wait for production of one unit
        max_wait = self.internal_stage.time_per_unit + 0.001
        stage_outbound_q = self.internal_stage.get_outbound_queue()
        produced_item = stage_outbound_q.get(timeout=max_wait)

        self.assertTrue(
            produced_item.type == self.internal_stage.get_stage_result_type(),
            "Stage did not produce expected resulting part"
        )
        log.debug("Item produced: %s", produced_item)

if __name__ == '__main__':
    unittest.main()