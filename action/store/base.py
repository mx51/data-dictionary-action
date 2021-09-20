from abc import ABCMeta, abstractmethod


class Store(metaclass=ABCMeta):
    @abstractmethod
    def read(self) -> dict:
        pass
