from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from datetime import datetime


@dataclass
class AudioTextPair:

    pair_id: str = ""

    audio_asset_id: str = ""

    text_asset_id: str = ""

    audio_checksum: str = ""

    text_checksum: str = ""

    original_audio_stem: str = ""

    original_text_stem: str = ""

    normalized_stem: str = ""

    order_index: int = 0

    validation_state: str = "valid"

    validation_messages: list[dict] = field(
        default_factory=list
    )

    source_project_id: str = ""

    source_origin: str = ""

    created_at: str = ""

    def to_dict(
        self,
    ):

        if not self.created_at:

            self.created_at = datetime.now().isoformat()

        return asdict(
            self
        )

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        names = {
            item.name
            for item in fields(cls)
        }

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in names
            }
        )


@dataclass
class AudioTextManifest:

    manifest_id: str = ""

    pair_ids: list[str] = field(
        default_factory=list
    )

    pairs: list[AudioTextPair] = field(
        default_factory=list
    )

    created_at: str = ""

    schema_version: int = 1

    source_folder_metadata: dict = field(
        default_factory=dict
    )

    validation_summary: dict = field(
        default_factory=dict
    )

    missing_audio: list[dict] = field(
        default_factory=list
    )

    missing_text: list[dict] = field(
        default_factory=list
    )

    duplicate_stem: list[dict] = field(
        default_factory=list
    )

    checksum_summary: dict = field(
        default_factory=dict
    )

    def to_dict(
        self,
    ):

        if not self.created_at:

            self.created_at = datetime.now().isoformat()

        if not self.pair_ids:

            self.pair_ids = [
                pair.pair_id
                for pair in self.pairs
            ]

        return {
            "manifest_id": self.manifest_id,
            "pair_ids": list(
                self.pair_ids
            ),
            "pairs": [
                pair.to_dict()
                for pair in self.pairs
            ],
            "created_at": self.created_at,
            "schema_version": self.schema_version,
            "source_folder_metadata": dict(
                self.source_folder_metadata
            ),
            "validation_summary": dict(
                self.validation_summary
            ),
            "missing_audio": list(
                self.missing_audio
            ),
            "missing_text": list(
                self.missing_text
            ),
            "duplicate_stem": list(
                self.duplicate_stem
            ),
            "checksum_summary": dict(
                self.checksum_summary
            ),
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        pairs = [
            AudioTextPair.from_dict(
                item
            )
            for item in data.get(
                "pairs",
                []
            )
        ]

        return cls(
            manifest_id=str(
                data.get(
                    "manifest_id",
                    "",
                )
            ),
            pair_ids=list(
                data.get(
                    "pair_ids",
                    []
                )
            ),
            pairs=pairs,
            created_at=str(
                data.get(
                    "created_at",
                    "",
                )
            ),
            schema_version=int(
                data.get(
                    "schema_version",
                    1,
                )
                or 1
            ),
            source_folder_metadata=dict(
                data.get(
                    "source_folder_metadata",
                    {},
                )
            ),
            validation_summary=dict(
                data.get(
                    "validation_summary",
                    {},
                )
            ),
            missing_audio=list(
                data.get(
                    "missing_audio",
                    [],
                )
            ),
            missing_text=list(
                data.get(
                    "missing_text",
                    [],
                )
            ),
            duplicate_stem=list(
                data.get(
                    "duplicate_stem",
                    [],
                )
            ),
            checksum_summary=dict(
                data.get(
                    "checksum_summary",
                    {},
                )
            ),
        )
