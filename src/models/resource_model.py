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

WORKLOAD_CLASS_LIGHT = "light"
WORKLOAD_CLASS_CPU_HEAVY = "cpu_heavy"
WORKLOAD_CLASS_GPU_INFERENCE = "gpu_inference"
WORKLOAD_CLASS_GPU_TRAINING = "gpu_training"
WORKLOAD_CLASS_IO_HEAVY = "io_heavy"

WORKLOAD_CLASSES = (
    WORKLOAD_CLASS_LIGHT,
    WORKLOAD_CLASS_CPU_HEAVY,
    WORKLOAD_CLASS_GPU_INFERENCE,
    WORKLOAD_CLASS_GPU_TRAINING,
    WORKLOAD_CLASS_IO_HEAVY,
)

SNAPSHOT_STATUS_VALID = "valid"
SNAPSHOT_STATUS_INVALID = "invalid"
SNAPSHOT_STATUS_UNKNOWN = "unknown"
SNAPSHOT_STATUS_STALE = "stale"

SNAPSHOT_STATUSES = (
    SNAPSHOT_STATUS_VALID,
    SNAPSHOT_STATUS_INVALID,
    SNAPSHOT_STATUS_UNKNOWN,
    SNAPSHOT_STATUS_STALE,
)

SHADOW_DECISION_WOULD_READY = "WOULD_READY"
SHADOW_DECISION_WOULD_WAIT = "WOULD_WAIT"
SHADOW_DECISION_WOULD_BLOCK = "WOULD_BLOCK"
SHADOW_DECISION_CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"

SHADOW_DECISIONS = (
    SHADOW_DECISION_WOULD_READY,
    SHADOW_DECISION_WOULD_WAIT,
    SHADOW_DECISION_WOULD_BLOCK,
    SHADOW_DECISION_CONFIRMATION_REQUIRED,
)

RESOURCE_REASON_RAM_BELOW_RESERVE = "ram_below_reserve"
RESOURCE_REASON_RAM_SNAPSHOT_UNKNOWN = "ram_snapshot_unknown"
RESOURCE_REASON_RAM_SNAPSHOT_INVALID = "ram_snapshot_invalid"
RESOURCE_REASON_SNAPSHOT_STALE = "snapshot_stale"
RESOURCE_REASON_DISK_BELOW_RESERVE = "disk_below_reserve"
RESOURCE_REASON_DISK_SNAPSHOT_UNKNOWN = "disk_snapshot_unknown"
RESOURCE_REASON_DISK_SNAPSHOT_INVALID = "disk_snapshot_invalid"
RESOURCE_REASON_GPU_UNAVAILABLE = "gpu_unavailable"
RESOURCE_REASON_VRAM_BELOW_RESERVE = "vram_below_reserve"
RESOURCE_REASON_GPU_SNAPSHOT_UNKNOWN = "gpu_snapshot_unknown"
RESOURCE_REASON_GPU_SNAPSHOT_INVALID = "gpu_snapshot_invalid"
RESOURCE_REASON_CPU_FALLBACK_CONFIRMATION_REQUIRED = (
    "cpu_fallback_confirmation_required"
)
RESOURCE_REASON_HEAVY_JOB_ALREADY_ACTIVE = "heavy_job_already_active"

LEASE_STATUS_ACTIVE = "active"
LEASE_STATUS_EXPIRED = "expired"
LEASE_STATUS_STALE = "stale"
LEASE_STATUS_RELEASED = "released"
LEASE_STATUS_ORPHANED = "orphaned"
LEASE_STATUS_UNKNOWN = "unknown"

LEASE_STATUSES = (
    LEASE_STATUS_ACTIVE,
    LEASE_STATUS_EXPIRED,
    LEASE_STATUS_STALE,
    LEASE_STATUS_RELEASED,
    LEASE_STATUS_ORPHANED,
    LEASE_STATUS_UNKNOWN,
)

LEASE_SHADOW_ACTION_WOULD_ACQUIRE = "WOULD_ACQUIRE"
LEASE_SHADOW_ACTION_WOULD_RENEW = "WOULD_RENEW"
LEASE_SHADOW_ACTION_WOULD_RELEASE = "WOULD_RELEASE"
LEASE_SHADOW_ACTION_WOULD_EXPIRE = "WOULD_EXPIRE"
LEASE_SHADOW_ACTION_WOULD_MARK_STALE = "WOULD_MARK_STALE"
LEASE_SHADOW_ACTION_WOULD_RECONCILE = "WOULD_RECONCILE"
LEASE_SHADOW_ACTION_WOULD_SKIP = "WOULD_SKIP"
LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE = "WOULD_BLOCK_DUPLICATE"

