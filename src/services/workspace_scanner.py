from pathlib import Path

from models.file_pair import FilePair
from models.workspace_model import WorkspaceModel
from models.workspace_model import VoiceDataset


class WorkspaceScanner:

    def scan(self, workspace):

        workspace = Path(workspace)

        model = WorkspaceModel()

        if not workspace.exists():
            return model

        for folder in workspace.iterdir():

            if not folder.is_dir():
                continue

            dataset = VoiceDataset(folder.name)

            mapping = {}

            for file in folder.iterdir():

                if not file.is_file():
                    continue

                stem = file.stem

                if stem not in mapping:
                    mapping[stem] = FilePair(stem)

                pair = mapping[stem]

                ext = file.suffix.lower()

                if ext == ".docx":
                    pair.docx = True
                    dataset.docx += 1
                    model.total_docx += 1

                elif ext == ".txt":
                    pair.txt = True
                    dataset.txt += 1
                    model.total_txt += 1

                elif ext == ".mp3":
                    pair.mp3 = True
                    dataset.mp3 += 1
                    model.total_mp3 += 1

                elif ext == ".wav":
                    pair.wav = True
                    dataset.wav += 1
                    model.total_wav += 1

            dataset.pairs = sorted(mapping.values(), key=lambda x: x.name)

            for pair in dataset.pairs:

                if pair.matched:
                    dataset.matched += 1
                    model.total_match += 1

                elif pair.has_text:
                    dataset.missing_audio += 1

                elif pair.has_audio:
                    dataset.missing_text += 1

            model.datasets.append(dataset)

        return model