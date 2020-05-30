import time
import logging
import cluster as ctr
import file_dict as fd


log = logging.getLogger()


class FileBasedStateHelper(object):
    """
    Helper class abstracting out the underlying file ops for leader election, flow consensus
    """

    def __init__(self, node, cluster):
        # extract addresses of other nodes in the cluster
        self.cluster = cluster
        self.nodes = cluster.nodes
        self.node_id = node.node_id

        # Constructs for maintaining source of truth
        self.leader_file = fd.FileDict(filename="state:leader")
        self.consensus_file = fd.FileDict(filename="state:consensus")

        # Keys for each of the fields involved
        self.leader_id = "leader_id"
        self.time_key = "timestamp"
        self.flow_key = "flow"

    def get_leader(self):
        leader = self.leader_file[self.leader_id]
        return leader

    def apply_for_leadership(self):
        '''
            Applies for leadership i.e. persists its own id ad leader
        '''
        log.debug("Node %s applying for leadership", self.node_id)
        application = {self.time_key: time.time(), self.leader_id: self.node_id}
        self.leader_file.update(application)

    def am_i_leader(self):
        leader = self.get_leader()
        return leader == self.node_id

    def update_flow(self, new_cluster_flow: ctr.ClusterWideFlow):
        """
            Utility to persist flow used by leader
        """
        is_leader = self.am_i_leader()
        if is_leader:
            self.consensus_file[self.flow_key] = new_cluster_flow
            log.warning("Updated cluster flow on leader: {} with flow:{}".format(self.node_id, new_cluster_flow))
            return True
        return False

    def get_flow(self):
        try:
            flow = self.consensus_file[self.flow_key]
        except:
            return None
        else:
            return flow

    def __repr__(self):
        return str({
            'RaftHelper': {
                "node ID": self.node_id,
                "cluster": self.cluster,
                # TODO add flow and nodes if necessary
            }
        })