LEASE_SHADOW_ACTIONS = (
    LEASE_SHADOW_ACTION_WOULD_ACQUIRE,
    LEASE_SHADOW_ACTION_WOULD_RENEW,
    LEASE_SHADOW_ACTION_WOULD_RELEASE,
    LEASE_SHADOW_ACTION_WOULD_EXPIRE,
    LEASE_SHADOW_ACTION_WOULD_MARK_STALE,
    LEASE_SHADOW_ACTION_WOULD_RECONCILE,
    LEASE_SHADOW_ACTION_WOULD_SKIP,
    LEASE_SHADOW_ACTION_WOULD_BLOCK_DUPLICATE,
)

LEASE_REASON_MISSING = "lease_missing"
LEASE_REASON_EXPIRED = "lease_expired"
LEASE_REASON_STALE = "lease_stale"
LEASE_REASON_DUPLICATE = "lease_duplicate"
LEASE_REASON_OWNER_MISMATCH = "lease_owner_mismatch"
LEASE_REASON_JOB_MISSING = "lease_job_missing"
LEASE_REASON_PROCESS_MISSING = "lease_process_missing"
LEASE_REASON_PROCESS_IDENTITY_MISMATCH = "lease_process_identity_mismatch"
LEASE_REASON_RENEWAL_DUE = "lease_renewal_due"
LEASE_REASON_RELEASE_DUE = "lease_release_due"
LEASE_REASON_ORPHANED = "lease_orphaned"
LEASE_REASON_STORE_CORRUPT = "lease_store_corrupt"
LEASE_REASON_STORE_UNAVAILABLE = "lease_store_unavailable"
LEASE_REASON_SCHEMA_LEGACY = "lease_schema_legacy"
LEASE_REASON_POLICY_MISMATCH = "lease_policy_mismatch"
LEASE_REASON_RECONCILIATION_REQUIRED = "lease_reconciliation_required"

LEASE_REASON_CODES = (
    LEASE_REASON_MISSING,
    LEASE_REASON_EXPIRED,
    LEASE_REASON_STALE,
    LEASE_REASON_DUPLICATE,
    LEASE_REASON_OWNER_MISMATCH,
    LEASE_REASON_JOB_MISSING,
    LEASE_REASON_PROCESS_MISSING,
    LEASE_REASON_PROCESS_IDENTITY_MISMATCH,
    LEASE_REASON_RENEWAL_DUE,
    LEASE_REASON_RELEASE_DUE,
    LEASE_REASON_ORPHANED,
    LEASE_REASON_STORE_CORRUPT,
    LEASE_REASON_STORE_UNAVAILABLE,
    LEASE_REASON_SCHEMA_LEGACY,
    LEASE_REASON_POLICY_MISMATCH,
    LEASE_REASON_RECONCILIATION_REQUIRED,
)


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

            data = data.to_dict()

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

            data = data.to_dict()

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

    provider_status: dict = field(
        default_factory=dict
    )

    validation_status: str = SNAPSHOT_STATUS_UNKNOWN

    validation_reason_codes: list = field(
        default_factory=list
    )

    freshness_age_seconds: float = 0.0

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

    workload_class: str = WORKLOAD_CLASS_LIGHT

    estimated_peak_ram_mb: int = 0

    estimated_peak_vram_mb: int = 0

    estimated_disk_mb: int = 0

    heavy_job: bool = False

    cpu_fallback_supported: bool = True

    cpu_fallback_confirmed: bool = False

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

            data = data.to_dict()

        data = data or {}

        requirement = cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )

        if requirement.workload_class not in WORKLOAD_CLASSES:

            requirement.workload_class = WORKLOAD_CLASS_LIGHT

        if not requirement.estimated_peak_ram_mb:

            requirement.estimated_peak_ram_mb = requirement.ram_mb

        if not requirement.estimated_peak_vram_mb:

            requirement.estimated_peak_vram_mb = requirement.vram_mb

        if not requirement.estimated_disk_mb:

            requirement.estimated_disk_mb = requirement.disk_free_mb

        if (
            requirement.requires_gpu
            and requirement.workload_class == WORKLOAD_CLASS_LIGHT
        ):

            requirement.workload_class = WORKLOAD_CLASS_GPU_INFERENCE

        if requirement.workload_class in (
            WORKLOAD_CLASS_CPU_HEAVY,
            WORKLOAD_CLASS_GPU_INFERENCE,
            WORKLOAD_CLASS_GPU_TRAINING,
            WORKLOAD_CLASS_IO_HEAVY,
        ):

            requirement.heavy_job = True

        return requirement


