from abc import ABC
from abc import abstractmethod

from models.engine_info import EngineInfo


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
    def train(
        self,
        voice,
        dataset,
    ):
        """
        Train model.

        dataset:
            DatasetService.prepare()
            trả về.
        """
        ...

    @abstractmethod
    def validate_dataset(
        self,
        dataset,
    ):
        """
        Kiểm tra dataset trước khi train.
        """

        ...

    @abstractmethod
    def create_preview(
        self,
        voice,
        output_file,
    ):
        """
        Sinh preview.wav
        """

        ...

    @abstractmethod
    def stop(self):
        ...
