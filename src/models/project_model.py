from dataclasses import dataclass, field
from pathlib import Path

from models.project_config import ProjectConfig


@dataclass
class ProjectModel:

    name: str

    path: Path

    input_dir: Path

    output_dir: Path

    cache_dir: Path

    log_dir: Path

    config: ProjectConfig = field(
        default_factory=ProjectConfig
    )

    status: str = "idle"

    progress: int = 0

    @property
    def id(self):

        return self.config.project_id

    @property
    def display_name(self):

        return (
            self.config.display_name
            or self.name
        )

    @property
    def is_archived(self):

        return (
            self.config.archive_state == "archived"
            or self.config.status == "archived"
        )

    @property
    def health_state(self):

        return self.config.health_state

    @property
    def export_dir(self):

        return self.path / self.config.export_folder

    @property
    def text_dir(self):

        return self.input_dir

    @property
    def audio_dir(self):

        return self.output_dir
