from pathlib import Path

from engines.base_engine import BaseEngine
from engines.gpt_sovits_adapter import GPTSoVITSAdapter
from models.engine_info import EngineInfo


class GPTSoVITSEngine(BaseEngine):

    def __init__(self):

        self.root = None

        self.adapter = None

    #
    # Info
    #

    def info(self):

        info = EngineInfo(

            id="gpt_sovits",

            name="GPT-SoVITS",

            version="v2 Pro",

            author="RVC-Boss",

            description="GPT-SoVITS Voice Cloning",

            supported_languages=[
                "en",
                "zh",
                "ja",
            ],

            executable="runtime/python.exe",

        )

        if self.root:

            info.engine_path = str(
                self.root
            )

        if self.adapter:

            runtime = self.adapter.runtime_info()

            info.installed = runtime["ready"]

            info.runtime_status = runtime

            if runtime["version"]:

                info.version = runtime["version"]

            if runtime["missing"]:

                info.last_error = (
                    "Thiếu runtime: "
                    + ", ".join(
                        runtime["missing"]
                    )
                )

        return info

    #
    # Path
    #

    def set_path(
        self,
        folder,
    ):

        self.root = Path(folder)

        self.adapter = GPTSoVITSAdapter(
            self.root
        )

    #
    # Init
    #

    def initialize(self):

        pass

    #
    # State
    #

    def is_available(self):

        return (

            self.adapter is not None

            and

            self.adapter.exists()

        )

    #
    # Generate
    #

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

        if self.adapter is None:

            raise RuntimeError(
                "Chưa cấu hình GPT-SoVITS."
            )

        config = voice.config

        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        options = self.generate_options(
            voice=voice,
            variant=variant,
            speed=speed,
            emotion=emotion,
            style=style,
            similarity=similarity,
        )

        return self.adapter.generate(

            gpt_model=config.gpt_model,

            sovits_model=config.sovits_model,

            reference_audio=config.reference_audio,

            reference_text=config.reference_text,

            prompt_language=config.prompt_language,

            target_text=text_file,

            text_language=config.text_language,

            output_dir=output_file.parent,

            output_file=output_file,

            **options,

        )

    def generate_options(
        self,
        voice,
        variant=None,
        speed=None,
        emotion=None,
        style=None,
        similarity=None,
    ):

        config = voice.config

        return {
            "voice_id": voice.id,
            "variant": variant or self.default_variant(config),
            "speed": speed if speed is not None else config.speed,
            "emotion": emotion or "",
            "style": style or "",
            "similarity": (
                similarity
                if similarity is not None
                else config.similarity
            ),
        }

    def default_variant(
        self,
        config,
    ):

        default_variant_id = getattr(
            config,
            "default_variant_id",
            "",
        )

        if default_variant_id:

            return default_variant_id

        variants = getattr(
            config,
            "variants",
            [],
        )

        if variants:

            return variants[0].get(
                "id",
                "original",
            )

        return "original"

    #
    # Train
    #

    def train(
        self,
        voice,
        dataset,
    ):

        raise NotImplementedError(
            "Sprint sau sẽ tích hợp train GPT-SoVITS."
        )

    #
    # Dataset
    #

    def validate_dataset(
        self,
        dataset,
    ):

        if dataset is None:

            raise RuntimeError(
                "Dataset rỗng."
            )

        if not dataset.get(
            "items"
        ):

            raise RuntimeError(
                "Dataset không có dữ liệu."
            )

        return True

    #
    # Preview
    #

    def create_preview(
        self,
        voice,
        output_file,
    ):

        if voice is None:

            raise RuntimeError(
                "Chưa chọn Voice."
            )

        preview_text = (
            voice.config.preview_text
        )

        temp = (
            Path(output_file)
            .parent
            / "__preview__.txt"
        )

        temp.write_text(
            preview_text,
            encoding="utf-8",
        )

        try:

            return self.generate(
                text_file=temp,
                output_file=output_file,
                voice=voice,
            )

        finally:

            if temp.exists():

                temp.unlink()

    #
    # Stop
    #

    def stop(self):

        #
        # GPT-SoVITS CLI chạy xong sẽ tự thoát.
        #

        pass


## ===== KẾT THÚC FILE =====
