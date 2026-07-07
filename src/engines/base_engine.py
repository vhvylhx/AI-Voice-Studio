from abc import ABC
from abc import abstractmethod

from .engine_info import EngineInfo


class BaseEngine(ABC):

    @abstractmethod
    def info(self) -> EngineInfo:
        ...

    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(
        self,
        text_file,
        output_file,
        voice=None,
    ):
        ...

    @abstractmethod
    def stop(self):
        ...