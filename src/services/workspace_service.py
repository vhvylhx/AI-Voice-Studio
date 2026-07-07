from pathlib import Path

from src.core import App
from src.events import bus, Events

from .base_service import BaseService


class WorkspaceService(BaseService):

    AUDIO_EXT = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

    TEXT_EXT = {".docx", ".txt"}

    def __init__(self):
        super().__init__(App)

        self.cache = {}

    def scan(self):

        workspace = Path(
            self.app.config.get("workspace")
        )

        result = {
            "voices": 0,
            "audio": 0,
            "docx": 0,
            "txt": 0
        }

        if not workspace.exists():
            self.cache = result
            return result

        for folder in workspace.iterdir():

            if not folder.is_dir():
                continue

            result["voices"] += 1

            for file in folder.rglob("*"):

                if not file.is_file():
                    continue

                ext = file.suffix.lower()

                if ext in self.AUDIO_EXT:
                    result["audio"] += 1

                elif ext == ".docx":
                    result["docx"] += 1

                elif ext == ".txt":
                    result["txt"] += 1

        self.cache = result

        bus.emit(
            Events.WORKSPACE_CHANGED,
            result
        )

        return result

    def get_cache(self):
        return self.cache