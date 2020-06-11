import sys
import pandas as pd
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
        self.m_dir = metrics_dir
        log.info("Starting to parse exprimental metrics from {}".format(self.m_dir))
        self.metrics_files = glob.glob(metrics_dir + "/*metrics*.csv")
        self.df = self._get_full_df()

    def _get_full_df(self):

        dfs = []
        if not self.metrics_files:
            log.error("Not metrics files in {}".format(self.m_dir))

        for fn in self.metrics_files:
            try:
                new_df = pd.read_csv(fn)
                dfs.append(new_df)
            except Exception as e:
                log.error("Unable to read metrics in file {} with exception {}. Skipping.".format(fn, e))
                continue

        return pd.concat(dfs, ignore_index=True)

    def _augment_results(self):
        # compute messages sent - heartbeats
        # TODO

        # compute messages received - heartbeats
        # TODO
        pass

    def _print_all_data(self):
        self.df.round(2)
        log.info("Full Exprimental results:\n\n%s\n\n===\n", self.df.to_string(float_format="%.0f"))

    def _print_all_metric_stats(self):
        res = self.df.groupby('metric_name').agg({'value': ['min', 'max', 'mean', 'median', 'std', 'var']})
        res.round(2)
        log.info("Metric-wise breakdown or results:\n\n%s\n\n===\n", res.to_string(float_format="%.2f"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        m_dir = sys.argv[1]
    else:
        m_dir = "./tmp"
    mp = Metricparser(m_dir)
    # mp._print_all_data()
    mp._augment_results()
    mp._print_all_metric_stats()
