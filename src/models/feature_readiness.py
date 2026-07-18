from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


STATUS_AVAILABLE = "available"
STATUS_DEGRADED = "degraded"
STATUS_BLOCKED = "blocked"


@dataclass
class FeatureReadiness:

    feature_id: str = ""

    name_vi: str = ""

    status: str = STATUS_BLOCKED

    available: bool = False

    degraded: bool = False

    blocked: bool = True

    required_components: list[str] = field(
        default_factory=list
    )

    missing_components: list[str] = field(
        default_factory=list
    )

    remediation: list[str] = field(
        default_factory=list
    )

    settings_target: str = ""

    technical_details: dict = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        return asdict(
            self
        )
