from dataclasses import dataclass, field
from pathlib import Path

from models.voice_config import VoiceConfig


@dataclass
class VoiceModel:

    name: str

    path: Path

    avatar: Path

    preview: Path

    config: VoiceConfig = field(
        default_factory=VoiceConfig
    )

    description: str = ""

    status: str = "idle"