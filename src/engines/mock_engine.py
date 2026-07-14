from pathlib import Path
import shutil
import time

from engines.base_engine import BaseEngine
from models.engine_info import EngineInfo


class MockEngine(BaseEngine):

    def info(self):

        return EngineInfo(

            id="mock",

            name="Mock Engine",

            version="1.0",

            author="AI Voice Studio",

            description="Testing Engine",

            supported_languages=[
                "vi"
            ],

        )

    def initialize(self):

        pass

    def is_available(self):

        return True

    def generate(

        self,

        text_file,

        output_file,

        voice=None,

    ):

        time.sleep(1)

        output = Path(output_file)

        output.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        sample = Path(
            "assets/sample.wav"
        )

        if sample.exists():

            shutil.copy(
                sample,
                output,
            )

        else:

            output.touch()

    def train(

        self,

        voice,

        dataset,

    ):

        time.sleep(2)

        return True

    def validate_dataset(

        self,

        dataset,

    ):

        return True

    def create_preview(

        self,

        voice,

        output_file,

    ):

        output = Path(
            output_file
        )

        sample = Path(
            "assets/sample.wav"
        )

        if sample.exists():

            shutil.copy(
                sample,
                output,
            )

        else:

            output.touch()

    def stop(self):

        pass