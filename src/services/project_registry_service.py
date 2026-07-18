import json
from pathlib import Path

from models.project_registry import ProjectRegistry
from models.project_registry import ProjectRegistryEntry


class ProjectRegistryService:

    def __init__(
        self,
        root="projects",
        file_name="project_registry.json",
    ):

        self.root = Path(
            root
        )

        self.file_name = file_name

    @property
    def file(
        self,
    ):

        return self.root / self.file_name

    def load(
        self,
    ):

        if not self.file.exists():

            return ProjectRegistry()

        try:

            return ProjectRegistry.from_dict(
                json.loads(
                    self.file.read_text(
                        encoding="utf-8"
                    )
                )
            )

        except Exception:

            backup = self.file.with_suffix(
                ".corrupt.json"
            )

            if not backup.exists():

                backup.write_text(
                    self.file.read_text(
                        encoding="utf-8",
                        errors="replace",
                    ),
                    encoding="utf-8",
                )

            return ProjectRegistry()

    def save(
        self,
        registry,
    ):

        registry = ProjectRegistry.from_dict(
            registry.to_dict()
            if hasattr(
                registry,
                "to_dict",
            )
            else registry
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = self.file.with_suffix(
            ".tmp"
        )

        temp.write_text(
            json.dumps(
                registry.to_dict(),
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temp.replace(
            self.file
        )

        return registry

    def sync_from_projects(
        self,
        projects,
    ):

        registry = self.load()

        entries = {
            entry.project_id: entry
            for entry in registry.entries
        }

        seen = set()

        for project in projects:

            entry = entries.get(
                project.id,
                ProjectRegistryEntry(
                    project_id=project.id,
                ),
            )

            entry.display_name = project.display_name
            entry.root_path = str(
                project.path
            )
            entry.status = project.config.status
            entry.archive_state = project.config.archive_state
            entry.last_opened_at = project.config.last_opened_at
            entry.favorite = bool(
                project.config.favorite
            )
            entry.health_state = project.config.health_state
            entry.missing = not Path(
                project.path
            ).exists()

            entries[project.id] = entry
            seen.add(
                project.id
            )

        for project_id, entry in entries.items():

            if project_id not in seen and entry.root_path:

                entry.missing = not Path(
                    entry.root_path
                ).exists()

        registry.entries = sorted(
            entries.values(),
            key=lambda item: (
                item.display_name.lower(),
                item.project_id,
            ),
        )

        return self.save(
            registry
        )

    def upsert(
        self,
        project,
    ):

        registry = self.load()

        kept = [
            entry
            for entry in registry.entries
            if entry.project_id != project.id
        ]

        kept.append(
            ProjectRegistryEntry(
                project_id=project.id,
                display_name=project.display_name,
                root_path=str(
                    project.path
                ),
                status=project.config.status,
                archive_state=project.config.archive_state,
                last_opened_at=project.config.last_opened_at,
                favorite=bool(
                    project.config.favorite
                ),
                health_state=project.config.health_state,
                missing=not Path(
                    project.path
                ).exists(),
            )
        )

        registry.entries = kept

        return self.save(
            registry
        )

    def mark_recent(
        self,
        project,
        limit=20,
    ):

        registry = self.load()

        ids = [
            item
            for item in registry.recent_project_ids
            if item != project.id
        ]

        ids.insert(
            0,
            project.id,
        )

        registry.recent_project_ids = ids[:limit]
        registry.current_project_id = project.id

        self.save(
            registry
        )

        self.upsert(
            project
        )

        return self.load()
