from abc import ABCMeta, abstractmethod


class BaseModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_instance():
        raise NotImplementedError

    @abstractmethod
    def predict(self):
        raise NotImplementedError
