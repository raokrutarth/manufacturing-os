from random import randint
import numpy as np

import time
import zmq
import sys
from  multiprocessing import Process
import threading

## Initial CODE with zmq
def server(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print("Running server on port: ", port)
    # serves only 5 request and dies
    for reqnum in range(5):
        # Wait for next request from client
        message = socket.recv()
        print("Received request #%s: %s" % (reqnum, message))

        # Send Object!!!
        socket.send_string("World from %s" % port) 
         
def client(ports=["5556"]):
    context = zmq.Context()
    print("Connecting to server with ports %s" % ports)
    socket = context.socket(zmq.REQ)
    for port in ports:
        socket.connect("tcp://localhost:%s" % port)
    for request in range (20):
        print("Sending request ", request,"...")
        socket.send_string("Hello")
        message = socket.recv()
        print("Received reply ", request, "[", message, "]")
        time.sleep (0.01) 



def start_process(process_id, init_inventory):
    print(process_id, " process started with inventory ", init_inventory)
    '''
        TODO
        Add new process start logic here
    '''

    while True:

        sleep(30)


def main():
    server_ports = range(5550,5558,2)
    for server_port in server_ports:
        Process(target=server, args=(server_port,)).start()
        
    # Now we can connect a client to all these servers
    Process(target=client, args=(server_ports,)).start()
    

    # # set of raw inventory items. i.e. part IDs
    # all_raw_inventory = [randint(0, 5) for _ in range(50000)]

    # num_nodes = 5
    # crash_codes = []

    # with Pool(processes=num_nodes) as pool:
    #     raw_inventory = np.array_split(all_raw_inventory, num_nodes)

    #     for i, i_subset in enumerate(raw_inventory):
    #         r = pool.apply_async(
    #             start_process,
    #             (i, i_subset)
    #         )
    #         crash_codes.append(r)

    #     for r in crash_codes:
    #         print(r.get())

    return None

if __name__ == "__main__":
    main()
    