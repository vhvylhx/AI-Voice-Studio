from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields

from models.reference_asset import ReferenceAsset


@dataclass
class ReferenceRegistryEntry:

    asset_id: str = ""

    asset_type: str = ""

    managed_relative_path: str = ""

    checksum: str = ""

    checksum_algorithm: str = "sha256"

    original_filename: str = ""

    storage_scope: str = "project"

    validation_state: str = "pending"

    last_verified_at: str = ""

    is_archived: bool = False

    usage_count: int = 0

    usage: list[dict] = field(
        default_factory=list
    )

    @classmethod
    def from_asset(
        cls,
        asset,
    ):

        asset = ReferenceAsset.from_dict(
            asset
        )

        return cls(
            asset_id=asset.asset_id,
            asset_type=asset.asset_type,
            managed_relative_path=asset.managed_relative_path,
            checksum=asset.checksum,
            checksum_algorithm=asset.checksum_algorithm,
            original_filename=asset.original_filename,
            storage_scope=asset.storage_scope,
            validation_state=asset.validation_state,
            last_verified_at=asset.last_verified_at,
            is_archived=asset.is_archived,
            usage_count=len(
                asset.usage or []
            ),
            usage=list(
                asset.usage or []
            ),
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

    def to_dict(
        self,
    ):

        return asdict(
            self
        )


@dataclass
class ReferenceRegistry:

    schema_version: int = 1

    entries: list[ReferenceRegistryEntry] = field(
        default_factory=list
    )

    updated_at: str = ""

    def to_dict(
        self,
    ):

        return {
            "schema_version": self.schema_version,
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = data or {}

        return cls(
            schema_version=int(
                data.get(
                    "schema_version",
                    1,
                )
                or 1
            ),
            entries=[
                ReferenceRegistryEntry.from_dict(
                    item
                )
                for item in data.get(
                    "entries",
                    []
                )
            ],
            updated_at=str(
                data.get(
                    "updated_at",
                    "",
                )
            ),
        )
