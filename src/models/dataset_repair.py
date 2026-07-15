from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict


@dataclass
class DatasetRepairConfig:

    auto_repair: bool = True

    review_mode: str = "auto"

    ignored_folder: str = "ignored"

    report_file: str = "dataset_repair_report.json"

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
            auto_repair=bool(
                data.get(
                    "auto_repair",
                    True,
                )
            ),
            review_mode=str(
                data.get(
                    "review_mode",
                    "auto",
                )
            ),
            ignored_folder=str(
                data.get(
                    "ignored_folder",
                    "ignored",
                )
            ),
            report_file=str(
                data.get(
                    "report_file",
                    "dataset_repair_report.json",
                )
            ),
        )


@dataclass
class DatasetRepairIssue:

    code: str

    file: str

    reason: str

    suggestion: str = ""

    repairable: bool = False

    action: str = "pending"

    repaired_file: str = ""

    metadata: Dict = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )
