import basecases as bcs
import cluster as ctr
import networkx as nx
import matplotlib.pyplot as plt

from metrics import Metrics


class ClusterPlotter(object):

    def __init__(self, cluster):
        self.cluster = cluster

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