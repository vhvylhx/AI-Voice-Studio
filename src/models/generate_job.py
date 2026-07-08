from dataclasses import dataclass
from pathlib import Path

from models.voice_model import VoiceModel


@dataclass
class GenerateJob:

    text_file: Path

    output_file: Path

    voice: VoiceModel

    engine: str

    status: str = "waiting"

    progress: int = 0

    error: str = ""