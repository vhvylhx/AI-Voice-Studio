from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


PREPROCESSING_SCHEMA_VERSION = 1


PREPROCESSING_ERROR_CODES = {
    "PREPROCESS_DATASET_INVALID",
    "PREPROCESS_METADATA_INVALID",
    "PREPROCESS_RUNTIME_MISSING",
    "PREPROCESS_SCRIPT_MISSING",
    "PREPROCESS_CONFIG_INVALID",
    "PREPROCESS_CUDA_UNAVAILABLE",
    "PREPROCESS_CUDA_OOM",
    "PREPROCESS_DISK_FULL",
    "PREPROCESS_PERMISSION_DENIED",
    "PREPROCESS_PROCESS_FAILED",
    "PREPROCESS_TIMEOUT",
    "PREPROCESS_OUTPUT_MISSING",
    "PREPROCESS_OUTPUT_INVALID",
    "PREPROCESS_CANCELLED",
    "PREPROCESS_UNKNOWN_ERROR",
}


def now_iso():

    return datetime.now().isoformat()


@dataclass
class PreprocessingStage:

    stage_id: str

    display_name: str

    script_key: str

    command: list = field(
        default_factory=list
    )

    env: dict = field(
        default_factory=dict
    )

    expected_artifacts: list = field(
        default_factory=list
    )

    requires_gpu: bool = False

    status: str = "pending"

    started_at: str = ""

    completed_at: str = ""

    elapsed_seconds: float = 0.0

    exit_code: int | None = None

    stdout_log: str = ""

    stderr_log: str = ""

    error_code: str = ""

    message: str = ""

    artifact_validation: dict = field(
        default_factory=dict
    )

    def to_dict(self):

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if isinstance(
            data,
            cls,
        ):

            return data

        data = data or {}

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )


@dataclass
class PreprocessingPlan:

    preprocessing_run_id: str

    voice_id: str

    display_name_snapshot: str = ""

    metadata_path: str = ""

    metadata_sha256: str = ""

    clip_count: int = 0

    total_duration: float = 0.0

    language: str = "vi"

    sample_rate: int = 32000

    runtime_profile_id: str = ""

    runtime_fingerprint: str = ""

    runtime_root: str = ""

    python_path: str = ""

    output_root: str = ""

    normalized_metadata_path: str = ""

    stages: list = field(
        default_factory=list
    )

    plan_fingerprint: str = ""

    created_at: str = field(
        default_factory=now_iso
    )

    def to_dict(self):

        data = asdict(
            self
        )

        data["stages"] = [
            PreprocessingStage.from_dict(
                item
            ).to_dict()
            for item in self.stages
        ]

        return data

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if isinstance(
            data,
            cls,
        ):

            return data

        data = dict(
            data or {}
        )

        data["stages"] = [
            PreprocessingStage.from_dict(
                item
            )
            for item in data.get(
                "stages",
                []
            )
        ]

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )


@dataclass
class PreprocessingRun:

    preprocessing_run_id: str

    voice_id: str

    display_name_snapshot: str = ""

    status: str = "created"

    dataset_fingerprint: str = ""

    runtime_profile_id: str = ""

    runtime_fingerprint: str = ""

    input_metadata_path: str = ""

    output_root: str = ""

    manifest_path: str = ""

    log_root: str = ""

    stages: list = field(
        default_factory=list
    )

    blockers: list = field(
        default_factory=list
    )

    warnings: list = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=now_iso
    )

    started_at: str = ""

    completed_at: str = ""

    training_ready: bool = False

    def to_dict(self):

        data = asdict(
            self
        )

        data["stages"] = [
            PreprocessingStage.from_dict(
                item
            ).to_dict()
            for item in self.stages
        ]

        return data

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        if isinstance(
            data,
            cls,
        ):

            return data

        data = dict(
            data or {}
        )

        data["stages"] = [
            PreprocessingStage.from_dict(
                item
            )
            for item in data.get(
                "stages",
                []
            )
        ]

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )
