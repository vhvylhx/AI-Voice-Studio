from dataclasses import dataclass
from pathlib import Path


@dataclass
class QueueItem:

    dataset: str

    text_file: Path

    audio_file: Path

    output_file: Path

    status: str = "waiting"

    progress: int = 0

    message: str = ""