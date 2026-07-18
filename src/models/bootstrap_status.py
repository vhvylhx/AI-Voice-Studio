from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class SetupIssue:

    component: str = ""

    status: str = "missing"

    message_vi: str = ""

    remediation: list[str] = field(
        default_factory=list
    )

    critical: bool = False

    def to_dict(
        self,
    ):

        return asdict(
            self
        )


@dataclass
class BootstrapStatus:

    mode: str = "setup_required"

    can_start_main_app: bool = False

    limited_mode: bool = False

    issues: list[SetupIssue] = field(
        default_factory=list
    )

    technical_details: dict = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        data = asdict(
            self
        )

        data["issues"] = [
            issue.to_dict()
            if hasattr(
                issue,
                "to_dict",
            )
            else issue
            for issue in self.issues
        ]

        return data
