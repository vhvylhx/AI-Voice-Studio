from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class TrainJobState:

    run_id: str

    voice_id: str

    status: str = "pending"

    checkpoint: str = ""

    model_output: str = ""

    report_path: str = ""

    resume_allowed: bool = False

    resume_confirmed: bool = False

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
