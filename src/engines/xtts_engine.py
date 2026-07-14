from pathlib import Path

from engines.base_engine import BaseEngine
from models.engine_info import EngineInfo


class XTTSEngine(BaseEngine):

    def __init__(self):

        self.initialized = False

    def info(self):

        return EngineInfo(
            id="xtts",
            name="XTTS v2",
            version="2.0",
            author="Coqui AI",
            description="Coqui XTTS v2 Text To Speech",
            supported_languages=[
                "vi",
                "en",
                "ja",
                "zh",
                "ko",
            ],
        )

    def initialize(self):

        """
        TODO

        Sprint sau sẽ:

        - Load XTTS model
        - Load CUDA
        - Load tokenizer
        """

        self.initialized = True

    def is_available(self):

        return self.initialized

    def generate(
        self,
        text_file,
        output_file,
        voice=None,
    ):

        raise NotImplementedError(
            "XTTS Generate chưa được cài đặt."
        )

    def validate_dataset(
        self,
        dataset,
    ):

        if not dataset:

            raise Exception(
                "Dataset rỗng."
            )

        items = dataset.get(
            "items",
            [],
        )

        if len(items) < 5:

            raise Exception(
                "Dataset quá ít dữ liệu."
            )

        return True

    def train(
        self,
        voice,
        dataset,
    ):

        self.validate_dataset(
            dataset
        )

        raise NotImplementedError(
            "XTTS Train chưa được cài đặt."
        )

    def create_preview(
        self,
        voice,
        output_file,
    ):

        raise NotImplementedError(
            "Preview chưa được cài đặt."
        )

    def stop(self):

        pass
