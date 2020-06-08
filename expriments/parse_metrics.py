from os.path import abspath
import sys
import pandas as pd
from datetime import datetime
from typing import List
import logging
import glob

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
)

log = logging.getLogger()


class Metricparser:

    def __init__(self, metrics_dir):
        log.info("Starting to parse exprimental metrics from {}".format(metrics_dir))
        self.metrics_files = glob.glob(metrics_dir + "/*metrics*.csv")
        self.df = self._get_full_df()

    def _get_full_df(self):
        return pd.concat([pd.read_csv(f) for f in self.metrics_files], ignore_index=True)

    def _print_all_data(self):
        self.df.round(2)
        log.info("Full Exprimental results:\n\n%s\n\n===\n", self.df.to_string(float_format="%.0f"))

    def _print_all_metric_stats(self):
        res = self.df.groupby('metric_name').agg({'value': ['min', 'max', 'mean', 'median', 'std', 'var']})
        res.round(2)
        log.info("Metric-wise breakdown:\n\n%s\n\n===\n", res.to_string(float_format="%.2f"))


if __name__ == "__main__":
    mp = Metricparser("../tmp")
    mp._print_all_data()
    mp._print_all_metric_stats()