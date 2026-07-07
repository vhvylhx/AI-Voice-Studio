from pathlib import Path
import json


class BaseRepository:

    def __init__(self, file_path):
        self.file = Path(file_path)

    def load(self, default=None):
        if default is None:
            default = {}

        if not self.file.exists():
            return default

        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def save(self, data):
        self.file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )