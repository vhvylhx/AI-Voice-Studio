from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields

from models.training_reference_config import TrainingReferenceConfig


def default_variants():

    variants = [
        ("default", "Giọng mặc định"),
        ("original", "Giọng gốc"),
        ("original_plus", "Giọng gốc+"),
        ("soft", "Nhẹ nhàng"),
        ("soft_plus", "Nhẹ nhàng+"),
        ("expressive", "Truyền cảm"),
        ("story", "Kể chuyện"),
        ("bright", "Tươi sáng"),
        ("deep", "Trầm ấm"),
        ("podcast", "Podcast"),
        ("audiobook", "Sách nói"),
        ("narration_mc", "MC thuyết minh"),
        ("news_mc", "MC thời sự"),
        ("young_female", "Nữ trẻ"),
        ("adult_female", "Nữ trưởng thành"),
        ("gentle_female", "Nữ dịu dàng"),
        ("elegant_female", "Nữ sang trọng"),
        ("strong_female", "Nữ mạnh mẽ"),
        ("emotional_female", "Nữ cảm xúc"),
        ("young_male", "Nam trẻ"),
        ("adult_male", "Nam trưởng thành"),
        ("warm_male", "Nam ấm áp"),
        ("deep_male", "Nam trầm"),
        ("strong_male", "Nam mạnh mẽ"),
        ("emotional_male", "Nam cảm xúc"),
        ("girl_1", "Bé gái 1"),
        ("girl_2", "Bé gái 2"),
        ("girl_3", "Bé gái 3"),
        ("boy_1", "Bé trai 1"),
        ("boy_2", "Bé trai 2"),
        ("boy_3", "Bé trai 3"),
        ("anime_female", "Anime nữ"),
        ("anime_male", "Anime nam"),
        ("robot", "Robot"),
        ("ai", "AI"),
        ("radio", "Radio"),
        ("eunuch", "Thái giám"),
        ("old_man", "Ông lão"),
        ("old_woman", "Bà lão"),
        ("custom_1", "Tùy chỉnh 1"),
        ("custom_2", "Tùy chỉnh 2"),
        ("custom_3", "Tùy chỉnh 3"),
        ("custom_4", "Tùy chỉnh 4"),
        ("custom_5", "Tùy chỉnh 5"),
    ]

    return [
        {
            "id": variant_id,
            "name": name,
            "enabled": True,
            "trained": False,
            "model_path": "",
            "style_profile_id": "",
            "style_mode": "inherit_voice_default",
            "style_strength": 1.0,
        }
        for variant_id, name in variants
    ]


def default_reading_style():

    return {
        "default_style_profile_id": "",
        "allow_variant_override": True,
        "fallback_mode": "degraded",
    }


def default_speaker_reference():

    return {
        "source_mode": "voice_default",
        "audio_asset_id": "",
        "text_asset_id": "",
        "selected_segment_id": "",
        "audio_path": "",
        "text": "",
        "folder": "",
        "source_origin": "legacy_voice_config",
        "checksum_snapshot": {},
        "legacy_path": "",
        "state": "pending",
        "messages": [],
        "metadata": {},
    }


def normalize_variant_style(
    variant,
):

    variant = dict(
        variant or {}
    )

    variant.setdefault(
        "style_profile_id",
        "",
    )

    variant.setdefault(
        "style_mode",
        "inherit_voice_default",
    )

    if variant[
        "style_mode"
    ] not in {
        "inherit_voice_default",
        "explicit",
        "disabled",
    }:

        variant["style_mode"] = "inherit_voice_default"

    try:

        variant["style_strength"] = float(
            variant.get(
                "style_strength",
                1.0,
            )
        )

    except Exception:

        variant["style_strength"] = 1.0

    return variant


