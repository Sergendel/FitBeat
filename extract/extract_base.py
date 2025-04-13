import abc


class ExtractBase(abc.ABC):

    @abc.abstractmethod
    def load_data(self):
        pass