from functions.time_function import TimeFunction
import pandas as pd
import sys


class MovingAverage(TimeFunction):
    def get_name(self):
        return 'Moving average'

    def get_parameters(self):
        return {
            "Window size": {
                "type": "int",
                "min": 1,
                "max": sys.maxsize,
                "default": 1
            }
        }

    def process_series(self, ts, param):
        size = int(param["Window size"])
        length = ts.shape[0]

        if size < 1 or size > length:
            return None

        average = pd.Series([0] * length, name=ts.name)
        average[0] = ts[0]
        for n in range(1, length):
            step = max(0, n - size)
            average[n] = average[n - 1] + (ts[n] - ts[step]) / size

        return average
