import json
import shutil
from datetime import datetime
from pathlib import Path


class ProjectBackupService:

    def __init__(
        self,
        backup_root="backups",
    ):

        self.backup_root = Path(
            backup_root
        )

    def backup_project(
        self,
        project,
        reason="manual",
        mode="metadata",
        reference_vault=None,
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        root = Path(
            project.path
        )

        target = self.unique_backup_path(
            root,
            project.id,
            timestamp,
        )

        target.mkdir(
            parents=True,
            exist_ok=False,
        )

        manifest = {
            "schema_version": 1,
            "project_id": project.id,
            "display_name": project.display_name,
            "created_at": datetime.now().isoformat(),
            "reason": reason,
            "mode": mode,
            "contains_media": mode == "complete",
            "files": [],
            "reference_assets": [],
        }

        for name in [
            "project.json",
        ]:

            source = root / name

            if source.exists():

                shutil.copy2(
                    source,
                    target / name,
                )

                manifest["files"].append(
                    name
                )

        if reference_vault is not None:

            self.copy_reference_metadata(
                reference_vault,
                target,
                manifest,
                include_media=mode == "complete",
            )

        (
            target / "backup_manifest.json"
        ).write_text(
            json.dumps(
                manifest,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return {
            "backup_path": str(
                target
            ),
            "manifest": manifest,
        }

    def unique_backup_path(
        self,
        project_root,
        project_id,
        timestamp,
    ):

        base = (
            Path(
                project_root
            )
            / self.backup_root
            / f"{project_id}_{timestamp}"
        )

        if not base.exists():

            return base

        index = 1

        while True:

            candidate = base.with_name(
                f"{base.name}_{index:02d}"
            )

            if not candidate.exists():

                return candidate

            index += 1

    def restore_project(
        self,
        project,
        backup_path,
        reference_vault=None,
    ):

        backup_path = Path(
            backup_path
        )

        manifest_file = backup_path / "backup_manifest.json"

        if not manifest_file.exists():

            raise ValueError(
                "Backup không có manifest."
            )

        manifest = json.loads(
            manifest_file.read_text(
                encoding="utf-8"
            )
        )

        if manifest.get(
            "project_id"
        ) != project.id:

            raise ValueError(
                "Backup không thuộc Project hiện tại."
            )

        safety = self.backup_project(
            project,
            reason="before_restore",
        )

        try:

            for name in manifest.get(
                "files",
                []
            ):

                source = backup_path / name

                target = Path(
                    project.path
                ) / name

                if source.exists():

                    shutil.copy2(
                        source,
                        target,
                    )

            if reference_vault is not None:

                self.restore_reference_metadata(
                    backup_path,
                    reference_vault,
                    include_media=manifest.get(
                        "contains_media",
                        False,
                    ),
                )

        except Exception:

            self.restore_project(
                project,
                safety[
                    "backup_path"
                ],
                reference_vault=reference_vault,
            )

            raise

        return {
            "restored": True,
            "safety_backup": safety[
                "backup_path"
            ],
            "manifest": manifest,
        }

    def copy_reference_metadata(
        self,
        reference_vault,
        target,
        manifest,
        include_media=False,
    ):

        vault_root = Path(
            reference_vault.vault_root
        )

        registry_root = vault_root / "registry"

        if registry_root.exists():

            destination = target / "reference_vault" / "registry"

            shutil.copytree(
                registry_root,
                destination,
                dirs_exist_ok=True,
            )

            manifest["files"].append(
                "reference_vault/registry"
            )

        if include_media:

            for folder in [
                "audio",
                "text",
                "pairs",
                "segments",
                "reports",
                "style_sources",
                "speaker_references",
                "normalized",
                "manifests",
            ]:

                source = vault_root / folder

                if not source.exists():

                    continue

                destination = target / "reference_vault" / folder

                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True,
                )

                manifest["files"].append(
                    f"reference_vault/{folder}"
                )

    def restore_reference_metadata(
        self,
        backup_path,
        reference_vault,
        include_media=False,
    ):

        backup_root = Path(
            backup_path
        ) / "reference_vault"

        if not backup_root.exists():

            return False

        target_root = Path(
            reference_vault.vault_root
        )

        for item in backup_root.iterdir():

            if item.name != "registry" and not include_media:

                continue

            destination = target_root / item.name

            if item.is_dir():

                shutil.copytree(
                    item,
                    destination,
                    dirs_exist_ok=True,
                )

            elif item.is_file():

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.copy2(
                    item,
                    destination,
                )

        return True
