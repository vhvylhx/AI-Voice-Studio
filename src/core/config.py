import json
from pathlib import Path

from .app_info import SETTINGS_FILE
from .app_paths import AppPaths


class Config:

    def __init__(self):
        AppPaths.ensure()

        self.file = AppPaths.SETTINGS / SETTINGS_FILE

        self.data = {
            "theme": "light",
            "language": "vi",
            "workspace": str(AppPaths.WORKSPACE),
            "output": str(AppPaths.OUTPUT),
            "style_profiles": str(AppPaths.STYLE_PROFILES),
            "voice": "",
            "engine": "GPT-SoVITS",
            "model": "",
            "remember_last_voice": True,
            "remember_last_project": True,
            "local_api_enabled": False,
            "local_api_host": "127.0.0.1",
            "local_api_port": 8765,
            "local_api_token": "",
            "local_api_auto_start": False,
            "allowed_origins": [],
            "output_access_policy": "managed_output_only",
            "local_api_concurrency": 1,
        }

        self.load()

    def load(self):
        if self.file.exists():
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except Exception:
                self.save()
        else:
            self.save()

    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                ensure_ascii=False,
                indent=4
            )

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def all(self):
        return self.data
