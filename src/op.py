import enum

class Op(enum.Enum):

    def __repr__(self):
        return "{}".format(self.name)

    # Inits a heartbeat from a node
    SendHeartbeat = 1

    # Signals to perform re-allocation; different from allocate in case we
    # use a different optimized algorithm for re-allocation
    TriggerReAllocate = 4

    """
    Operations which are supported right now
    """

    # Signals to initiate initial flow allocation consensus
    TriggerAllocate = 3

    # Signals to broadcast update dep request i.e. update its production, consumption requirements
    SendUpdateDep = 5

    # Signal to kill node
    Kill = 2

    # Signal to recover node
    Recover = 6