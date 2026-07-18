import hashlib
import json
import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models.reference_asset import ReferenceAsset
from services.reference_registry_service import ReferenceRegistryService


class ReferenceVaultService:

    FOLDERS = [
        "audio",
        "text",
        "manifests",
        "pairs",
        "segments",
        "reports",
        "style_sources",
        "speaker_references",
        "normalized",
        "registry",
        "temp",
    ]

    AUDIO_TYPES = {
        "speaker_reference_audio",
        "training_reference_audio",
        "style_source_audio",
        "normalized_audio",
        "dataset_reference_segment",
    }

    TEXT_TYPES = {
        "speaker_reference_text",
        "training_reference_text",
        "style_source_text",
        "transcript",
    }

    def __init__(
        self,
        vault_root="workspace/reference_vault",
        registry_service=None,
    ):

        self.vault_root = Path(
            vault_root
        )

        self.registry_service = (
            registry_service
            or ReferenceRegistryService(
                self.vault_root
            )
        )

        self.ensure_structure()

    def ensure_structure(
        self,
    ):

        for folder in self.FOLDERS:

            (
                self.vault_root / folder
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

    def import_file(
        self,
        source_file,
        asset_type,
        display_name="",
        storage_scope="project",
        source_project_id="",
        source_voice_id="",
        source_style_profile_id="",
        source_dataset_id="",
        source_origin="external",
        usage=None,
        deduplicate=True,
    ):

        source_file = Path(
            source_file
        )

        if not source_file.exists() or not source_file.is_file():

            raise FileNotFoundError(
                source_file
            )

        source_size = source_file.stat().st_size

        checksum = self.sha256(
            source_file
        )

        if deduplicate:

            existing = self.registry_service.find_by_checksum(
                checksum,
                asset_type=asset_type,
                extension=source_file.suffix.lower(),
            )

            if existing:

                asset = self.load_asset(
                    existing.asset_id
                )

                asset.usage = self.merge_usage(
                    asset.usage,
                    usage,
                )

                asset.updated_at = datetime.now().isoformat()

                self.save_asset(
                    asset
                )

                return {
                    "asset": asset,
                    "deduplicated": True,
                }

        asset_id = self.new_asset_id(
            asset_type
        )

        extension = source_file.suffix.lower()

        relative = self.asset_relative_path(
            asset_type,
            asset_id,
            extension,
        )

        target = self.vault_root / relative

        temp = (
            self.vault_root
            / "temp"
            / f"{asset_id}{extension}.tmp"
        )

        temp.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            shutil.copy2(
                source_file,
                temp,
            )

            if temp.stat().st_size != source_size:

                raise IOError(
                    "import_size_mismatch"
                )

            temp_checksum = self.sha256(
                temp
            )

            if temp_checksum != checksum:

                raise IOError(
                    "import_checksum_mismatch"
                )

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            os.replace(
                temp,
                target,
            )

        except Exception:

            if temp.exists():

                temp.unlink()

            raise

        now = datetime.now().isoformat()

        asset = ReferenceAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            display_name=display_name
            or source_file.name,
            storage_scope=storage_scope,
            managed_relative_path=relative.as_posix(),
            original_path=str(
                source_file
            ),
            original_filename=source_file.name,
            original_size=source_size,
            checksum=checksum,
            checksum_algorithm="sha256",
            mime_type=mimetypes.guess_type(
                source_file.name
            )[0]
            or "",
            extension=extension,
            text_encoding="utf-8"
            if asset_type in self.TEXT_TYPES
            else "",
            created_at=now,
            updated_at=now,
            imported_at=now,
            source_origin=source_origin,
            source_project_id=source_project_id,
            source_voice_id=source_voice_id,
            source_style_profile_id=source_style_profile_id,
            source_dataset_id=source_dataset_id,
            validation_state="valid",
            is_managed=True,
            is_external=False,
            usage=self.merge_usage(
                [],
                usage,
            ),
            provenance={
                "original_path": str(
                    source_file
                ),
                "original_filename": source_file.name,
            },
        )

        self.save_asset(
            asset
        )

        return {
            "asset": asset,
            "deduplicated": False,
        }

    def import_text(
        self,
        text,
        asset_type,
        display_name,
        extension=".txt",
        **kwargs,
    ):

        asset_id = self.new_asset_id(
            asset_type
        )

        extension = extension if extension.startswith(".") else f".{extension}"

        relative = self.asset_relative_path(
            asset_type,
            asset_id,
            extension,
        )

        target = self.vault_root / relative

        temp = (
            self.vault_root
            / "temp"
            / f"{asset_id}{extension}.tmp"
        )

        text = str(
            text or ""
        )

        temp.write_text(
            text,
            encoding="utf-8",
        )

        checksum = self.sha256(
            temp
        )

        existing = self.registry_service.find_by_checksum(
            checksum,
            asset_type=asset_type,
            extension=extension,
        )

        if existing:

            temp.unlink(
                missing_ok=True
            )

            asset = self.load_asset(
                existing.asset_id
            )

            return {
                "asset": asset,
                "deduplicated": True,
            }

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.replace(
            temp,
            target,
        )

        now = datetime.now().isoformat()

        asset = ReferenceAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            display_name=display_name,
            managed_relative_path=relative.as_posix(),
            original_filename=display_name,
            original_size=target.stat().st_size,
            checksum=checksum,
            extension=extension,
            text_encoding="utf-8",
            created_at=now,
            updated_at=now,
            imported_at=now,
            validation_state="valid",
            is_managed=True,
            **kwargs,
        )

        self.save_asset(
            asset
        )

        return {
            "asset": asset,
            "deduplicated": False,
        }

    def save_json_asset(
        self,
        asset_type,
        data,
        display_name,
        folder="manifests",
        source_project_id="",
    ):

        asset_id = self.new_asset_id(
            asset_type
        )

        relative = Path(
            folder
        ) / f"{asset_id}.json"

        target = self.vault_root / relative

        self.atomic_write_json(
            target,
            data,
        )

        checksum = self.sha256(
            target
        )

        now = datetime.now().isoformat()

        asset = ReferenceAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            display_name=display_name,
            managed_relative_path=relative.as_posix(),
            original_filename=display_name,
            original_size=target.stat().st_size,
            checksum=checksum,
            extension=".json",
            mime_type="application/json",
            text_encoding="utf-8",
            created_at=now,
            updated_at=now,
            imported_at=now,
            source_project_id=source_project_id,
            validation_state="valid",
            is_managed=True,
        )

        self.save_asset(
            asset
        )

        return asset

    def load_asset(
        self,
        asset_id,
    ):

        metadata_file = self.asset_metadata_file(
            asset_id
        )

        if not metadata_file.exists():

            raise FileNotFoundError(
                metadata_file
            )

        return ReferenceAsset.from_dict(
            json.loads(
                metadata_file.read_text(
                    encoding="utf-8"
                )
            )
        )

    def resolve_asset_path(
        self,
        asset_id,
    ):

        asset = self.load_asset(
            asset_id
        )

        path = self.vault_root / asset.managed_relative_path

        return path

    def verify_asset(
        self,
        asset_id,
    ):

        asset = self.load_asset(
            asset_id
        )

        path = self.vault_root / asset.managed_relative_path

        messages = []

        if not path.exists():

            asset.is_missing = True
            asset.validation_state = "missing"
            messages.append(
                self.issue(
                    "asset_missing",
                    str(
                        path
                    ),
                    "Managed asset khong ton tai.",
                )
            )

        elif self.sha256(
            path
        ) != asset.checksum:

            asset.is_corrupt = True
            asset.validation_state = "corrupt"
            messages.append(
                self.issue(
                    "checksum_mismatch",
                    str(
                        path
                    ),
                    "Checksum asset khong khop.",
                )
            )

        else:

            asset.is_missing = False
            asset.is_corrupt = False
            asset.validation_state = "valid"
            asset.last_verified_at = datetime.now().isoformat()

        asset.validation_messages = messages

        self.save_asset(
            asset
        )

        return {
            "asset": asset,
            "ok": not messages,
            "messages": messages,
        }

    def relink_external(
        self,
        asset_id,
        new_path,
    ):

        asset = self.load_asset(
            asset_id
        )

        new_path = Path(
            new_path
        )

        if not new_path.exists():

            raise FileNotFoundError(
                new_path
            )

        checksum = self.sha256(
            new_path
        )

        if asset.checksum and checksum != asset.checksum:

            return {
                "ok": False,
                "warning": "checksum_mismatch",
                "asset_id": asset.asset_id,
                "expected": asset.checksum,
                "actual": checksum,
            }

        asset.original_path = str(
            new_path
        )

        asset.provenance[
            "relinked_at"
        ] = datetime.now().isoformat()

        self.save_asset(
            asset
        )

        return {
            "ok": True,
            "asset_id": asset.asset_id,
        }

    def save_asset(
        self,
        asset,
    ):

        asset = ReferenceAsset.from_dict(
            asset
        )

        self.atomic_write_json(
            self.asset_metadata_file(
                asset.asset_id
            ),
            asset.to_dict(),
        )

        self.registry_service.upsert(
            asset
        )

        return asset

    def asset_metadata_file(
        self,
        asset_id,
    ):

        return (
            self.vault_root
            / "registry"
            / "assets"
            / f"{self.safe_id(asset_id)}.json"
        )

    def asset_relative_path(
        self,
        asset_type,
        asset_id,
        extension,
    ):

        if asset_type in self.AUDIO_TYPES:

            folder = "audio"

        elif asset_type in self.TEXT_TYPES:

            folder = "text"

        elif asset_type == "audio_text_manifest":

            folder = "pairs"

        elif asset_type == "selected_segment":

            folder = "segments"

        elif asset_type == "validation_report":

            folder = "reports"

        else:

            folder = "manifests"

        return Path(
            folder
        ) / f"{asset_id}{extension}"

    def new_asset_id(
        self,
        asset_type,
    ):

        prefix = self.safe_id(
            asset_type
        )[:24] or "asset"

        while True:

            asset_id = f"{prefix}_{uuid4().hex[:16]}"

            if not self.asset_metadata_file(
                asset_id
            ).exists():

                return asset_id

    def sha256(
        self,
        file,
    ):

        digest = hashlib.sha256()

        with open(
            file,
            "rb",
        ) as handle:

            for chunk in iter(
                lambda: handle.read(
                    1024 * 1024
                ),
                b"",
            ):

                digest.update(
                    chunk
                )

        return digest.hexdigest()

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
            or char in {
                "_",
                "-",
            }
        )

    def merge_usage(
        self,
        current,
        usage,
    ):

        result = [
            dict(
                item
            )
            for item in current or []
            if isinstance(
                item,
                dict,
            )
        ]

        if isinstance(
            usage,
            dict,
        ):

            marker = json.dumps(
                usage,
                sort_keys=True,
                ensure_ascii=False,
            )

            existing = {
                json.dumps(
                    item,
                    sort_keys=True,
                    ensure_ascii=False,
                )
                for item in result
            }

            if marker not in existing:

                result.append(
                    dict(
                        usage
                    )
                )

        return result

    def issue(
        self,
        code,
        path,
        reason,
    ):

        return {
            "code": code,
            "path": path,
            "reason": reason,
            "suggestion": "Kiem tra Reference Vault hoac restore tu backup.",
        }

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
                indent=4,
                ensure_ascii=False,
            )

            handle.flush()

        temp.replace(
            file
        )
