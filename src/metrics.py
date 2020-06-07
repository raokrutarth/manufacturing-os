from os.path import abspath
import pandas as pd
from datetime import datetime
from typing import List
import logging
from enum import Enum

log = logging.getLogger()


class DFOperation(Enum):
    Increase = 0
    Decrease = 1
    Set = 2


class Metrics:
    '''
        Metrics allows different parts of the code to set metics that can
        be measured and persisted in a csv file.
    '''
    def __init__(self, node_id):
        self._metrics_file = abspath("./tmp/manufacturing_os_metrics_node_{}.csv".format(node_id))
        self._df = pd.DataFrame(columns=["timestamp", "node_id", "metric_name", "value"])

        self._df.timestamp = pd.to_datetime(self._df.timestamp)
        self._df.node_id = self._df.node_id.astype(int)
        self._df.metric_name = self._df.metric_name.astype(str)
        self._df.value = self._df.value.astype("float64")

    def _persist_metrics(self):
        self._df.to_csv(self._metrics_file)

    def _modify_or_add_to_df(self, node_id: int, metric_name: str, value: float, mode: DFOperation):
        if ((self._df.node_id == node_id) & (self._df.metric_name == metric_name)).any():
            if mode == DFOperation.Increase:
                self._df.loc[(self._df.node_id == node_id) & (self._df.metric_name == metric_name), "value"] += value
            elif mode == DFOperation.Decrease:
                self._df.loc[(self._df.node_id == node_id) & (self._df.metric_name == metric_name), "value"] -= value
            elif mode == DFOperation.Set:
                self._df.loc[(self._df.node_id == node_id) & (self._df.metric_name == metric_name), "value"] = value

            self._df.loc[(self._df.node_id == node_id) & (self._df.metric_name == metric_name), "timestamp"] = datetime.now()
        else:
            self._df = self._df.append({
                "timestamp": datetime.now(),
                "node_id": node_id,
                "metric_name": metric_name,
                "value": value if mode != DFOperation.Decrease else (-1 * value),
            }, ignore_index=True)
        self._persist_metrics()

    def increase_metric(self, node_id: int, metric_name: str, value: float = 1.0):
        self._modify_or_add_to_df(node_id, metric_name, value, DFOperation.Increase)

    def decrease_metric(self, node_id: int, metric_name: str, value: float = 1.0):
        self._modify_or_add_to_df(node_id, metric_name, value, DFOperation.Decrease)

    def set_metric(self, node_id: int, metric_name: str, value: float):
        self._modify_or_add_to_df(node_id, metric_name, value, DFOperation.Set)

    def get_metric(self, node_id: int, metric_name: str):
        column = self._df.loc[(self._df["node_id"] == node_id) & (self._df["metric_name"] == metric_name)]

        if column.empty:
            raise LookupError
        elif len(column) > 1:
            raise ValueError
        result = column.value.iloc[0]
        return result

    def plot_metrics(self, node_id: int, metric_names: List[str]):
        pass
