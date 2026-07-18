from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


RESOURCE_SCHEMA_VERSION = 1


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
