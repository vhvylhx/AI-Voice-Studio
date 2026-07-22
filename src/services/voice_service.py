import json
from pathlib import Path
import unicodedata

from models.voice_config import VoiceConfig
from services.engine_language_router import EngineLanguageRouter
from models.voice_model import VoiceModel


class VoiceService:

    def __init__(self):

        self._root = Path(
            "voices"
        )

        self._root.mkdir(
            parents=True,
            exist_ok=True
        )

    def root(self):

        return self._root

    def create(
        self,
        name,
    ):

        name = self.normalize_display_name(
            name
        )

        errors = self.validate_display_name(
            name
        )

        if errors:

            raise ValueError(
                ",".join(
                    errors
                )
            )

        voice = self.root() / name

        voice.mkdir(
            parents=True,
            exist_ok=True
        )

        config = VoiceConfig()

        config.voice_id = self.next_id()

        self.ensure_folders(
            voice
        )

        self.save_config(
            voice,
            config,
        )

        return self.load(
            name
        )

    def load(
        self,
        name,
    ):

        folder = self.root() / name

        with open(
            folder / "voice.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            config = VoiceConfig.from_dict(
                data
            )

        migrated = False

        if not data.get(
            "voice_id"
        ):

            config.voice_id = self.next_id(
                exclude=name
            )

            migrated = True

        if not data.get(
            "variants"
        ):

            migrated = True

        model = VoiceModel(
            name=name,
            path=folder,
            avatar=folder / "avatar.png",
            preview=folder / "preview.wav",
            config=config,
        )

        model.dataset_dir = (
            folder / "dataset"
        )

        model.model_dir = (
            folder / "model"
        )

        model.logs_dir = (
            folder / "logs"
        )

        model.export_dir = (
            folder / "export"
        )

        self.ensure_folders(
            folder
        )

        if migrated:

            self.save(
                model
            )

        model.trained = (
            model.preview.exists()
            and config.gpt_model
            and config.sovits_model
        )

        return model

    def save(
        self,
        voice,
    ):

        self.save_config(
            voice.path,
            voice.config,
        )

    def save_config(
        self,
        folder,
        config,
    ):

        with open(
            folder / "voice.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config.to_dict(),
                f,
                indent=4,
                ensure_ascii=False
            )

    def list(self):

        result = []

        for folder in self.root().iterdir():

            if not folder.is_dir():

                continue

            if (
                folder / "voice.json"
            ).exists():

                result.append(
                    folder.name
                )

        return sorted(
            result
        )

    def exists(
        self,
        name,
    ):

        return (
            self.root() / name
        ).exists()

    def delete(
        self,
        name,
    ):

        import shutil

        folder = (
            self.root() / name
        )

        if folder.exists():

            shutil.rmtree(
                folder
            )

    def rename(
        self,
        old_name,
        new_name,
    ):

        new_name = self.normalize_display_name(
            new_name
        )

        errors = self.validate_display_name(
            new_name
        )

        if errors:

            raise ValueError(
                ",".join(
                    errors
                )
            )

        if old_name == new_name:

            return self.load(
                old_name
            )

        old = (
            self.root() / old_name
        )

        new = (
            self.root() / new_name
        )

        if old.exists():

            if new.exists():

                raise ValueError(
                    "voice_name_duplicate"
                )

            voice = self.load(
                old_name
            )

            voice_id = voice.id

            old.rename(
                new
            )

            voice.name = new_name

            voice.path = new

            voice.avatar = (
                new / "avatar.png"
            )

            voice.preview = (
                new / "preview.wav"
            )

            self.save(
                voice
            )

            reloaded = self.load(
                new_name
            )

            if reloaded.id != voice_id:

                raise RuntimeError(
                    "voice_id_changed_after_rename"
                )

            return reloaded

        raise FileNotFoundError(
            old
        )

    def normalize_display_name(
        self,
        name,
    ):

        return unicodedata.normalize(
            "NFC",
            str(
                name or ""
            ).strip(),
        )

    def validate_display_name(
        self,
        name,
    ):

        errors = []

        if not name:

            errors.append(
                "voice_name_required"
            )

        if len(
            name
        ) > 120:

            errors.append(
                "voice_name_too_long"
            )

        if any(
            ord(
                char
            )
            < 32
            for char in name
        ):

            errors.append(
                "voice_name_control_character"
            )

        if any(
            char in name
            for char in (
                "\\",
                "/",
                ":",
                "*",
                "?",
                '"',
                "<",
                ">",
                "|",
            )
        ):

            errors.append(
                "voice_name_unsafe_character"
            )

        return errors

    def ensure_folders(
        self,
        folder,
    ):

        (folder / "dataset").mkdir(
            exist_ok=True
        )

        (folder / "model").mkdir(
            exist_ok=True
        )

        (folder / "logs").mkdir(
            exist_ok=True
        )

        (folder / "export").mkdir(
            exist_ok=True
        )

    def link_engine(
        self,
        voice,
        engine_id,
        engine_path="",
    ):

        errors = EngineLanguageRouter().validate_binding(
            getattr(
                voice.config,
                "language",
                "",
            ),
            engine_id,
        )

        if errors:

            raise RuntimeError(
                ",".join(
                    errors
                )
            )

        voice.config.engine = engine_id

        if engine_path:

            voice.config.engine_path = str(
                engine_path
            )

        self.save(
            voice
        )

        return voice

    def link_gpt_sovits(
        self,
        voice,
        engine_path="",
    ):

        return self.link_engine(
            voice=voice,
            engine_id="gpt_sovits",
            engine_path=engine_path,
        )

    def validate_gpt_sovits(
        self,
        voice,
    ):

        config = voice.config

        missing = []

        files = [
            (
                "gpt_model",
                config.gpt_model,
                {
                    ".ckpt",
                },
            ),
            (
                "sovits_model",
                config.sovits_model,
                {
                    ".pth",
                },
            ),
            (
                "reference_audio",
                config.reference_audio,
                {
                    ".wav",
                    ".mp3",
                    ".flac",
                    ".m4a",
                },
            ),
        ]

        for name, value, suffixes in files:

            if not str(value).strip():

                missing.append(
                    name
                )

                continue

            file = Path(value)

            if not file.exists():

                missing.append(
                    name
                )

                continue

            if file.suffix.lower() not in suffixes:

                missing.append(
                    name
                )

        if not str(
            config.reference_text
        ).strip():

            missing.append(
                "reference_text"
            )

        return {
            "voice_id": voice.id,
            "voice_name": voice.name,
            "engine": config.engine,
            "ready": not missing,
            "missing": missing,
        }

    def next_id(
        self,
        exclude=None,
    ):

        used = set()

        for name in self.list():

            if name == exclude:

                continue

            file = (
                self.root()
                / name
                / "voice.json"
            )

            if not file.exists():

                continue

            try:

                data = json.loads(
                    file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue

            voice_id = data.get(
                "voice_id",
                "",
            )

            if voice_id:

                used.add(
                    voice_id
                )

        index = 1

        while True:

            voice_id = f"{index:04d}"

            if voice_id not in used:

                return voice_id

            index += 1


## ===== KẾT THÚC FILE =====
