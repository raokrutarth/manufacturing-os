import enum
import messages


class Op(enum.Enum):

    # Inits a heartbeat from a node
    Heartbeat = 1
    # Signals to initiate leader election
    ElectLeader = 2
    # Notifies everyone of death
    Death = 3
    # Signals to perform re-allocation; different from allocate in case we use a different optimized algorithm for
    # re-allocation - which we should ideally do
    ReAllocate = 4

    """
    Operations which are supported right now
    """

    # Signals to initiate initial flow allocation consensus
    Allocate = 5


class OpHandler:

    @staticmethod
    def getMsgForOp(op: Op):
        if op == Op.Allocate:
            return messages.AllocateReq()
        else:
            assert False, "Invalid op: {}".format(op.name)
