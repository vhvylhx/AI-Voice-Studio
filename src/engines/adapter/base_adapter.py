from abc import ABC
from abc import abstractmethod


class BaseAdapter(ABC):

    @abstractmethod
    def exists(self):
        ...

    @abstractmethod
    def generate(
        self,
        **kwargs,
    ):
        ...

    @abstractmethod
    def train(
        self,
        **kwargs,
    ):
        ...

    @abstractmethod
    def preview(
        self,
        **kwargs,
    ):
        ...