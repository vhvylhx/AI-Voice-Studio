from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class LocalApiConfig:

    local_api_enabled: bool = False

    local_api_host: str = "127.0.0.1"

    local_api_port: int = 8765

    local_api_token: str = ""

    local_api_auto_start: bool = False

    allowed_origins: list[str] = field(
        default_factory=list
    )

    output_access_policy: str = "managed_output_only"

    concurrency: int = 1

    def to_dict(
        self,
        include_token=True,
    ):

        data = asdict(
            self
        )

        if not include_token:

            data.pop(
                "local_api_token",
                None,
            )

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

        data = data or {}

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in cls.__dataclass_fields__
            }
        )
