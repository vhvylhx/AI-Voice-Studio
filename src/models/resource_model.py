import hashlib
import json

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


RESOURCE_SCHEMA_VERSION = 1

RESOURCE_POLICY_SCHEMA_VERSION = 2

FEATURE_MODE_DISABLED = "disabled"
FEATURE_MODE_MONITOR_ONLY = "monitor_only"
FEATURE_MODE_ENFORCED = "enforced"

RESOURCE_FEATURE_MODE_KEYS = (
    "resource_policy_v2_mode",
    "resource_decision_v2_mode",
    "resource_lease_v2_mode",
    "thread_budget_mode",
    "process_supervisor_mode",
    "runtime_pressure_guard_mode",
    "job_runner_safety_integration_mode",
    "resource_observability_mode",
)

RESOURCE_FEATURE_MODES = (
    FEATURE_MODE_DISABLED,
    FEATURE_MODE_MONITOR_ONLY,
    FEATURE_MODE_ENFORCED,
)

DEFAULT_RESOURCE_FEATURE_MODES = {
    "resource_policy_v2_mode": FEATURE_MODE_MONITOR_ONLY,
    "resource_decision_v2_mode": FEATURE_MODE_MONITOR_ONLY,
    "resource_lease_v2_mode": FEATURE_MODE_MONITOR_ONLY,
    "thread_budget_mode": FEATURE_MODE_MONITOR_ONLY,
    "process_supervisor_mode": FEATURE_MODE_MONITOR_ONLY,
    "runtime_pressure_guard_mode": FEATURE_MODE_MONITOR_ONLY,
    "job_runner_safety_integration_mode": FEATURE_MODE_DISABLED,
    "resource_observability_mode": FEATURE_MODE_MONITOR_ONLY,
}

FALLBACK_RESOURCE_FEATURE_MODES = {
    key: FEATURE_MODE_DISABLED
    for key in RESOURCE_FEATURE_MODE_KEYS
}

FALLBACK_RESOURCE_FEATURE_MODES[
    "resource_observability_mode"
] = FEATURE_MODE_MONITOR_ONLY

DEFAULT_RAM_PRESSURE_THRESHOLDS_MB = {
    "warning_available_ram_mb": 10240,
    "high_available_ram_mb": 8192,
    "critical_available_ram_mb": 6144,
    "emergency_available_ram_mb": 4096,
}

DEFAULT_THREAD_LIMITS = {
    "ui_light_threads": 2,
    "gpu_orchestration_threads": 2,
    "cpu_heavy_preprocessing_threads": 4,
}


def now_iso():

    return datetime.now().isoformat()


def safe_float(
    value,
    default=0.0,
):

    try:

        return float(
            value
        )

    except Exception:

        return default


def safe_int(
    value,
    default=0,
):

    try:

        return int(
            value
        )

    except Exception:

        return default


def canonical_policy_fingerprint(
    data,
):

    payload = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        payload.encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass
