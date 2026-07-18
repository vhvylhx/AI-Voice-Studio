import json
import shutil
from datetime import datetime
from pathlib import Path

from core.app_paths import AppPaths
from models.style_profile import STYLE_PROFILE_SCHEMA_VERSION
from models.style_profile import STYLE_STATUS_ARCHIVED
from models.style_profile import STYLE_STATUS_DEGRADED
from models.style_profile import STYLE_STATUS_INVALID
from models.style_profile import StyleProfile


class StyleProfileRepository:

    PROFILE_FILE = "style_profile.json"

    def __init__(
        self,
        root=None,
    ):

        self.root = Path(
            root or AppPaths.STYLE_PROFILES
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create(
        self,
        profile,
    ):

        profile = StyleProfile.from_dict(
            profile.to_dict()
            if hasattr(
                profile,
                "to_dict",
            )
            else profile
        )

        if not profile.style_profile_id:

            profile.style_profile_id = self.next_id()

        self.validate_profile(
            profile
        )

        folder = self.profile_dir(
            profile.style_profile_id
        )

        if folder.exists():

            raise ValueError(
                "style_profile_exists"
            )

        self.ensure_structure(
            folder
        )

        self.atomic_write_json(
            folder / self.PROFILE_FILE,
            profile.to_dict(),
        )

        self.write_manifest(
            profile.style_profile_id
        )

        return profile

    def load(
        self,
        style_profile_id,
    ):

        file = self.profile_file(
            style_profile_id
        )

        if not file.exists():

            raise FileNotFoundError(
                file
            )

        try:

            data = json.loads(
                file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            profile = StyleProfile(
                style_profile_id=style_profile_id,
                display_name=style_profile_id,
                status=STYLE_STATUS_INVALID,
            )

            profile.integrity["invalid_files"] = [
                self.PROFILE_FILE
            ]

            return profile

        profile = self.migrate(
            data
        )

        if profile.schema_version != data.get(
            "schema_version",
            STYLE_PROFILE_SCHEMA_VERSION,
        ):

            self.backup_file(
                file
            )

            self.atomic_write_json(
                file,
                profile.to_dict(),
            )

        return profile

    def update(
        self,
        profile,
        backup=True,
    ):

        profile = StyleProfile.from_dict(
            profile.to_dict()
            if hasattr(
                profile,
                "to_dict",
            )
            else profile
        )

        self.validate_profile(
            profile
        )

        file = self.profile_file(
            profile.style_profile_id
        )

        if backup and file.exists():

            self.backup_file(
                file
            )

        self.ensure_structure(
            self.profile_dir(
                profile.style_profile_id
            )
        )

        self.atomic_write_json(
            file,
            profile.to_dict(),
        )

        self.write_manifest(
            profile.style_profile_id
        )

        return profile

    def list(
        self,
        include_archived=False,
    ):

        result = []

        if not self.root.exists():

            return result

        for folder in self.root.iterdir():

            if not folder.is_dir():

                continue

            if not (
                folder / self.PROFILE_FILE
            ).exists():

                continue

            profile = self.load(
                folder.name
            )

            if (
                profile.status == STYLE_STATUS_ARCHIVED
                and not include_archived
            ):

                continue

            result.append(
                profile
            )

        return sorted(
            result,
            key=lambda item: item.style_profile_id,
        )

    def archive(
        self,
        style_profile_id,
    ):

        profile = self.load(
            style_profile_id
        )

        profile.status = STYLE_STATUS_ARCHIVED

        profile.updated_at = datetime.now().isoformat()

        return self.update(
            profile
        )

    def exists(
        self,
        style_profile_id,
    ):

        return self.profile_file(
            style_profile_id
        ).exists()

    def next_id(
        self,
    ):

        used = {
            profile.style_profile_id
            for profile in self.list(
                include_archived=True
            )
        }

        index = 1

        while True:

            style_profile_id = f"style_{index:06d}"

            if style_profile_id not in used:

                return style_profile_id

            index += 1

    def migrate(
        self,
        data,
    ):

        schema_version = int(
            data.get(
                "schema_version",
                0,
            )
            or 0
        )

        if schema_version > STYLE_PROFILE_SCHEMA_VERSION:

            profile = StyleProfile.from_dict(
                data
            )

            profile.status = STYLE_STATUS_DEGRADED

            profile.integrity["invalid_files"] = [
                "schema_newer_than_app"
            ]

            return profile

        data = dict(
            data
        )

        data["schema_version"] = STYLE_PROFILE_SCHEMA_VERSION

        return StyleProfile.from_dict(
            data
        )

    def validate_profile(
        self,
        profile,
    ):

        errors = profile.validate()

        if errors:

            raise ValueError(
                ",".join(
                    errors
                )
            )

        safe = self.safe_id(
            profile.style_profile_id
        )

        if safe != profile.style_profile_id:

            raise ValueError(
                "style_profile_id_unsafe"
            )

    def ensure_structure(
        self,
        folder,
    ):

        for name in [
            "prosody",
            "indexes",
            "references",
            "references/optional_selected_clips",
            "cache",
            "export",
            "logs",
            "backups",
        ]:

            (
                Path(
                    folder
                )
                / name
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

        placeholder_files = {
            "prosody/pause_profile.json": {},
            "prosody/rhythm_profile.json": {},
            "prosody/punctuation_profile.json": {},
            "prosody/intonation_profile.json": {},
            "prosody/emphasis_profile.json": {},
            "prosody/breathing_profile.json": {},
            "prosody/reading_fingerprint.json": {},
            "indexes/reference_index.json": {},
            "indexes/sentence_index.json": {},
            "indexes/style_clusters.json": {},
            "references/manifest.json": {
                "items": [],
            },
            "extraction_state.json": {
                "status": "pending",
                "message_vi": "Chua chay trich xuat Voice DNA.",
            },
            "extraction_report.json": {
                "status": "pending",
                "items": [],
            },
        }

        for relative, data in placeholder_files.items():

            file = Path(
                folder
            ) / relative

            if not file.exists():

                self.atomic_write_json(
                    file,
                    data,
                )

    def write_manifest(
        self,
        style_profile_id,
    ):

        folder = self.profile_dir(
            style_profile_id
        )

        manifest = {
            "schema_version": 1,
            "style_profile_id": style_profile_id,
            "files": [
                self.PROFILE_FILE,
                "manifest.json",
                "extraction_state.json",
                "extraction_report.json",
                "references/manifest.json",
            ],
            "updated_at": datetime.now().isoformat(),
        }

        self.atomic_write_json(
            folder / "manifest.json",
            manifest,
        )

    def profile_dir(
        self,
        style_profile_id,
    ):

        return self.root / self.safe_id(
            style_profile_id
        )

    def profile_file(
        self,
        style_profile_id,
    ):

        return (
            self.profile_dir(
                style_profile_id
            )
            / self.PROFILE_FILE
        )

    def safe_id(
        self,
        value,
    ):

        return "".join(
            char
            for char in str(
                value
            )
            if char.isalnum()
            or char in (
                "_",
                "-",
            )
        )

    def backup_file(
        self,
        file,
    ):

        file = Path(
            file
        )

        if not file.exists():

            return None

        backup_dir = file.parent / "backups"

        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        target = backup_dir / f"{file.name}.{timestamp}.bak"

        shutil.copy2(
            file,
            target,
        )

        return target

    def atomic_write_json(
        self,
        file,
        data,
    ):

        file = Path(
            file
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = file.with_suffix(
            file.suffix + ".tmp"
        )

        with open(
            temp,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                data,
                handle,
                ensure_ascii=False,
                indent=4,
            )

            handle.flush()

        temp.replace(
            file
        )

