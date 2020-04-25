from multiprocessing import  Pool
from time import sleep
from random import randint
import numpy as np

import socket 

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)

def start_process(process_id, init_inventory):
    print(process_id, " process started with inventory ", init_inventory)

    '''
        TODO
        Add new process start logic here
    '''
    while True:
        sleep(30)


def main():

    # set of raw inventory items. i.e. part IDs
    all_raw_inventory = [randint(0, 5) for _ in range(50000)]

    num_nodes = 5
    crash_codes = []

    with Pool(processes=num_nodes) as pool:
        raw_inventory = np.array_split(all_raw_inventory, num_nodes)

        for i, i_subset in enumerate(raw_inventory):
            r = pool.apply_async(
                start_process,
                (i, i_subset)
            )
            crash_codes.append(r)

        for r in crash_codes:
            print(r.get())


    return None

if __name__ == "__main__":
    main()