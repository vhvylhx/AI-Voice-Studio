from dataclasses import dataclass, field

from src.models.file_pair import FilePair


@dataclass
class VoiceDataset:

    name: str

    pairs: list[FilePair] = field(default_factory=list)

    docx: int = 0

    txt: int = 0

    mp3: int = 0

    wav: int = 0

    matched: int = 0

    missing_audio: int = 0

    missing_text: int = 0


@dataclass
class WorkspaceModel:

    datasets: list[VoiceDataset] = field(default_factory=list)

    total_docx: int = 0

    total_txt: int = 0

    total_mp3: int = 0

    total_wav: int = 0

    total_match: int = 0

    @property
    def dataset_count(self):

        return len(self.datasets)