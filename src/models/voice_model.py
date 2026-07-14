from dataclasses import dataclass, field
from pathlib import Path

from models.voice_config import VoiceConfig


@dataclass
class VoiceModel:

    #
    # Basic
    #

    name: str

    path: Path

    avatar: Path

    preview: Path

    description: str = ""

    #
    # Config
    #

    config: VoiceConfig = field(
        default_factory=VoiceConfig
    )

    #
    # Folder
    #

    dataset_dir: Path | None = None

    model_dir: Path | None = None

    export_dir: Path | None = None

    logs_dir: Path | None = None

    #
    # Variant
    #

    variant_dir: Path | None = None

    original_dir: Path | None = None

    soft_dir: Path | None = None

    expressive_dir: Path | None = None

    story_dir: Path | None = None

    bright_dir: Path | None = None

    deep_dir: Path | None = None

    male_a_dir: Path | None = None

    male_b_dir: Path | None = None

    female_a_dir: Path | None = None

    female_b_dir: Path | None = None

    #
    # Runtime
    #

    trained: bool = False

    status: str = "idle"

    progress: int = 0

    last_error: str = ""

    #
    # Helper
    #

    @property
    def id(self):

        return self.config.voice_id

    @property
    def variants(self):

        return self.config.variants
