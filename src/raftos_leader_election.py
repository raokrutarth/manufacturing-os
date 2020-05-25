import asyncio
from random import randint
from time import sleep
import raftos
import logging
from os.path import abspath
from multiprocessing import Process


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger()


async def node_routine(loop, node, cluster):

    await raftos.register(node, cluster=cluster, loop=loop)

    TIME = 3
    num_lives = randint(3, 8)
    while True:
        await asyncio.sleep(TIME, loop=loop)
        await raftos.State.wait_for_election_success()

        leader = raftos.get_leader()
        print("Leader is: {}", leader)
        if leader == node:
            num_lives -= 3
            log.info("%s : I am leader" % (node))

        log.info("%s : exiting in %d sec" % (node, num_lives*TIME))

        num_lives -= 1
        if num_lives <= 0:
            break


def run_node(log_dir, node, cluster):
    print("node %s started" % (node))
    loop = asyncio.new_event_loop()

    raftos.configure({
        'log_path': log_dir,
        'serializer': raftos.serializers.JSONSerializer,
        'loop': loop,
        'election_interval_spread': 2.0,
    })

    loop.run_until_complete(node_routine(loop, node, cluster))
    log.info("%s : exited" % (node))


def test():

    cluster = set(['127.0.0.1:{}'.format(port) for port in range(30000, 30034, 2)])
    print(cluster)

    processes = set([])
    log_dir = abspath("./tmp")

    try:
        for node in cluster:
            node_args = (log_dir, node, cluster - {node})
            p = Process(target=run_node, args=node_args)
            log.info("%r", node_args)

            p.start()
            processes.add(p)

        while processes:
            for process in tuple(processes):
                process.join()
                processes.remove(process)
    finally:
        for process in processes:
            if process.is_alive():
                log.warning('Terminating %r', process)
                process.terminate()


if __name__ == '__main__':
    test()