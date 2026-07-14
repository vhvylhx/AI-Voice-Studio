from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class RuntimeProfile:

    profile_id: str

    display_name: str

    engine_version: str = ""

    runtime_path: str = ""

    python_path: str = ""

    hardware_profile: str = ""

    minimum_vram: str = ""

    recommended_vram: str = ""

    status: str = "unknown"

    is_default: bool = False

    pretrained_model_path: str = ""

    compatibility_notes: str = ""

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
