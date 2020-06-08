import pydot
import io
import state
import randomcolor
import random

import basecases as bcs
import cluster as ctr
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from time import sleep

from metrics import Metrics


class ClusterPlotter(object):

    def __init__(self):
        self.reader = state.StateReader()
        self.rand_color = randomcolor.RandomColor()
        self.colors = self.rand_color.generate(hue="blue", count=len(self.item_type_to_id))

    def init_states(self):
        self.cluster = self.reader.get_cluster()
        self.nodes = self.cluster.nodes

        # TODO: Add number of colors based on output item type
        self.item_type_to_id = self.cluster.get_distinct_item_types_mapping()
        self.node_ids_to_colors = {
            n.node_id: self.colors[self.item_type_to_id[self.get_item_type(n.node_id)]] for n in self.nodes
        }

    def get_item_type(self, node_id):
        return self.cluster.node_ids_to_nodes[node_id].dependency.get_result_item_type()

    def get_color_for_node_id(self, node_id):
        return self.node_ids_to_colors[node_id]

    def reinit_colors_for_nodes(self, leader=None, dead_nodes=None):
        """
        Reinits colors for dead nodes and leader
        """
        leader_color = "#CAFF70"
        dead_color = "#FF4040"
        if leader:
            self.node_ids_to_colors[leader] = leader_color
        if dead_nodes:
            for nid in dead_nodes:
                self.node_ids_to_colors[nid] = dead_color

    def render_pydot_graph_to_console(self, graph):
        # render pydot by calling dot, no file saved to disk
        png_str = graph.create(prog='dot', format='png')
        # treat the dot output string as an image file
        sio = io.BytesIO()
        sio.write(png_str)
        sio.seek(0)
        plt.axis('off')
        plt.imshow(plt.imread(sio), aspect="equal")
        # Allows the plots to work in a non-blocking manner
        plt.draw()
        plt.pause(0.001)

    def get_pydot_graph_from_nx_graph(self, nx_graph: nx.Graph, leader, dead_nodes):

        self.reinit_colors_for_nodes(leader=leader, dead_nodes=dead_nodes)

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

    def plot_current_state(self):
        """
        Plots the current state of the cluster after reading the state from file
        We use the following information,
            - Flow
            - Leader info
            - Hidden info e.g. whether node has crashed or not
            - Metrics - various stats we want to measure
        """
        flow = self.reader.get_flow()
        leader = self.reader.get_leader()
        self.init_states()

        if flow is None:
            return

        # Add plotting the following eventually
        # dead_nodes = self.reader.get_dead_nodes()
        # metrics = self.reader.get_metrics()
        graph = flow.get_networkx_graph_repr()
        pydot_graph = self.get_pydot_graph_from_nx_graph(graph, leader, dead_nodes=None)
        self.render_pydot_graph_to_console(pydot_graph)

    def plot_flow(self, flow: ctr.ClusterWideFlow):
        graph = flow.get_networkx_graph_repr()
        pydot_graph = self.get_pydot_graph_from_nx_graph(graph, leader=None, dead_nodes=None)
        self.render_pydot_graph_to_console(pydot_graph)


if __name__ == "__main__":

    assert False, "This will not work right now"

    nodes = bcs.bootstrap_dependencies_seven_nodes()

    blueprint = ctr.ClusterBlueprint(nodes)
    cluster = ctr.Cluster(blueprint)
    flow = ctr.bootstrap_flow(cluster.nodes, Metrics("ui-test"), 999999)  # HACK

    plotter = ClusterPlotter()
    plotter.plot_flow(flow)
    plotter.plot_current_state()
    sleep(10000)
