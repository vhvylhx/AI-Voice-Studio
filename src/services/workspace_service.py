from pathlib import Path

from services.workspace_scanner import WorkspaceScanner


class WorkspaceService:

    def __init__(self):

        self.workspace = Path("workspace")

        self.scanner = WorkspaceScanner()

    def set_workspace(self, path):

        self.workspace = Path(path)

    def get_workspace(self):

        return str(self.workspace)

    def load(self):

        return self.scanner.scan(self.workspace)

    def scan(self):

        model = self.load()

        return {
            "voices": model.dataset_count,
            "docx": model.total_docx,
            "txt": model.total_txt,
            "audio": model.total_mp3 + model.total_wav,
        }