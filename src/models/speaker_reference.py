from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class SpeakerReference:

    source_mode: str = "none"

    audio_asset_id: str = ""

    text_asset_id: str = ""

    selected_segment_id: str = ""

    audio_path: str = ""

    text: str = ""

    folder: str = ""

    source_origin: str = ""

    checksum_snapshot: dict = field(
        default_factory=dict
    )

    legacy_path: str = ""

    state: str = "pending"

    messages: list[dict] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

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
