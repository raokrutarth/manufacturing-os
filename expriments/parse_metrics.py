from os.path import abspath
import sys
import pandas as pd
from datetime import datetime
from typing import List
import logging
import glob

log = logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG
)


class Metricparser:

    def __init__(self, metrics_dir):
        log.info()
        self.metrics_files = glob.glob(metrics_dir + "/*metrics*.csv")

    def _get_full_df():
        all_metrics_files =
        return pd.concat([pd.read_csv(f) for f in all_metrics_files], ignore_index=True)

