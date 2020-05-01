import unittest
from time import sleep
from multiprocessing import Process

import basecases
import nodes
import processes

# Testing each function
class TestNodes(unittest.TestCase):

    # Testing Single Basenode with structure: Base = namedtuple('Base', ['name', 'id'])
    @unittest.skip("skipping until production logic implemented")
    def test_basenode(self):
        basenode_input = {"name": "door", "node_id": 123}
        basenode = nodes.BaseNode(basenode_input)
        self.assertEqual(basenode.node_id, 123)
        self.assertEqual(basenode.name, "door")

    # Testing Single Itemnode with structure: Item = namedtuple('Base', 'Itemreq') withItemReq = namedtuple('ItemReq', ['item', 'quantity'])
    @unittest.skip("skipping until production logic implemented")
    def test_itemnode(self):
        basenode_input = {"name": "door", "node_id": 123}
        basenode = nodes.BaseNode(basenode_input)
        
        itemreq = {"dependency": "wood", "quantity": 5}
        itemnode = nodes.SingleItemNode(basenode, itemreq)
        print(itemnode)
        self.assertEqual(itemnode.name, "door")
        self.assertEqual(itemnode.node_id, 123)
        self.assertEqual(itemnode.dependency, "wood")
        self.assertEqual(itemnode.quantity, 5)


class BootstrapCluster(unittest.TestCase):
    def setUp(self):
        self.blueprint = basecases.dummyBlueprintCase(3)
        self.cluster = nodes.Cluster(self.blueprint)
        self.TIMEOUT = 3.0

    def spawn_cluster_process(self):
        for node in self.cluster.nodes:
            Process(target=processes.SocketBasedNodeProcess, args=(node, self.cluster)).start()


class TestBootstrapCluster(BootstrapCluster):
    def test_bootstrap_cluster(self):
        self.spawn_cluster_process()
        sleep(self.TIMEOUT)
    

if __name__ == '__main__':
    unittest.main()