@dataclass
class VoiceConfig:

    #
    # Schema
    #

    schema_version: int = 1

    voice_id: str = ""

    #
    # Display
    #

    language: str = "vi"

    model: str = ""

    training_status: str = "new"

    #
    # Engine
    #

    engine: str = "gpt_sovits"

    engine_path: str = ""

    #
    # Model
    #

    gpt_model: str = ""

    sovits_model: str = ""

    reference_audio: str = ""

    reference_text: str = ""

    prompt_language: str = "vi"

    text_language: str = "vi"

    #
    # Audio
    #

    speed: float = 1.0

    pitch: float = 1.0

    volume: float = 1.0

    temperature: float = 1.0

    top_p: float = 1.0

    top_k: int = 15

    repetition_penalty: float = 1.35

    #
    # Dataset
    #

    dataset_path: str = ""

    sample_rate: int = 32000

    batch_size: int = 4

    epochs: int = 15

    #
    # Dataset Clean
    #

    remove_chapter_title: bool = False

    remove_ads: bool = False

    remove_intro: bool = False

    remove_outro: bool = False

    keep_blank_line: bool = False

    normalize_punctuation: bool = True

    normalize_number: bool = False

    normalize_symbol: bool = True

    normalize_laugh: bool = True

    #
    # Voice Variant
    #

    create_main_voice: bool = True

    create_soft_voice: bool = True

    create_expressive_voice: bool = True

    create_story_voice: bool = True

    create_bright_voice: bool = True

    create_deep_voice: bool = True

    create_male_a: bool = False

    create_male_b: bool = False

    create_female_a: bool = False

    create_female_b: bool = False

    #
    # Emotion
    #

    emotion_strength: float = 0.5

    style_strength: float = 0.5

    similarity: float = 1.0

    #
    # Variant Schema
    #

    default_variant_id: str = "default"

    default_style_id: str = ""

    variants: list[dict] = field(
        default_factory=default_variants
    )

    reading_style: dict = field(
        default_factory=default_reading_style
    )

    speaker_reference: dict = field(
        default_factory=default_speaker_reference
    )

    training_reference: dict = field(
        default_factory=lambda: TrainingReferenceConfig().to_dict()
    )

    #
    # Preview
    #

    preview_text: str = (
        "Xin chào, đây là giọng nói mẫu."
    )

    #
    # Time
    #

    created_at: str = ""

    updated_at: str = ""

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if data is None:

            data = {}

        names = {
            field.name
            for field in fields(cls)
        }

        migrated = {}

        for name in names:

            if name in data:

                migrated[name] = data[name]

        if not migrated.get(
            "variants"
        ):

            migrated["variants"] = default_variants()

        migrated["variants"] = [
            normalize_variant_style(
                variant
            )
            for variant in migrated.get(
                "variants",
                []
            )
        ]

        variant_ids = {
            variant.get(
                "id",
                "",
            )
            for variant in migrated.get(
                "variants",
                []
            )
        }

        if "default" not in variant_ids:

            migrated["variants"] = (
                [
                    {
                        "id": "default",
                        "name": "Giọng mặc định",
                        "enabled": True,
                        "trained": False,
                        "model_path": "",
                        "style_profile_id": "",
                        "style_mode": "inherit_voice_default",
                        "style_strength": 1.0,
                    }
                ]
                + migrated.get(
                    "variants",
                    []
                )
            )

        reading_style = dict(
            migrated.get(
                "reading_style",
                {},
            )
            or {}
        )

        for key, value in default_reading_style().items():

            reading_style.setdefault(
                key,
                value,
            )

        migrated["reading_style"] = reading_style

        speaker_reference = dict(
            migrated.get(
                "speaker_reference",
                {},
            )
            or {}
        )

        for key, value in default_speaker_reference().items():

            speaker_reference.setdefault(
                key,
                value,
            )

        if not speaker_reference.get(
            "audio_path"
        ) and migrated.get(
            "reference_audio",
            "",
        ):

            speaker_reference["audio_path"] = migrated.get(
                "reference_audio",
                "",
            )

        if not speaker_reference.get(
            "text"
        ) and migrated.get(
            "reference_text",
            "",
        ):

            speaker_reference["text"] = migrated.get(
                "reference_text",
                "",
            )

        migrated["speaker_reference"] = speaker_reference

        migrated["training_reference"] = TrainingReferenceConfig.from_dict(
            migrated.get(
                "training_reference",
                {},
            )
        ).to_dict()

        return cls(
            **migrated
        )

    def to_dict(self):

        return {
            field.name: getattr(
                self,
                field.name,
            )
            for field in fields(self)
        }