class GPUDeviceInfo:

    device_id: str = "0"

    name: str = ""

    vram_total_mb: int = 0

    vram_free_mb: int = 0

    vram_used_mb: int = 0

    utilization_percent: float = 0.0

    temperature_c: float = 0.0

    cuda_available: bool = False

    status: str = "unknown"

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
class HardwareProfile:

    os_name: str = ""

    cpu_name: str = ""

    cpu_threads: int = 0

    ram_total_mb: int = 0

    gpu_devices: list = field(
        default_factory=list
    )

    ffmpeg_available: bool = False

    ffprobe_available: bool = False

    nvidia_smi_available: bool = False

    detected_at: str = field(
        default_factory=now_iso
    )

    schema_version: int = RESOURCE_SCHEMA_VERSION

    def to_dict(self):

        data = asdict(
            self
        )

        data["gpu_devices"] = [
            GPUDeviceInfo.from_dict(
                item
            ).to_dict()
            for item in self.gpu_devices
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

        data["gpu_devices"] = [
            GPUDeviceInfo.from_dict(
                item
            )
            for item in data.get(
                "gpu_devices",
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
class ResourceSnapshot:

    cpu_percent: float = 0.0

    ram_total_mb: int = 0

    ram_available_mb: int = 0

    ram_used_percent: float = 0.0

    disk_path: str = ""

    disk_total_mb: int = 0

    disk_free_mb: int = 0

    disk_used_percent: float = 0.0

    gpu_devices: list = field(
        default_factory=list
    )

    pressure_state: str = "unknown"

    captured_at: str = field(
        default_factory=now_iso
    )

    schema_version: int = RESOURCE_SCHEMA_VERSION

    def to_dict(self):

        data = asdict(
            self
        )

        data["gpu_devices"] = [
            GPUDeviceInfo.from_dict(
                item
            ).to_dict()
            for item in self.gpu_devices
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

        data["gpu_devices"] = [
            GPUDeviceInfo.from_dict(
                item
            )
            for item in data.get(
                "gpu_devices",
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
class ResourceRequirement:

    profile_id: str = "cpu_light"

    cpu_threads: int = 1

    ram_mb: int = 256

    disk_free_mb: int = 128

    requires_gpu: bool = False

    gpu_count: int = 0

    vram_mb: int = 0

    allow_cpu_fallback: bool = True

    exclusive_gpu: bool = False

    notes: str = ""

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
class ResourcePolicy:

    schema_version: int = RESOURCE_POLICY_SCHEMA_VERSION

    policy_id: str = "balanced"

    display_name: str = "Balanced"

    max_concurrent_jobs: int = 1

    max_gpu_jobs: int = 1

    reserve_ram_mb: int = 1024

    reserve_vram_mb: int = 512

    reserve_disk_mb: int = 1024

    snapshot_ttl_seconds: float = 2.0

    resource_wait_recheck_seconds: float = 5.0

    lease_ttl_seconds: float = 300.0

    pressure_cpu_warning_percent: float = 90.0

    pressure_ram_warning_percent: float = 90.0

    pressure_disk_warning_percent: float = 95.0

    pressure_vram_warning_percent: float = 90.0

    allow_cpu_fallback: bool = True

    auto_pause_on_critical_pressure: bool = False

    feature_modes: dict = field(
        default_factory=lambda: dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
    )

    ram_pressure_thresholds: dict = field(
        default_factory=lambda: dict(
            DEFAULT_RAM_PRESSURE_THRESHOLDS_MB
        )
    )

    thread_limits: dict = field(
        default_factory=lambda: dict(
            DEFAULT_THREAD_LIMITS
        )
    )

    batch_size: int = 1

    cooperative_stop_grace_seconds: int = 20

    kill_escalation_wait_seconds: int = 5

    cpu_fallback_requires_job_confirmation: bool = True

    snapshot_unknown_state_policy: str = "monitor_only"

    scope: str = "global_application"

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

        policy = cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )

        policy.feature_modes = dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        ) | dict(
            policy.feature_modes
            or {}
        )

        policy.ram_pressure_thresholds = dict(
            DEFAULT_RAM_PRESSURE_THRESHOLDS_MB
        ) | dict(
            policy.ram_pressure_thresholds
            or {}
        )

        policy.thread_limits = dict(
            DEFAULT_THREAD_LIMITS
        ) | dict(
            policy.thread_limits
            or {}
        )

        return policy


@dataclass
class ResolvedResourcePolicy:

    schema_version: int = RESOURCE_POLICY_SCHEMA_VERSION

    source: str = "primary"

    notices: list = field(
        default_factory=list
    )

    feature_modes: dict = field(
        default_factory=lambda: dict(
            DEFAULT_RESOURCE_FEATURE_MODES
        )
    )

    reserve_ram_mb: int = 8192

    reserve_vram_mb: int = 512

    reserve_disk_mb: int = 1024

    ram_pressure_thresholds: dict = field(
        default_factory=lambda: dict(
            DEFAULT_RAM_PRESSURE_THRESHOLDS_MB
        )
    )

    max_concurrent_jobs: int = 1

    max_gpu_jobs: int = 1

    batch_size: int = 1

    thread_limits: dict = field(
        default_factory=lambda: dict(
            DEFAULT_THREAD_LIMITS
        )
    )

    allow_cpu_fallback: bool = False

    cpu_fallback_requires_job_confirmation: bool = True

    snapshot_ttl_seconds: float = 2.0

    resource_wait_recheck_seconds: float = 5.0

    lease_ttl_seconds: float = 300.0

    cooperative_stop_grace_seconds: int = 20

    kill_escalation_wait_seconds: int = 5

    snapshot_unknown_state_policy: str = "monitor_only"

    scope: str = "global_application"

    provenance: dict = field(
        default_factory=dict
    )

    fingerprint: str = ""

    def effective_dict(
        self,
    ):

        return {
            "schema_version": self.schema_version,
            "feature_modes": dict(
                self.feature_modes
            ),
            "reserve_ram_mb": self.reserve_ram_mb,
            "reserve_vram_mb": self.reserve_vram_mb,
            "reserve_disk_mb": self.reserve_disk_mb,
            "ram_pressure_thresholds": dict(
                self.ram_pressure_thresholds
            ),
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "max_gpu_jobs": self.max_gpu_jobs,
            "batch_size": self.batch_size,
            "thread_limits": dict(
                self.thread_limits
            ),
            "allow_cpu_fallback": self.allow_cpu_fallback,
            "cpu_fallback_requires_job_confirmation": (
                self.cpu_fallback_requires_job_confirmation
            ),
            "snapshot_ttl_seconds": self.snapshot_ttl_seconds,
            "resource_wait_recheck_seconds": (
                self.resource_wait_recheck_seconds
            ),
            "lease_ttl_seconds": self.lease_ttl_seconds,
            "cooperative_stop_grace_seconds": (
                self.cooperative_stop_grace_seconds
            ),
            "kill_escalation_wait_seconds": (
                self.kill_escalation_wait_seconds
            ),
            "snapshot_unknown_state_policy": (
                self.snapshot_unknown_state_policy
            ),
            "scope": self.scope,
        }

    def to_dict(
        self,
    ):

        data = asdict(
            self
        )

        if not data.get(
            "fingerprint"
        ):

            data["fingerprint"] = canonical_policy_fingerprint(
                self.effective_dict()
            )

        return data

    @classmethod
    def from_policy(
        cls,
        policy,
        source="primary",
        notices=None,
        provenance=None,
    ):

        policy = ResourcePolicy.from_dict(
            policy
        )

        resolved = cls(
            schema_version=RESOURCE_POLICY_SCHEMA_VERSION,
            source=source,
            notices=list(
                notices
                or []
            ),
            feature_modes=dict(
                policy.feature_modes
            ),
            reserve_ram_mb=int(
                policy.reserve_ram_mb
            ),
            reserve_vram_mb=int(
                policy.reserve_vram_mb
            ),
            reserve_disk_mb=int(
                policy.reserve_disk_mb
            ),
            ram_pressure_thresholds=dict(
                policy.ram_pressure_thresholds
            ),
            max_concurrent_jobs=int(
                policy.max_concurrent_jobs
            ),
            max_gpu_jobs=int(
                policy.max_gpu_jobs
            ),
            batch_size=int(
                policy.batch_size
            ),
            thread_limits=dict(
                policy.thread_limits
            ),
            allow_cpu_fallback=bool(
                policy.allow_cpu_fallback
            ),
            cpu_fallback_requires_job_confirmation=bool(
                policy.cpu_fallback_requires_job_confirmation
            ),
            snapshot_ttl_seconds=float(
                policy.snapshot_ttl_seconds
            ),
            resource_wait_recheck_seconds=float(
                policy.resource_wait_recheck_seconds
            ),
            lease_ttl_seconds=float(
                policy.lease_ttl_seconds
            ),
            cooperative_stop_grace_seconds=int(
                policy.cooperative_stop_grace_seconds
            ),
            kill_escalation_wait_seconds=int(
                policy.kill_escalation_wait_seconds
            ),
            snapshot_unknown_state_policy=str(
                policy.snapshot_unknown_state_policy
            ),
            scope=str(
                policy.scope
            ),
            provenance=provenance
            or {
                "policy": source,
                "defaults": "schema_v2",
            },
        )

        resolved.fingerprint = canonical_policy_fingerprint(
            resolved.effective_dict()
        )

        return resolved

@dataclass
class ResourceDecision:

    status: str = "ready"

    reason_code: str = ""

    message_vi: str = ""

    requirement: dict = field(
        default_factory=dict
    )

    snapshot: dict = field(
        default_factory=dict
    )

    policy: dict = field(
        default_factory=dict
    )

    selected_gpu_device_id: str = ""

    pressure_state: str = "normal"

    remediation: list = field(
        default_factory=list
    )

    decided_at: str = field(
        default_factory=now_iso
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
class ResourceLease:

    lease_id: str

    job_id: str

    job_type: str = ""

    owner: str = ""

    resource_type: str = "cpu"

    gpu_device_id: str = ""

    requirement: dict = field(
        default_factory=dict
    )

    acquired_at: str = field(
        default_factory=now_iso
    )

    renewed_at: str = field(
        default_factory=now_iso
    )

    expires_at: str = ""

    status: str = "active"

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
