import time
import logging
import cluster as ctr
import file_dict as fd


log = logging.getLogger()


class StateReader(object):
    """
    Base class abstracting out the underlying read ops for leader election, flow consensus
    This can only allow reads
    """

    def __init__(self):
        # Constructs for maintaining source of truth
        self.leader_file = fd.FileDict(filename="state:leader")
        self.consensus_file = fd.FileDict(filename="state:consensus")
        self.cluster_file = fd.FileDict(filename="state:cluster")

        # Keys for each of the fields involved
        self.leader_id = "leader_id"
        self.time_key = "timestamp"
        self.flow_key = "flow"
        self.cluster_key = "cluster"

    def get_cluster(self):
        try:
            cluster = self.cluster_file[self.cluster_key]
        except Exception as e:
            log.critical("Unable to fetch cluster information")
            log.exception(e)
            return None
        else:
            return cluster

    def get_leader(self):
        try:
            leader = self.leader_file[self.leader_id]
        except:
            return None
        else:
            return leader

    def get_flow(self):
        try:
            flow = self.consensus_file[self.flow_key]
        except Exception:
            log.error("Node %d unable to fetch cluster flow. Flow not available in consensus file", self.node_id)
            return None
        else:
            # HACK convert the flow key types to bypass the implicit int to str conversion
            # that occurs during file persistance of the flow object
            flow.outgoing_flows = {int(k): v for k, v in flow.outgoing_flows.items()}
            flow.incoming_flows = {int(k): v for k, v in flow.incoming_flows.items()}
            return flow


class FileBasedStateHelper(StateReader):
    """
    Helper class abstracting out the underlying file ops for leader election, flow consensus
    """

    def __init__(self, node_id):
        super(FileBasedStateHelper, self).__init__()
        # Establish node specific fields
        self.node_id = node_id

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
            log.info("Node {} (leader) updated flow to: {}".format(self.node_id, new_cluster_flow))
            return True
        return False

    def set_cluster(self, cluster: ctr.Cluster):
        """
            Utility to persist cluster; every node can do this
        """
        self.cluster_file[self.cluster_key] = cluster
        log.debug("Node {} updated cluster".format(self.node_id))
