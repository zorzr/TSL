import os
import pandas as pd
from formats.format import *
import config

TIMESTAMP = 'Timestamp'


class DataFile:
    def __init__(self, filename, labels):
        self.filename = filename
        self.labels = labels

        self.df = None
        self.functions = []
        self.labels_list = []

        ext = os.path.splitext(filename)[1]
        self.io = get_format(ext)

        if self.io is None:
            config.logger.error("Unrecognized format for file: {}".format(self.filename))
            raise UnrecognizedFormatError

        self.read()
        self.update_labels_list()

    def read(self):
        self.df = self.io.read(self.filename)
        if self.df is None:
            config.logger.error("Cannot read file {}, is it structured correctly?".format(self.filename))
            raise BadFileError

    def get_data_columns(self):
        data_col = []
        for i, key in enumerate(self.df):
            if key != TIMESTAMP and key not in self.labels:
                data_col.append(i)
        return data_col

    def get_original_columns(self):
        orig_col = []
        for i, key in enumerate(self.df):
            if key not in self.labels and key not in self.functions:
                orig_col.append(i)
        return orig_col

    def get_function_columns(self):
        func_col = []
        for i, key in enumerate(self.df):
            if key in self.functions:
                func_col.append(i)
        return func_col

    def get_data_header(self):
        col_names = []
        for key in list(self.df):
            if key != TIMESTAMP and key not in self.labels and key not in self.functions:
                col_names.append(key)
        return col_names

    def get_full_header(self):
        col_names = []
        for key in list(self.df):
            if key != TIMESTAMP and key not in self.labels:
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

    def update_labels_list(self):
        self.labels_list = []
        for i, key in enumerate(list(self.df)):
            if key in self.labels:
                data = self.df.iloc[:, i]
                self.labels_list.append([key, self.get_label_range(data)])

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
        self.df = all_data

    def get_series_to_process(self, column):
        data = self.df[column]
        index = pd.DatetimeIndex(self.df[TIMESTAMP]) if TIMESTAMP in self.df else self.df.index
        return pd.Series(data.values, index=index, name=column)

    # TODO: insert function before labels to keep a single plot_set
    def add_function(self, series):
        self.functions.append(series.name)
        self.df = pd.concat([self.df, series], axis=1)

    def remove_function(self, f_name):
        self.functions.remove(f_name)
        del self.df[f_name]
