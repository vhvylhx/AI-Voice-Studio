from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field


@dataclass
class ProjectRegistryEntry:

    project_id: str = ""

    display_name: str = ""

    root_path: str = ""

    status: str = "active"

    archive_state: str = "active"

    last_opened_at: str = ""

    favorite: bool = False

    health_state: str = "unknown"

    missing: bool = False

    schema_version: int = 1

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


@dataclass
class ProjectRegistry:

    schema_version: int = 1

    current_project_id: str = ""

    recent_project_ids: list[str] = field(
        default_factory=list
    )

    entries: list[ProjectRegistryEntry] = field(
        default_factory=list
    )

    def to_dict(
        self,
    ):

        return {
            "schema_version": self.schema_version,
            "current_project_id": self.current_project_id,
            "recent_project_ids": list(
                self.recent_project_ids
            ),
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
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
            ),
            current_project_id=str(
                data.get(
                    "current_project_id",
                    "",
                )
            ),
            recent_project_ids=list(
                data.get(
                    "recent_project_ids",
                    [],
                )
            ),
            entries=[
                ProjectRegistryEntry.from_dict(
                    item
                )
                for item in data.get(
                    "entries",
                    []
                )
            ],
        )
