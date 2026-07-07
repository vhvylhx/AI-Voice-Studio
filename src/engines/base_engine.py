from abc import ABC, abstractmethod


class BaseEngine(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def generate(self, text: str, output_path: str):
        pass