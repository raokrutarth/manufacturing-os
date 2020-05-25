import asyncio
import logging
from typing import List
import os
import raftos
import random
import multiprocessing as mp
import aioprocessing as aio

from threading import Thread
from multiprocessing import Process
from time import sleep

import nodes
import processes
import operations
import cluster
import basecases

from os.path import abspath

LEADER_WAL_DIR = abspath("./tmp")


class DummyProcess(object):

    def init_event_loop(self):
        # Do aioprocessing specific things
        # policy = asyncio.get_event_loop_policy()
        # policy.set_event_loop(policy.new_event_loop())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop

    def __init__(self, port, ports):
        self.port = port
        self.ports = ports

        sleep(random.random())
        print('construct dummy', self.port)
        self.init_event_loop()
        print('init event loop', self.port)
        self.dummy = None

        event_loop = asyncio.get_event_loop()
        assert event_loop == self.loop
        event_loop.run_until_complete(self.init_everything())

    async def init_everything(self):
        print("started init on", self.port)

        await self.init_raftos()
        print('init raftos done', self.port)

        await self.am_i_leader()
        print('am_i_leader done', self.port)
        for i in range(10):
            sleep(1.0)
            print(self.port, raftos.get_leader())

        # event_loop.run_until_complete(self.boot_raftos())

    async def init_raftos(self):
        loop = asyncio.get_event_loop()
        raftos.configure({
            'log_path': LEADER_WAL_DIR,
            'loop': loop
        })

        print('init_raftos', self.port)

        await raftos.register(
            # node running on this machine
            '127.0.0.1:%d' % self.port,
            # other servers
            cluster=['127.0.0.1:%d' % p for p in self.ports],
            loop=loop
        )

        sleep(5.0)
        print('done with init_raftos', self.port)

        return None

    async def boot_raftos(self):
        print('boot_raftos', self.port)
        await self.init_repl_obj()
        print('done with boot_raftos', self.port)

    async def _get_leader(self):
        print("GL: Node %s waiting for leader election to complete. Current leader: %s", self.port, raftos.get_leader())
        await raftos.State.wait_for_election_success()
        leader = raftos.get_leader()
        print("GL: Node {} detected {} as leader node".format(self.port, leader))
        return leader

    async def am_i_leader(self):
        leader = await self._get_leader()
        return leader == self.port

    async def init_repl_obj(self):
        is_leader = await self.am_i_leader()
        if is_leader and False:
            print("I'm on leader: {}".format(self.port))
            dummy_obj = {'x': 0, 'y': 1}
            self.dummy = raftos.Replicated(name='dummy')
            print("Starting to init cluster flow: {} on leader: {}".format(self.port, dummy_obj))
            await self.dummy.set(dummy_obj)
            print("Finished init cluster flow on leader: {}".format(self.node_address))


ports = None
def init_cluster_helper(args):
    node = DummyProcess(args[0], args[1])
    print(node.port, "is done")


def init_cluster_helper_onearg(port):
    global ports
    print(ports)
    node = DummyProcess(port, ports)
    print(node.port, "is done")


async def spawn_cluster_processes(n):
    global ports
    ports = list(range(8000, 8000 + n))
    ps = []
    for port in ports:
        p = Thread(target=init_cluster_helper_onearg, args=(port,), daemon=True)
        ps.append(p)
        print("Node %d started", port)
        p.start()
    # print("Now joining all")
    # for p in ps:
    #     await p.join()


async def spawn_cluster_processes_main_approach(n):
    ports = list(range(8000, 8000 + n))
    ps = []
    for port in ports:
        n = DummyProcess(port, ports)
        await n.init_everything()
    print("Now joining all")


def spawn_cluster_processes_async(n):
    ports = list(range(8000, 8000 + n))
    nodes = [DummyProcess(port, ports) for port in ports]

    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(n.init_everything()) for n in nodes]
    loop.run_until_complete(asyncio.gather(tasks))
    loop.close()


def main():
    # spawn_cluster_processes_async(n=3)
    # spawn_cluster_processes(n=3)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(spawn_cluster_processes(2))
    # loop.run_until_complete(spawn_cluster_processes_main_approach(3))

    print("All nodes started")
    while 1:
        sleep(60)


if __name__ == "__main__":
    main()
