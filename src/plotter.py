import pydot
import randomcolor

import basecases as bcs
import cluster as ctr
import networkx as nx
import matplotlib.pyplot as plt

from metrics import Metrics


class ClusterPlotter(object):

    def __init__(self, cluster):
        self.cluster = cluster
        self.rand_color = randomcolor.RandomColor()
        # TODO: Add number of colors based on output item type
        self.colors = self.rand_color.generate(hue="blue", count=10)

    def get_color_for_node_id(self, node_id):
        item_type = self.cluster.nodes.node_ids_to_nodes[node_id].dependency.get_result_item_type()

    def get_pydot_graph(self):
        graph = pydot.Dot(graph_type='digraph')

        for n, neighbors in graph.adj.items():
            color =
            node = pydot.Node("Node-{}".format(n), style="filled", fillcolor=)
            for nbr, eattr in neighbors.items():
                wt = eattr['weight']
                if wt < 0.5: print('(%d, %d, %.3f)' % (n, nbr, wt))

    def plot_current_state(self, flow: ctr.ClusterWideFlow):
        graph = flow.get_networkx_graph_repr()
        nx.draw(graph)
        plt.show()


if __name__ == "__main__":

    metrics = Metrics()
    nodes = bcs.bootstrap_dependencies_seven_nodes()

    blueprint = ctr.ClusterBlueprint(nodes)
    cluster = ctr.Cluster(metrics, blueprint)
    flow = ctr.bootstrap_flow(cluster.nodes)

    plotter = ClusterPlotter(cluster)

    plotter.plot_current_state(flow)