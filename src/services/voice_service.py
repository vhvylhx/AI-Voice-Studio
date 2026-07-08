import json
from pathlib import Path

from core.app_context import AppContext

from models.voice_config import VoiceConfig
from models.voice_model import VoiceModel


class VoiceService:

    def root(self):

        project = AppContext.current_project.get()

        root = project.path / "voices"

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        return root

    def create(self, name):

        voice = self.root() / name

        voice.mkdir(
            parents=True,
            exist_ok=True
        )

        config = VoiceConfig()

        with open(
            voice / "voice.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config.__dict__,
                f,
                indent=4,
                ensure_ascii=False
            )

        return self.load(name)

    def load(self, name):

        folder = self.root() / name

        with open(
            folder / "voice.json",
            "r",
            encoding="utf-8"
        ) as f:

            config = VoiceConfig(
                **json.load(f)
            )

        return VoiceModel(
            name=name,
            path=folder,
            avatar=folder / "avatar.png",
            preview=folder / "preview.wav",
            config=config,
        )

    def save(self, voice):

        with open(
            voice.path / "voice.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                voice.config.__dict__,
                f,
                indent=4,
                ensure_ascii=False
            )

    def list(self):

        result = []

        for folder in self.root().iterdir():

            if not folder.is_dir():
                continue

            if (folder / "voice.json").exists():

                result.append(folder.name)

        return sorted(result)

    def exists(self, name):

        return (
            self.root() / name
        ).exists()

    def delete(self, name):

        import shutil

        folder = self.root() / name

        if folder.exists():

            shutil.rmtree(folder)

    def rename(
        self,
        old_name,
        new_name
    ):

        old = self.root() / old_name

        new = self.root() / new_name

        if old.exists():

            old.rename(new)