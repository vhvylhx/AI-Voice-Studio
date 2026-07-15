from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class DatasetReviewConfig:

    mode: str = "manual"

    default_status: str = "pending"

    report_file: str = "review_report.json"

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
            mode=str(
                data.get(
                    "mode",
                    "manual",
                )
            ),
            default_status=str(
                data.get(
                    "default_status",
                    "pending",
                )
            ),
            report_file=str(
                data.get(
                    "report_file",
                    "review_report.json",
                )
            ),
        )


@dataclass
class DatasetReviewItem:

    source_audio: str = ""

    source_text: str = ""

    reason: str = ""

    suggestion: str = ""

    status: str = "pending"

    code: str = ""

    file: str = ""

    review_required: bool = True

    def to_dict(
        self,
    ):

        return asdict(
            self
        )
