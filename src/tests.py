import unittest
import logging
import basecases
import random
import time
from state import FileBasedStateHelper

from cluster import Cluster
import processes as proc
from time import sleep
from multiprocessing import Process


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger()

if __name__ == '__main__':
    unittest.main()