from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


VOICE_PUBLISH_SCHEMA_VERSION = 1


@dataclass
class VoicePublishRequest:

    schema_version: int = VOICE_PUBLISH_SCHEMA_VERSION

    voice_id: str = ""

    training_run_id: str = ""

    gpt_model: str = ""

    sovits_model: str = ""

    reference_audio: str = ""

    reference_text: str = ""

    prompt_language: str = "vi"

    text_language: str = "vi"

    runtime_profile_id: str = ""

    confirm_publish: bool = False

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        names = set(
            cls.__dataclass_fields__.keys()
        )

        return cls(
            **{
                name: data[name]
                for name in names
                if name in data
            }
        )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )


@dataclass
class VoicePublishResult:

    schema_version: int = VOICE_PUBLISH_SCHEMA_VERSION

    publish_id: str = ""

    voice_id: str = ""

    training_run_id: str = ""

    status: str = "blocked"

    validation_status: str = "blocked"

    blockers: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    fingerprint: str = ""

    assets: dict = field(
        default_factory=dict
    )

    created_at: str = ""

    def to_dict(
        self,
    ):

        return asdict(
            self
        )
