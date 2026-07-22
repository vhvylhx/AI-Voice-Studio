from engines.base_engine import BaseEngine
from engines.vieneu_tts_adapter import VieNeuTTSAdapter
from models.engine_info import EngineInfo


class VieNeuTTSEngine(BaseEngine):

    def __init__(
        self,
        adapter=None,
    ):

        self.adapter = adapter or VieNeuTTSAdapter()

        self._runtime_status = None

    def info(
        self,
    ):

        runtime_status = self.availability_probe()

        return EngineInfo(
            id="vieneu",
            name="VieNeu-TTS",
            version="3.2.3",
            author="AI Voice Studio",
            description="Engine tiếng Việt VieNeu-TTS",
            supported_languages=[
                "vi"
            ],
            executable=str(
                self.adapter.runtime_python
            ),
            engine_path=str(
                self.adapter.model_root
            ),
            installed=bool(
                runtime_status.get(
                    "ready"
                )
            ),
            available=bool(
                runtime_status.get(
                    "ready"
                )
            ),
            can_generate=True,
            can_train=False,
            can_preview=False,
            last_error=""
            if runtime_status.get(
                "ready"
            )
            else (
                "VieNeu-TTS runtime chưa sẵn sàng: "
                + runtime_status.get(
                    "reason",
                    "unknown",
                )
            ),
            runtime_status=runtime_status,
        )

    def initialize(
        self,
    ):

        return None

    def is_available(
        self,
    ):

        return bool(
            self.availability_probe().get(
                "ready"
            )
        )

    def availability_probe(
        self,
    ):

        self._runtime_status = self.adapter.availability_probe()

        return dict(
            self._runtime_status
        )

    def validate(
        self,
        text_file,
        output_file,
        voice=None,
    ):

        if voice is None:

            raise RuntimeError(
                "Chưa chọn Voice."
            )

        config = voice.config

        self.adapter.validate(
            text_file=text_file,
            output_file=output_file,
            reference_audio=config.reference_audio,
            reference_text=config.reference_text,
        )

    def generate(
        self,
        text_file,
        output_file,
        voice=None,
        variant=None,
        speed=None,
        emotion=None,
        style=None,
        similarity=None,
    ):

        if voice is None:

            raise RuntimeError(
                "Chưa chọn Voice."
            )

        status = self.availability_probe()

        if not status.get(
            "ready"
        ):

            raise RuntimeError(
                "UNAVAILABLE: VieNeu-TTS runtime chưa sẵn sàng: "
                + status.get(
                    "reason",
                    "unknown",
                )
            )

        config = voice.config

        output_file = self.adapter.generate(
            text_file=text_file,
            output_file=output_file,
            reference_audio=config.reference_audio,
            reference_text=config.reference_text,
            temperature=getattr(
                config,
                "temperature",
                0.70,
            ),
            top_k=getattr(
                config,
                "top_k",
                20,
            ),
            top_p=getattr(
                config,
                "top_p",
                0.95,
            ),
            style=style
            or getattr(
                config,
                "default_style_id",
                "",
            )
            or "tu_nhien",
            denoise=True,
        )

        return output_file

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
