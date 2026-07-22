from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


LANGUAGE_CATALOG_VERSION = 1

LANGUAGE_STATUS_READY = "READY"
LANGUAGE_STATUS_BLOCKED = "BLOCKED"
LANGUAGE_STATUS_MISSING = "MISSING"
LANGUAGE_STATUS_UNAVAILABLE = "UNAVAILABLE"
LANGUAGE_STATUS_UNVERIFIED = "UNVERIFIED"

ENGINE_GPT_SOVITS = "gpt_sovits"
ENGINE_VIETNAMESE = "vietnamese_engine"


@dataclass
class LanguageDefinition:

    code: str = ""

    display_name_vi: str = ""

    display_name_en: str = ""

    primary: bool = False

    default_engine_id: str = ""

    gpt_sovits_language: str = ""

    aliases: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VoiceEngineBinding:

    language_code: str = ""

    engine_id: str = ""

    runtime_profile_id: str = ""

    status: str = "unconfigured"

    active: bool = True

    model_binding: dict = field(
        default_factory=dict
    )

    reference_binding: dict = field(
        default_factory=dict
    )

    inference_verified: bool = False

    smoke_fingerprint: str = ""

    compatibility_notes: list[str] = field(
        default_factory=list
    )

    updated_at: str = ""

    def to_dict(self):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(
            data or {}
        )

        allowed = cls.__dataclass_fields__

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in allowed
            }
        )


@dataclass
class LanguageDetectionResult:

    language_code: str = ""

    confidence: float = 0.0

    method: str = "heuristic"

    warnings: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class LanguageSegment:

    segment_id: str = ""

    text: str = ""

    language_code: str = ""

    confidence: float = 0.0

    start_index: int = 0

    end_index: int = 0

    warnings: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class LanguageRoute:

    language_code: str = ""

    engine_id: str = ""

    runtime_profile_id: str = ""

    status: str = LANGUAGE_STATUS_BLOCKED

    reason: str = ""

    gpt_sovits_language: str = ""

    fingerprint: str = ""

    warnings: list[str] = field(
        default_factory=list
    )

    blockers: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )
