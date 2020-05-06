
class SuppyChainWorker(object):

    '''
        SuppyChainWorker implements the business logic needed
        by the worker. Each node maintains a SuppyChainWorker that
        is given the up-to-date supply chain state
    '''

    def __init__(self, name):
        self.name = name
        self.incoming_chains = set()
        self.outgoing_chains = set()

    def set_incoming_chains(self, chains):
        self.incoming_chains = chains

    def set_outgoing_chain(self, chains):
        self.outgoing_chains = chains

    def remove_incoming_chains(self, chain):
        self.incoming_chains.remove(chain)

    def remove_outgoing_chain(self, chain):
        self.outgoing_chains.remove(chain)

    def add_incoming_chains(self, chain):
        self.incoming_chains.add(chain)

    def add_outgoing_chain(self, chain):
        self.outgoing_chains.add(chain)

    def request_materials(self):
        # TODO
        # Use self.incoming_chains to pick a node
        # to request parts from. Return the selected node.
        return None

    def send_product(self):
        # TODO
        # Use self.outgoing_chains to pick a node
        # to send parts to. Return the selected node.
        return None
