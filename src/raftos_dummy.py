import asyncio
import logging
from typing import List
import os
import raftos
import random
import multiprocessing as mp
import aioprocessing as aio
from multiprocessing import Process
from time import sleep
from asgiref.sync import async_to_sync

import nodes
import processes
import operations
import cluster
import basecases

from os.path import abspath

LEADER_WAL_DIR = abspath("./tmp")


class DummyProcess(object):

    def __init__(self, port, ports):
        self.port = port
        self.ports = ports
        self.dummy = None

        self.init_everything()

    def init_everything(self):
        loop = asyncio.new_event_loop()
        print("started init on", self.port)

        res = loop.run_until_complete(self.init_raftos(loop))
        print('init raftos done in node with port', self.port, res)
        # everything okay till here

        print("Node ", self.port, " about to check self leader status")
        loop.run_until_complete(self.am_i_leader())
        print('am_i_leader done', self.port)

    async def init_raftos(self, loop):
        raftos.configure({
            'log_path': LEADER_WAL_DIR,
        })

        self_address = '127.0.0.1:%d' % self.port
        cluster_addresses = ['127.0.0.1:%d' % p for p in self.ports if p != self.port]
        print('init_raftos', self.port, self.ports, cluster_addresses)

        await raftos.register(
            # node running on this machine
            self_address,
            # other servers
            cluster=cluster_addresses,
            loop=loop,
        )
        print('raftos register completed in node with port', self.port)
        return True


    async def am_i_leader(self):
        await raftos.State.wait_for_election_success()
        leader = raftos.get_leader()
        print("GL: Node {} detected {} as leader node".format(self.port, leader))
        return leader == "127.0.0.1:%d" % (self.port)

def init_node_helper(args):
    port, ports = args
    node = DummyProcess(port, ports)
    print(node.port, "port based node exited")

def main():
    ports = list(range(5000, 5000 + 3))
    ps = []

    for port in ports:
        # start a OS process per node
        args = (port, ports)
        p = Process(
            target=init_node_helper,
            args=(args,),
            daemon=True
        )
        ps.append(p)
        print("Node with port %d started" % port)
        p.start()


    print("All nodes started")
    while 1:
        sleep(60)


if __name__ == "__main__":
    main()
