from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


VIENEU_ENGINE_ID = "vieneu_tts"
VIENEU_IMPORT_SCHEMA_VERSION = 1


@dataclass
class VieneuModelSelection:

    engine_id: str = VIENEU_ENGINE_ID

    package_name: str = "vieneu"

    package_version: str = "3.2.3"

    model_repo: str = "pnnbao-ump/VieNeu-TTS-v3-Turbo"

    model_revision: str = "75ff82a"

    display_name: str = "VieNeu-TTS v3 Turbo"

    sample_rate: int = 48000

    device_preference: str = "cpu"

    backend: str = "onnx_cpu"

    reference_cloning_backend: str = "cpu_onnx_ref_audio_supported_with_torchaudio_frontend"

    license: str = "Apache-2.0"

    evidence_urls: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuCodecSelection:

    repo_id: str = "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"

    revision: str = ""

    resolved_revision: str = ""

    license: str = ""

    required_files: list[str] = field(
        default_factory=lambda: [
            "moss_audio_tokenizer_decode_full.onnx",
            "moss_audio_tokenizer_decode_shared.data",
            "moss_audio_tokenizer_decode_step.onnx",
            "codec_browser_onnx_meta.json",
            "moss_audio_tokenizer_encode.onnx",
            "moss_audio_tokenizer_encode.data",
        ]
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuResourceSafetyProfile:

    profile_id: str = "low_resource_safe_32gb"

    inference_concurrency: int = 1

    subprocess_concurrency: int = 1

    batch_size: int = 1

    cpu_threads: int = 2

    cpu_threads_max: int = 4

    process_priority: str = "BELOW_NORMAL"

    gpu_allowed: bool = False

    minimum_free_ram_before_start_gb: float = 8.0

    warning_free_ram_gb: float = 6.0

    critical_free_ram_gb: float = 4.0

    target_process_tree_ram_limit_gb: float = 16.0

    hard_safety_process_tree_ram_limit_gb: float = 20.0

    model_lazy_load: bool = True

    unload_after_operation: bool = True

    no_parallel_engine_loading: bool = True

    no_background_benchmark: bool = True

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuSourceContract:

    engine_id: str = VIENEU_ENGINE_ID

    package_name: str = "vieneu"

    package_version: str = "3.2.3"

    backend: str = "onnx_cpu"

    inference_backend: str = "onnx_cpu"

    reference_frontend: str = "cpu_torch_torchaudio"

    cpu_onnx_ref_audio_supported: bool = True

    gpu_required_for_ref_audio: bool = False

    cuda_allowed: bool = False

    torch_import_required_for_fresh_ref_audio: bool = True

    cpu_torch_frontend_required_for_fresh_reference_enrollment: bool = True

    strict_torch_free_fresh_ref_audio_supported: bool = False

    decision: str = "CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND"

    requirements: list[str] = field(
        default_factory=lambda: [
            "cpu_torch_frontend_required_for_fresh_reference_enrollment"
        ]
    )

    blockers: list[str] = field(
        default_factory=list
    )

    evidence: list[dict] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuRuntimeManifest:

    engine_id: str

    package_version: str

    python_version: str

    model_revision: str

    onnxruntime_version: str | None

    torch_version: str | None

    torchaudio_version: str | None

    cpu_only: bool

    cuda_expected: bool

    cuda_available: bool

    onnx_providers: list[str]

    install_commands: list[list[str]]

    package_hashes: dict[str, str]

    created_at: str

    fingerprint: str

    status: str

    blockers: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuControlledDownloadPlan:

    plan_id: str

    selection: dict

    target_root: str

    runtime_root: str

    model_cache_root: str

    diagnostics_root: str

    allowed_roots: list[str] = field(
        default_factory=list
    )

    license_gate: str = "UNVERIFIED"

    revision_gate: str = "UNVERIFIED"

    model_gate: str = "UNVERIFIED"

    runtime_gate: str = "UNVERIFIED"

    low_resource_gate: str = "UNVERIFIED"

    ready_to_download: bool = False

    ready_to_import: bool = False

    ready_for_canary: bool = False

    blockers: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    install_commands: list[list[str]] = field(
        default_factory=list
    )

    canary_texts: list[str] = field(
        default_factory=list
    )

    cleanup_policy: str = "delete_partial_on_failure"

    schema_version: int = VIENEU_IMPORT_SCHEMA_VERSION

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuReferenceValidation:

    status: str = "missing"

    audio_path: str = ""

    text: str = ""

    language: str = "vi"

    duration: float = 0.0

    sample_rate: int = 0

    channels: int = 0

    codec: str = ""

    requires_resample_copy: bool = False

    blockers: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return asdict(
            self
        )


@dataclass
class VieneuCanaryReport:

    run_id: str

    status: str = "SKIPPED"

    output_root: str = ""

    selected_model: dict = field(
        default_factory=dict
    )

    reference: dict = field(
        default_factory=dict
    )

    command: list[str] = field(
        default_factory=list
    )

    stdout_log: str = ""

    stderr_log: str = ""

    wav_outputs: list[dict] = field(
        default_factory=list
    )

    performance: list[dict] = field(
        default_factory=list
    )

    blockers: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    readiness_effect: dict = field(
        default_factory=dict
    )

    schema_version: int = VIENEU_IMPORT_SCHEMA_VERSION

    def to_dict(self):

        return asdict(
            self
        )
