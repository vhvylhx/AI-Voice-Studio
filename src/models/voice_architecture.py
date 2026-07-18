from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class VoiceIdentityContract:

    voice_id: str = ""

    name: str = ""

    dataset_path: str = ""

    model_path: str = ""

    preview_path: str = ""

    metadata_path: str = ""


@dataclass
class VoiceVariantContract:

    variant_id: str = ""

    name: str = ""

    description: str = ""

    reference_style_ids: list[str] = field(
        default_factory=list
    )


@dataclass
class VoicePresetContract:

    preset_id: str = ""

    name: str = ""

    speed: float = 1.0

    pitch: float = 1.0

    volume: float = 1.0

    similarity: float = 1.0

    temperature: float = 1.0

    top_k: int = 15

    top_p: float = 1.0

    pause: float = 0.0

    silence: float = 0.0

    seed: int | None = None

    engine_params: dict = field(
        default_factory=dict
    )


@dataclass
class ReferenceStyleContract:

    reference_style_id: str = ""

    name: str = ""

    audio_paths: list[str] = field(
        default_factory=list
    )


@dataclass
class TextProfileContract:

    text_profile_id: str = ""

    name: str = ""

    sentence_split: str = "default"

    pause_rule: str = "default"

    number_rule: str = "default"

    date_rule: str = "default"

    money_rule: str = "default"

    url_rule: str = "default"

    email_rule: str = "default"

    symbol_rule: str = "default"


@dataclass
class GenerateRequestContract:

    voice_id: str

    variant_id: str

    preset_id: str

    reference_style_id: str

    text_profile_id: str

    engine: str

    text: str

    def to_dict(self):

        return asdict(
            self
        )
