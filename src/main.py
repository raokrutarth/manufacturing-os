import basecases
import nodes
from multiprocessing import Process

def main():
    demo_blueprint = basecases.dummyBlueprintCase1()
    demo_cluster = nodes.Cluster(demo_blueprint)
    print(demo_cluster)

    flags = {'runOps': True}
    for node in demo_cluster.nodes:
        Process(
            target=nodes.SocketBasedNodeProcess,
            args=(node, demo_cluster, flags),
        ).start()



if __name__ == "__main__":
    main()
