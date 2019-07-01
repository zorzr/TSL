from abc import ABC, abstractmethod


class Format(ABC):
    extensions = None

    @abstractmethod
    def read(self, filename):
        pass

    @abstractmethod
    def save(self, dataframe, filename):
        pass


def get_format(ext):
    for cls in Format.__subclasses__():
        f = cls()
        if ext in f.extensions:
            return f
    return None


def get_all_formats():
    format_list = []
    for cls in Format.__subclasses__():
        format_list.extend(cls().extensions)
    return format_list


# Exceptions
class UnrecognizedFormatError(Exception):
    pass


class BadFileError(Exception):
    pass
