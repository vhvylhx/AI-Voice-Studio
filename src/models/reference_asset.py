from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from datetime import datetime


REFERENCE_ASSET_SCHEMA_VERSION = 1


@dataclass
class ReferenceAsset:

    schema_version: int = REFERENCE_ASSET_SCHEMA_VERSION

    asset_id: str = ""

    asset_type: str = ""

    display_name: str = ""

    storage_scope: str = "project"

    managed_relative_path: str = ""

    original_path: str = ""

    original_filename: str = ""

    original_size: int = 0

    checksum: str = ""

    checksum_algorithm: str = "sha256"

    mime_type: str = ""

    extension: str = ""

    duration: float = 0.0

    sample_rate: int = 0

    channels: int = 0

    text_encoding: str = ""

    created_at: str = ""

    updated_at: str = ""

    imported_at: str = ""

    last_verified_at: str = ""

    source_origin: str = ""

    source_project_id: str = ""

    source_voice_id: str = ""

    source_style_profile_id: str = ""

    source_dataset_id: str = ""

    pair_group_id: str = ""

    validation_state: str = "pending"

    validation_messages: list[dict] = field(
        default_factory=list
    )

    provenance: dict = field(
        default_factory=dict
    )

    is_managed: bool = True

    is_external: bool = False

    is_missing: bool = False

    is_corrupt: bool = False

    is_archived: bool = False

    usage: list[dict] = field(
        default_factory=list
    )

    def normalize(
        self,
    ):

        now = datetime.now().isoformat()

        if not self.created_at:

            self.created_at = now

        if not self.updated_at:

            self.updated_at = self.created_at

        if not self.imported_at:

            self.imported_at = self.created_at

        self.original_size = int(
            self.original_size or 0
        )

        self.duration = float(
            self.duration or 0.0
        )

        self.sample_rate = int(
            self.sample_rate or 0
        )

        self.channels = int(
            self.channels or 0
        )

        self.validation_messages = [
            dict(
                item
            )
            for item in self.validation_messages or []
            if isinstance(
                item,
                dict,
            )
        ]

        self.usage = [
            dict(
                item
            )
            for item in self.usage or []
            if isinstance(
                item,
                dict,
            )
        ]

        return self

    def to_dict(
        self,
    ):

        return asdict(
            self.normalize()
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

            return data.normalize()

        data = data or {}

        names = {
            item.name
            for item in fields(cls)
        }

        asset = cls(
            **{
                key: value
                for key, value in data.items()
                if key in names
            }
        )

        return asset.normalize()