@dataclass
class ResourceSnapshotValidation:

    status: str = SNAPSHOT_STATUS_UNKNOWN

    reason_codes: list = field(
        default_factory=list
    )

    ram_status: str = SNAPSHOT_STATUS_UNKNOWN

    gpu_status: str = SNAPSHOT_STATUS_UNKNOWN

    disk_status: str = SNAPSHOT_STATUS_UNKNOWN

    age_seconds: float = 0.0

    validated_at: str = field(
        default_factory=now_iso
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )


@dataclass
class ResourceDecisionObservation:

    actual_decision: str = "ready"

    shadow_decision: str = SHADOW_DECISION_WOULD_READY

    reason_codes: list = field(
        default_factory=list
    )

    snapshot_status: str = SNAPSHOT_STATUS_UNKNOWN

    workload_class: str = WORKLOAD_CLASS_LIGHT

    policy_fingerprint: str = ""

    observed_at: str = field(
        default_factory=now_iso
    )

    would_block: bool = False

    would_wait: bool = False

    confirmation_required: bool = False

    monitor_only: bool = True

    def to_dict(
        self,
    ):

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
class ResourceLeaseV2:

    lease_id: str = ""

    job_id: str = ""

    resource_kind: str = "cpu"

    owner_id: str = ""

    runner_id: str = ""

    workload_class: str = WORKLOAD_CLASS_LIGHT

    acquired_at: str = field(
        default_factory=now_iso
    )

    last_renewed_at: str = field(
        default_factory=now_iso
    )

    expires_at: str = ""

    ttl_seconds: float = 300.0

    status: str = LEASE_STATUS_ACTIVE

    policy_fingerprint: str = ""

    process_identity: dict = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )

    provenance: dict = field(
        default_factory=dict
    )

    schema_version: int = 2

    def to_dict(
        self,
    ):

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

        lease = cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )

        if lease.status not in LEASE_STATUSES:

            lease.status = LEASE_STATUS_UNKNOWN

        if lease.workload_class not in WORKLOAD_CLASSES:

            lease.workload_class = WORKLOAD_CLASS_LIGHT

        return lease

    @classmethod
    def from_legacy(
        cls,
        lease,
        policy=None,
    ):

        lease = ResourceLease.from_dict(
            lease
        )

        requirement = ResourceRequirement.from_dict(
            lease.requirement
        )

        ttl_seconds = float(
            getattr(
                policy,
                "lease_ttl_seconds",
                300.0,
            )
        )

        return cls(
            lease_id=lease.lease_id,
            job_id=lease.job_id,
            resource_kind=lease.resource_type,
            owner_id=lease.owner,
            runner_id=lease.owner,
            workload_class=requirement.workload_class,
            acquired_at=lease.acquired_at,
            last_renewed_at=lease.renewed_at,
            expires_at=lease.expires_at,
            ttl_seconds=ttl_seconds,
            status=lease.status
            if lease.status in LEASE_STATUSES
            else LEASE_STATUS_UNKNOWN,
            policy_fingerprint=getattr(
                policy,
                "fingerprint",
                "",
            ),
            process_identity={},
            metadata={
                "job_type": lease.job_type,
                "gpu_device_id": lease.gpu_device_id,
                "requirement": requirement.to_dict(),
            },
            provenance={
                "source": "legacy_resource_lease",
                "schema_version": 1,
            },
        )


@dataclass
class ResourceLeaseObservation:

    actual_lease_state: str = LEASE_STATUS_UNKNOWN

    shadow_lease_state: str = LEASE_STATUS_UNKNOWN

    shadow_action: str = LEASE_SHADOW_ACTION_WOULD_SKIP

    reason_codes: list = field(
        default_factory=list
    )

    lease_id: str = ""

    job_id: str = ""

    resource_kind: str = "cpu"

    owner_id: str = ""

    expires_at: str = ""

    is_expired: bool = False

    is_stale: bool = False

    duplicate_detected: bool = False

    orphan_detected: bool = False

    would_acquire: bool = False

    would_renew: bool = False

    would_release: bool = False

    would_reconcile: bool = False

    policy_fingerprint: str = ""

    observed_at: str = field(
        default_factory=now_iso
    )

    monitor_only: bool = True

    schema_version: int = 2

    def to_dict(
        self,
    ):

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

    lease_renew_interval_seconds: float = 120.0

    stale_lease_handling_mode: str = "monitor_only"

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

    lease_renew_interval_seconds: float = 120.0

    stale_lease_handling_mode: str = "monitor_only"

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
            "lease_renew_interval_seconds": (
                self.lease_renew_interval_seconds
            ),
            "stale_lease_handling_mode": (
                self.stale_lease_handling_mode
            ),
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
            lease_renew_interval_seconds=float(
                policy.lease_renew_interval_seconds
            ),
            stale_lease_handling_mode=str(
                policy.stale_lease_handling_mode
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

    shadow_observation: dict = field(
        default_factory=dict
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
