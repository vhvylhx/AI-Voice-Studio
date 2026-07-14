from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields


def default_variants():

    variants = [
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
        }
        for variant_id, name in variants
    ]


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

    variants: list[dict] = field(
        default_factory=default_variants
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
