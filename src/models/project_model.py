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