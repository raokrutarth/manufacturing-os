import unittest
from sc_stage import SuppyChainStage
from items import Item, ItemDependency, ItemReq

class TestSupplyChainStage(unittest.TestCase):

    def setUp(self):
        self.inbound_items
        self.stage = SuppyChainStage(
            name='test-stage',
            item_dependency=ItemDe
        )

    def test_insert_into_inbound(self):
        self.stage.accept_material(Item(""))

if __name__ == '__main__':
    unittest.main()