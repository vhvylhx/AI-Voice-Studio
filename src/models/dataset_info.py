from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatasetInfo:
    name: str
    path: Path
    mp3_count: int
    docx_count: int
    txt_count: int