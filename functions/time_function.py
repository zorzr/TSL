import sys
from abc import ABC, abstractmethod


class TimeFunction(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_parameters(self):
        pass

    @abstractmethod
    def process_series(self, ts, param):
        pass
