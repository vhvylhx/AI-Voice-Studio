from pathlib import Path

from engines.base_engine import BaseEngine
from engines.engine_info import EngineInfo


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
        Sprint sau sẽ load model XTTS tại đây.
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
            "XTTS chưa được cài đặt."
        )

    def stop(self):

        pass