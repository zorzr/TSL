import csv
import pandas as pd
from formats.format import Format


class CSVFormat(Format):
    extensions = ['.csv']

    @staticmethod
    def get_dialect(filename):
        with open(filename) as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
        return dialect

    def read(self, filename):
        try:
            d = self.get_dialect(filename)
            df = pd.read_csv(filename, dialect=d, sep=d.delimiter, doublequote=d.doublequote)

            # Fix for columns with the same name
            with open(filename, 'r') as f:
                reader = csv.reader(f, dialect=d)
                header = next(reader)
            df.columns = header
        except pd.errors.ParserError:
            df = None

        return df

    def save(self, dataframe, filename):
        dataframe.to_csv(filename, sep=',', index=False)
