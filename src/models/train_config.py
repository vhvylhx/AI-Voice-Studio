from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass
class TrainConfig:

    validation_only: bool = True

    smoke_test: bool = False

    run_id: str = ""

    metadata_path: str = ""

    review_report_path: str = ""

    runtime_profile_id: str = ""

    sample_rate: int = 32000

    batch_size: int | None = None

    epochs: int | None = None

    save_interval: int | None = None

    learning_rate: float | None = None

    num_workers: int | None = None

    checkpoint_policy: str = ""

    resume_policy: str = ""

    pretrained_model_version: str = ""

    require_user_confirmed_params: bool = True

    def ensure_run_id(
        self,
    ):

        if not self.run_id:

            self.run_id = uuid4().hex

        return self.run_id

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

    @classmethod
    def from_paths(
        cls,
        metadata_path,
        review_report_path="",
        **kwargs,
    ):

        return cls(
            metadata_path=str(
                Path(
                    metadata_path
                )
            )
            if metadata_path
            else "",
            review_report_path=str(
                Path(
                    review_report_path
                )
            )
            if review_report_path
            else "",
            **kwargs,
        )
