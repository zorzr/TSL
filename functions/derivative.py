from functions.time_function import TimeFunction
import pandas as pd
import numpy as np

SCALE_NAMES = ['Milliseconds', 'Seconds', 'Minutes', 'Hours', 'Days']
SCALE_VALUES = [0.001, 1.0, 60.0, 3600.0, 86400.0]


class Derivative(TimeFunction):
    def get_name(self):
        return 'Derivative'

    def get_parameters(self):
        return {
            "Time scale": {
                "type": "combo",
                "values": SCALE_NAMES,
                "default": 2
            }
        }

    def process_series(self, ts, param):
        scale_index = SCALE_NAMES.index(param["Time scale"])
        scale = SCALE_VALUES[scale_index]
        dt = self.get_delta(ts.index, scale)
        derivative = ts.diff() / dt
        return pd.Series(derivative.values, name=ts.name)

    @staticmethod
    def get_delta(timestamp, scale):
        try:
            t = timestamp.to_series()
            return t.diff().dt.total_seconds() / scale
        except (TypeError, AttributeError):
            return pd.Series(np.ones(len(timestamp)))

