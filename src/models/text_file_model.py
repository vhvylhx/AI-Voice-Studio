from dataclasses import dataclass
from pathlib import Path


@dataclass
class TextFileModel:

    name: str

    path: Path

    extension: str

    output: Path | None = None

    status: str = "waiting"

    selected: bool = True