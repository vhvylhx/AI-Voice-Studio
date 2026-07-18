from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


GENERATE_MODE_STANDARD = "standard"
GENERATE_MODE_AI_STYLE = "ai_style"

TEMP_STATUS_SUCCESS = "success"
TEMP_STATUS_PAUSE = "pause"
TEMP_STATUS_CANCEL = "cancel"
TEMP_STATUS_ERROR = "error"
TEMP_STATUS_STOPPED = "stopped"


@dataclass
class SpeedProfile:

    speed: float = 1.0

    preset_speeds: list[float] = field(
        default_factory=lambda: [
            0.5,
            0.75,
            1.0,
            1.1,
            1.2,
            1.3,
            1.5,
        ]
    )

    allow_custom: bool = True

    custom_min: float | None = 0.8

    custom_max: float | None = 1.2

    method_priority: list[str] = field(
        default_factory=lambda: [
            "native",
            "high_quality_time_stretch",
            "ffmpeg_fallback",
        ]
    )


@dataclass
class GenerateAudioProfile:

    comma_pause_ms: int = 120

    sentence_pause_ms: int = 300

    dialogue_pause_ms: int = 250

    paragraph_pause_ms: int = 500

    scene_pause_ms: int = 800

    crossfade_ms: int = 20

    retry_count: int = 1

    fail_policy: str = "stop_job"

    output_format: str = "wav"

    mp3_bitrate_kbps: int = 192

    supported_mp3_bitrates: list[int] = field(
        default_factory=lambda: [
            128,
            192,
            256,
            320,
        ]
    )

    supported_output_formats: list[str] = field(
        default_factory=lambda: [
            "wav",
            "mp3",
        ]
    )


@dataclass
class GenerateSelectionConfig:

    mode: str = GENERATE_MODE_STANDARD

    voice_id: str = ""

    selected_variant_id: str = ""

    allow_all_variants: bool = False

    allowed_variant_ids: list[str] = field(
        default_factory=list
    )

    allow_all_styles: bool = False

    allowed_style_ids: list[str] = field(
        default_factory=list
    )

    default_variant_id: str = ""

    default_style_id: str = ""

    speed: SpeedProfile = field(
        default_factory=SpeedProfile
    )

    preset_id: str = ""

    reference_style_id: str = ""

    text_profile_id: str = ""

    input_path: str = ""

    output_folder: str = ""

    output_name: str = ""

    output_format: str = "wav"

    mp3_bitrate_kbps: int = 192


@dataclass
class GenerateRequest:

    text: str = ""

    text_file: str = ""

    output_file: str = ""

    selection: GenerateSelectionConfig = field(
        default_factory=GenerateSelectionConfig
    )

    project_id: str = ""

    job_id: str = ""

    overwrite: bool = False

    audio_profile: GenerateAudioProfile = field(
        default_factory=GenerateAudioProfile
    )


@dataclass
class GenerateChunk:

    chunk_id: str = ""

    text: str = ""

    voice_id: str = ""

    variant_id: str = ""

    style_id: str = ""

    preset_id: str = ""

    reference_style_id: str = ""

    speed: float = 1.0

    output_temp_path: str = ""

    status: str = "pending"

    retry_count: int = 0

    error: str = ""

    boundary: str = "sentence"


@dataclass
class GeneratePlan:

    job_id: str = ""

    chunks: list[GenerateChunk] = field(
        default_factory=list
    )

    variant_timeline: "VariantTimeline" | None = None

    style_timeline: "StyleTimeline" | None = None


@dataclass
class VariantDecision:

    segment_index: int = 0

    text: str = ""

    variant_id: str = ""

    confidence: float = 0.0

    reason: str = ""


@dataclass
class StyleDecision:

    segment_index: int = 0

    text: str = ""

    style_id: str = ""

    confidence: float = 0.0

    reason: str = ""


@dataclass
class VariantTimeline:

    items: list[VariantDecision] = field(
        default_factory=list
    )


@dataclass
class StyleTimeline:

    items: list[StyleDecision] = field(
        default_factory=list
    )


@dataclass
class GenerateProgress:

    stage: str = ""

    current_item: int = 0

    total_items: int = 0

    percent: float = 0.0

    elapsed_seconds: float = 0.0

    estimated_remaining_seconds: float = 0.0

    message: str = ""

    level: str = "info"


@dataclass
class TempWorkspace:

    job_id: str = ""

    kind: str = "generate"

    root: str = ""

    work_dir: str = ""

    keep_on_error: bool = True

    cleanup_on_success: bool = True

    keep_on_pause: bool = True

    cancel_requires_user_choice: bool = True

    resume_uses_existing_temp: bool = True


@dataclass
class GenerateResult:

    ok: bool = False

    output_file: str = ""

    mode: str = GENERATE_MODE_STANDARD

    variant_timeline: VariantTimeline = field(
        default_factory=VariantTimeline
    )

    style_timeline: StyleTimeline = field(
        default_factory=StyleTimeline
    )

    warnings: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    temp_workspace: TempWorkspace | None = None

    report_path: str = ""

    report: dict = field(
        default_factory=dict
    )

    def to_dict(self):

        return asdict(
            self
        )
