from engines.base_engine import BaseEngine
from models.engine_info import EngineInfo


class VieNeuTTSEngine(BaseEngine):

    def info(
        self,
    ):

        return EngineInfo(
            id="vieneu",
            name="VieNeu-TTS",
            version="",
            author="AI Voice Studio",
            description="Engine tiếng Việt VieNeu-TTS",
            supported_languages=[
                "vi"
            ],
            installed=False,
            available=False,
            can_generate=True,
            can_train=False,
            can_preview=False,
            last_error=(
                "VieNeu-TTS chưa được cấu hình runtime trong ứng dụng."
            ),
            runtime_status={
                "ready": False,
                "status": "UNAVAILABLE",
                "reason": "vieneu_runtime_not_configured",
            },
        )

    def initialize(
        self,
    ):

        return None

    def is_available(
        self,
    ):

        return False

    def generate(
        self,
        text_file,
        output_file,
        voice=None,
    ):

        raise RuntimeError(
            "UNAVAILABLE: VieNeu-TTS chưa sẵn sàng; không fallback sang GPT-SoVITS cho tiếng Việt."
        )

    def train(
        self,
        voice,
        dataset,
    ):

        raise NotImplementedError(
            "VieNeu-TTS train chưa được tích hợp."
        )

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

        raise RuntimeError(
            "UNAVAILABLE: VieNeu-TTS preview chưa sẵn sàng."
        )

    def stop(
        self,
    ):

        return None

