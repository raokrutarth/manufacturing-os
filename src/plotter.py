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
from nodes import NodeState
from collections import defaultdict

from metrics import Metrics


class ClusterPlotter(object):

    def __init__(self):
        self.reader = state.StateReader()
        self.metrics = Metrics(-1)

        self.rand_color = randomcolor.RandomColor()

        sleep(5.0)

        self.cluster = self.reader.get_cluster()
        self.nodes = self.cluster.nodes
        self.item_type_to_id = self.cluster.get_distinct_item_types_mapping()
        self.colors = self.rand_color.generate(hue=None, count=len(self.item_type_to_id))
        self.init_states()

        self.num_produces_df = None
        self.counter = 0

    def init_states(self):
        self.cluster = self.reader.get_cluster()
        self.nodes = self.cluster.nodes

        # TODO: Add number of colors based on output item type
        self.item_type_to_id = self.cluster.get_distinct_item_types_mapping()
        self.node_ids_to_colors = {
            n.node_id: self.colors[self.item_type_to_id[self.get_item_type(n.node_id)]] for n in self.nodes
        }
        self.node_ids_to_shapes = {n.node_id: "ellipse" for n in self.nodes}
        self.node_ids_to_styles = {n.node_id: "filled" for n in self.nodes}

    def get_item_type(self, node_id):
        return self.cluster.node_ids_to_nodes[str(node_id)].dependency.get_result_item_type()

    def get_color_for_node_id(self, node_id):
        return self.node_ids_to_colors[node_id]

    def reinit_objs_for_nodes(self, leader_id=None, dead_nodes=None):
        """
        Reinits colors for dead nodes and leader
        """
        leader_color = "#CAFF70"
        dead_color = "#FF4040"

        if dead_nodes is not None:
            for nid in dead_nodes:
                self.node_ids_to_colors[nid] = dead_color
                self.node_ids_to_styles[nid] = "dotted"
        if leader_id is not None:
            self.node_ids_to_colors[leader_id] = leader_color
            self.node_ids_to_shapes[leader_id] = "tripleoctagon"

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
        plt.clf()

    def get_pydot_graph_from_nx_graph(self, nx_graph: nx.Graph, leader_id, dead_node_ids):

        self.reinit_objs_for_nodes(leader_id=leader_id, dead_nodes=dead_node_ids)

        # Store the metrics for production
        num_produces = defaultdict(lambda: 0)

        if self.counter % 3 == 0:
            num_produces_df = self.metrics.get_metrics_for_all('batches_produced_total')
            if num_produces_df is not None:
                self.num_produces_df = num_produces_df
        self.counter += 1

        if self.num_produces_df is not None:
            for index, row in self.num_produces_df.iterrows():
                num_produces[int(row['node_id'])] = int(row['value'])

        def get_pydot_node(nid):
            return pydot.Node(
                name="{}-{}".format(self.get_item_type(nid), nid),
                style=self.node_ids_to_styles[nid],
                shape=self.node_ids_to_shapes[nid],
                fillcolor=self.get_color_for_node_id(nid),
                fontsize="18.0",
                xlabel=str(num_produces[nid])
            )

        graph = pydot.Dot(graph_type='digraph', rankdir='LR', dpi=50)

        pydot_nodes = {}
        for n in nx_graph.nodes:
            node = get_pydot_node(n)
            graph.add_node(node)
            pydot_nodes[n] = node

        def get_pydot_edge(n0, n1, item_req):
            return pydot.Edge(
                pydot_nodes[n0],
                pydot_nodes[n1],
                label='{}'.format(item_req.item.type, item_req.quantity),
                fontsize="16.0",
                color="blue"
            )

        def get_pydot_null_edge(n0, n1):
            return pydot.Edge(
                pydot_nodes[n0],
                pydot_nodes[n1],
                color="white"
            )

        for n0, neighbors in nx_graph.adj.items():
            for n1, edge_attr in neighbors.items():
                item_req = edge_attr['item_req']
                edge = get_pydot_edge(n0, n1, item_req)
                graph.add_edge(edge)

        isolates = list(nx.isolates(nx_graph))
        num_rows = int(len(isolates) ** 0.5)
        for idx in range(0, len(isolates), num_rows):
            for idy in range(idx, idx + num_rows - 1):
                if (idy + 1) >= len(isolates):
                    break
                n0, n1 = isolates[idy], isolates[idy + 1]
                edge = get_pydot_null_edge(n0, n1)
                graph.add_edge(edge)

        return graph

    def get_dead_node_ids(self):
        cluster = self.reader.get_cluster()
        return [n.node_id for n in cluster.nodes if n.is_active == NodeState.inactive]

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
        dead_node_ids = self.get_dead_node_ids()
        self.init_states()

        if flow is None:
            return

        graph = flow.get_networkx_graph_repr()
        pydot_graph = self.get_pydot_graph_from_nx_graph(graph, leader, dead_node_ids=dead_node_ids)
        self.render_pydot_graph_to_console(pydot_graph)

    def plot_flow(self, flow: ctr.ClusterWideFlow):
        graph = flow.get_networkx_graph_repr()
        pydot_graph = self.get_pydot_graph_from_nx_graph(graph, leader_id=None, dead_node_ids=None)
        self.render_pydot_graph_to_console(pydot_graph)


if __name__ == "__main__":

    # nodes = bcs.bootstrap_random_dag(5, 'high', 4)
    nodes = bcs.bootstrap_demo()

    blueprint = ctr.ClusterBlueprint(nodes)
    cluster = ctr.Cluster(blueprint)
    flow = ctr.bootstrap_flow(cluster.nodes, Metrics("ui-test"), 999999)  # HACK

    state_reader = state.FileBasedStateHelper(0)
    state_reader.set_cluster(cluster)
    state_reader.apply_for_leadership()

    # Set some nodes as dead
    for idx in range(len(cluster.nodes)):
        if random.random() < 0.2:
            cluster.nodes[idx].is_active = NodeState.inactive
    state_reader.set_cluster(cluster)
    state_reader.update_flow(flow)

    print('Init plotter...')
    plotter = ClusterPlotter()
    print('Plotting...')

    # plotter.plot_flow(flow)
    plotter.plot_current_state()
