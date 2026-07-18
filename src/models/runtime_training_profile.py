from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class HardwareInfo:

    gpu: str = ""

    vram_mb: int = 0

    cuda_available: bool = False

    cpu: str = ""

    cpu_threads: int = 0

    ram_mb: int = 0

    python: str = ""

    runtime_profile_id: str = ""

    runtime_status: str = "unknown"

    fingerprint: str = ""

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
class RuntimeTrainingProfile:

    mode: str = "auto"

    auto_detect_hardware: bool = True

    runtime_profile_id: str = ""

    compute_mode: str = "auto"

    batch_size: int = 1

    num_workers: int = 0

    vram_profile: str = "low_vram"

    gpt_config: str = "s1longer.yaml"

    gpt_epochs: int = 20

    sovits_config: str = "s2v2Pro.json"

    sovits_epochs: int = 50

    save_interval: int = 1

    pretrained_model_version: str = "v2Pro"

    resume_policy: str = "manual"

    checkpoint_policy: str = "save_every_epoch"

    compatibility_mode: str = "compatibility"

    reason: str = ""

    warnings: list[str] = field(
        default_factory=list
    )

    hardware: dict = field(
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

