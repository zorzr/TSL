import os
import pandas as pd
from formats.format import *
import config

TIMESTAMP = 'Timestamp'


class DataFile:
    def __init__(self, filename, labels):
        self.filename = filename

        self.df = None
        self.labels_list = []

        ext = os.path.splitext(filename)[1]
        self.io = get_format(ext)

        if self.io is None:
            config.logger.error("Unrecognized format for file: {}".format(self.filename))
            raise UnrecognizedFormatError

        self.read()
        self.update_labels_list(labels)

    def read(self):
        self.df = self.io.read(self.filename)
        if self.df is None:
            config.logger.error("Cannot read file {}, is it structured correctly?".format(self.filename))
            raise BadFileError

    def get_data_columns(self):
        data_col = []
        for i, key in enumerate(self.df):
            if key != TIMESTAMP:
                data_col.append(i)
        return data_col

    def get_original_columns(self):
        functions = config.get_functions()

        orig_col = []
        for i, key in enumerate(self.df):
            if key not in functions:
                orig_col.append(i)
        return orig_col

    def get_function_columns(self):
        functions = config.get_functions()

        func_col = []
        for i, key in enumerate(self.df):
            if key in functions:
                func_col.append(i)
        return func_col

    def get_data_header(self):
        col_names = []
        for key in list(self.df):
            if key != TIMESTAMP:
                col_names.append(key)
        return col_names

    def get_timestamp(self):
        if TIMESTAMP not in list(self.df):
            return []
        return pd.to_datetime(self.df[TIMESTAMP])

    @staticmethod
    def get_label_range(label_col):
        indexes = [i for i, val in enumerate(label_col) if val == 1.0]
        return indexes[0], indexes[-1]

    def update_labels_list(self, labels):
        self.labels_list = []
        for i, key in enumerate(list(self.df)):
            if key in labels:
                data = self.df.iloc[:, i]
                self.labels_list.append([key, self.get_label_range(data)])

        # Labels are removed from DataFrame to avoid mistakes
        for label in labels:
            if label in list(self.df):
                del self.df[label]

    def get_label_series(self, label):
        a = label[1][0]
        b = label[1][1] + 1
        n_rows = self.df.shape[0]
        s = pd.Series(n_rows * [''], name=label[0])
        for i in range(a, b):
            s.iat[i] = '1'
        return s

    def labels_list_to_df(self):
        if not self.labels_list:
            return None

        columns = [self.get_label_series(l) for l in self.labels_list]
        all_columns = pd.concat(columns, axis=1)
        return all_columns

    def save(self):
        label_df = self.labels_list_to_df()
        func_df = self.df.iloc[:, self.get_function_columns()]
        all_data = self.df.iloc[:, self.get_original_columns()]

        if func_df is not None:
            all_data = pd.concat([all_data, func_df], axis=1)
        if label_df is not None:
            all_data = pd.concat([all_data, label_df], axis=1)

        self.io.save(all_data, self.filename)

    def get_series_to_process(self, column, name):
        data = self.df.iloc[:, column]
        index = pd.DatetimeIndex(self.df[TIMESTAMP]) if TIMESTAMP in self.df else self.df.index
        return pd.Series(data.values, index=index, name=name)

    def add_function(self, series):
        self.df = pd.concat([self.df, series], axis=1)

    def remove_function(self, f_name):
        del self.df[f_name]
