import pydot
import io
import randomcolor

import basecases as bcs
import cluster as ctr
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from metrics import Metrics


class ClusterPlotter(object):

    def __init__(self, cluster):
        self.cluster = cluster
        self.rand_color = randomcolor.RandomColor()
        # TODO: Add number of colors based on output item type
        self.item_type_to_id = self.cluster.get_distinct_item_types_mapping()
        self.colors = self.rand_color.generate(hue="blue", count=len(self.item_type_to_id))

    def get_item_type(self, node_id):
        return self.cluster.node_ids_to_nodes[node_id].dependency.get_result_item_type()

    def get_color_for_node_id(self, node_id):
        return self.colors[self.item_type_to_id[self.get_item_type(node_id)]]

    def render_pydot_graph_to_console(self, graph):
        # render pydot by calling dot, no file saved to disk
        png_str = graph.create(prog='dot', format='png')
        # treat the dot output string as an image file
        sio = io.BytesIO()
        sio.write(png_str)
        sio.seek(0)
        plt.axis('off')
        plt.imshow(plt.imread(sio), aspect="equal")
        plt.show()

    def get_pydot_graph_from_nx_graph(self, nx_graph: nx.Graph):

        def get_pydot_node(nid):
            return pydot.Node(
                name="{}-{}".format(self.get_item_type(nid), nid),
                style="filled",
                fillcolor=self.get_color_for_node_id(nid)
            )

        graph = pydot.Dot(graph_type='digraph')

        pydot_nodes = {}
        for n in nx_graph.nodes:
            node = get_pydot_node(n)
            graph.add_node(node)
            pydot_nodes[n] = node

        def get_pydot_edge(n0, n1, item_req):
            return pydot.Edge(
                pydot_nodes[n0],
                pydot_nodes[n1],
                label='{}({})'.format(item_req.item.type, item_req.quantity),
                fontsize="10.0",
                color="blue"
            )

        for n0, neighbors in nx_graph.adj.items():
            for n1, edge_attr in neighbors.items():
                item_req = edge_attr['item_req']
                edge = get_pydot_edge(n0, n1, item_req)
                graph.add_edge(edge)

        return graph

    def plot_current_state(self, flow: ctr.ClusterWideFlow):
        graph = flow.get_networkx_graph_repr()
        pydot_graph = self.get_pydot_graph_from_nx_graph(graph)
        self.render_pydot_graph_to_console(pydot_graph)


if __name__ == "__main__":

    metrics = Metrics()
    nodes = bcs.bootstrap_dependencies_seven_nodes()

    blueprint = ctr.ClusterBlueprint(nodes)
    cluster = ctr.Cluster(metrics, blueprint)
    flow = ctr.bootstrap_flow(cluster.nodes)

    plotter = ClusterPlotter(cluster)

    plotter.plot_current_state(flow)
