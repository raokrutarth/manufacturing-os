import unittest
import logging
import sys

from metrics import Metrics

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
log = logging.getLogger()

'''
    Run unit tests in root dir with command:
        python -m unittest discover -v -s src/ -p "*metrics.py"
'''


class TestMetrics(unittest.TestCase):

    def setUp(self):
        self.metrics = Metrics()

    def tearDown(self):
        pass

    def test_valid_increment(self):
        self.metrics.increase_metric(0, "my_metric_1")
        self.metrics.increase_metric(0, "my_metric_1", 42)
        self.assertTrue(
            self.metrics.get_metric(0, "my_metric_1") == 43.0,
            "metric not found"
        )

        self.metrics.decrease_metric(0, "my_metric_1")
        self.metrics.decrease_metric(0, "my_metric_1", 2)
        self.assertTrue(
            self.metrics.get_metric(0, "my_metric_1") == 40.0,
            "metric not found"
        )

    def test_valid_set_and_get(self):
        with self.assertRaises(LookupError):
            self.metrics.get_metric(0, "my_metric_2")

        self.metrics.set_metric(0, "my_metric_2", 9)

        self.assertTrue(
            self.metrics.get_metric(0, "my_metric_2") == 9.0,
            "metric not correct"
        )

        self.metrics.set_metric(0, "my_metric_2", 10.0)

        self.assertTrue(
            self.metrics.get_metric(0, "my_metric_2") == 10.0,
            "metric not correct"
        )

    def test_invalid_set(self):
        with self.assertRaises(TypeError):
            self.metrics.set_metric("0", 90, "42")
