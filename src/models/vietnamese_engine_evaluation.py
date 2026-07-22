from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


EVIDENCE_CLAIMED = "CLAIMED_BY_UPSTREAM"
EVIDENCE_VERIFIED = "VERIFIED_LOCALLY"
EVIDENCE_NOT_VERIFIED = "NOT_VERIFIED"
EVIDENCE_UNSUPPORTED = "UNSUPPORTED"

LICENSE_PASS = "PASS"
LICENSE_BLOCKED = "BLOCKED"
LICENSE_UNVERIFIED = "LICENSE_UNVERIFIED"

SCORE_MEASURED = "MEASURED"
SCORE_MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
SCORE_CLAIMED_ONLY = "CLAIMED_ONLY"
SCORE_NOT_TESTED = "NOT_TESTED"


@dataclass
class LicenseAudit:

    source_code_license: str = ""

    model_checkpoint_license: str = ""

    dataset_restrictions: str = ""

    commercial_use: str = "unknown"

    attribution_required: bool = False

    redistribution_restriction: str = ""

    status: str = LICENSE_UNVERIFIED

    blockers: list[str] = field(
        default_factory=list
    )

    notes: list[str] = field(
        default_factory=list
    )

    evidence_urls: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class DownloadPlan:

    engine_id: str = ""

    model_id: str = ""

    source: str = ""

    revision: str = ""

    expected_files: list[str] = field(
        default_factory=list
    )

    expected_size: str = ""

    checksum: str = ""

    license: str = ""

    target_cache: str = ""

    disk_free_required: str = ""

    resumable: bool = False

    cleanup_policy: str = "delete_partial_on_failure"

    requires_user_permission: bool = True

    ready_to_download: bool = False

    blockers: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class LowResourceSafetyProfile:

    profile_id: str = "low_resource_safe"

    inference_processes: int = 1

    gpu_concurrency: int = 1

    cpu_workers: int = 1

    batch_size: int = 1

    lazy_load: bool = True

    unload_after_task: bool = True

    allow_parallel_gpu_engines: bool = False

    background_benchmark: bool = False

    full_dataset_run: bool = False

    monitor_process_vram: bool = True

    cancel_supported: bool = True

    no_progress_watchdog: bool = True

    cleanup_process_tree: bool = True

    release_resource_lease: bool = True

    force_gpu: bool = False

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class CandidateScore:

    criterion: str = ""

    status: str = SCORE_NOT_TESTED

    value: str = ""

    notes: str = ""

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class EngineEvaluationRecord:

    engine_id: str = ""

    display_name: str = ""

    upstream_repository: str = ""

    version_commit_tag: str = ""

    source_license: str = ""

    model_checkpoint_license: str = ""

    windows_compatibility: dict = field(
        default_factory=dict
    )

    python_version: dict = field(
        default_factory=dict
    )

    cuda_requirements: dict = field(
        default_factory=dict
    )

    cpu_inference: dict = field(
        default_factory=dict
    )

    gpu_inference: dict = field(
        default_factory=dict
    )

    minimum_observed_ram: dict = field(
        default_factory=dict
    )

    minimum_observed_vram: dict = field(
        default_factory=dict
    )

    model_size: dict = field(
        default_factory=dict
    )

    sample_rate: dict = field(
        default_factory=dict
    )

    voice_cloning_support: dict = field(
        default_factory=dict
    )

    reference_audio_requirements: dict = field(
        default_factory=dict
    )

    reference_text_requirements: dict = field(
        default_factory=dict
    )

    vietnamese_pronunciation: dict = field(
        default_factory=dict
    )

    long_form_support: dict = field(
        default_factory=dict
    )

    style_emotion_support: dict = field(
        default_factory=dict
    )

    streaming_support: dict = field(
        default_factory=dict
    )

    fine_tuning_support: dict = field(
        default_factory=dict
    )

    offline_support: dict = field(
        default_factory=dict
    )

    api_cli_library_integration: dict = field(
        default_factory=dict
    )

    maintenance_state: dict = field(
        default_factory=dict
    )

    known_limitations: list[str] = field(
        default_factory=list
    )

    blockers: list[str] = field(
        default_factory=list
    )

    recommendation: str = ""

    license_audit: dict = field(
        default_factory=dict
    )

    download_plan: dict = field(
        default_factory=dict
    )

    scorecard: list[dict] = field(
        default_factory=list
    )

    evidence_urls: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )
