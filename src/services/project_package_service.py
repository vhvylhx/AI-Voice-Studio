import json
import zipfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class ProjectPackageService:

    MANIFEST = "manifest.json"

    def export_project(
        self,
        project,
        package_file,
        mode="lightweight",
        reference_vault=None,
    ):

        package_file = Path(
            package_file
        )

        package_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest = {
            "schema_version": 1,
            "package_type": "avs_project",
            "mode": mode,
            "contains_media": mode in {
                "standard",
                "full",
            },
            "project_id": project.id,
            "display_name": project.display_name,
            "exported_at": datetime.now().isoformat(),
            "files": [
                "project.json",
            ],
            "reference_assets": [],
        }

        with zipfile.ZipFile(
            package_file,
            "w",
            zipfile.ZIP_DEFLATED,
        ) as archive:

            config = Path(
                project.path
            ) / "project.json"

            if config.exists():

                archive.write(
                    config,
                    "project.json",
                )

            if reference_vault is not None and mode in {
                "lightweight",
                "standard",
                "full",
            }:

                self.write_reference_vault(
                    archive,
                    manifest,
                    reference_vault,
                    include_media=mode in {
                        "standard",
                        "full",
                    },
                )

            archive.writestr(
                self.MANIFEST,
                json.dumps(
                    manifest,
                    indent=4,
                    ensure_ascii=False,
                )
            )

        return {
            "package_file": str(
                package_file
            ),
            "manifest": manifest,
        }

    def inspect_package(
        self,
        package_file,
    ):

        package_file = Path(
            package_file
        )

        with zipfile.ZipFile(
            package_file,
            "r",
        ) as archive:

            for info in archive.infolist():

                self.validate_member(
                    info.filename
                )

            if self.MANIFEST not in archive.namelist():

                raise ValueError(
                    "Package thiếu manifest."
                )

            manifest = json.loads(
                archive.read(
                    self.MANIFEST
                ).decode(
                    "utf-8"
                )
            )

        if manifest.get(
            "package_type"
        ) != "avs_project":

            raise ValueError(
                "Package không phải Project của AI Voice Studio."
            )

        return manifest

    def import_project(
        self,
        package_file,
        destination_root,
        import_as_new=True,
        reference_vault=None,
    ):

        manifest = self.inspect_package(
            package_file
        )

        destination_root = Path(
            destination_root
        )

        new_id = (
            f"project_{uuid4().hex[:12]}"
            if import_as_new
            else manifest.get(
                "project_id",
                f"project_{uuid4().hex[:12]}",
            )
        )

        target = destination_root / new_id

        if target.exists():

            raise ValueError(
                "Project import đã tồn tại. Mặc định không ghi đè."
            )

        target.mkdir(
            parents=True,
            exist_ok=False,
        )

        with zipfile.ZipFile(
            package_file,
            "r",
        ) as archive:

            for info in archive.infolist():

                name = self.validate_member(
                    info.filename
                )

                if name == self.MANIFEST:

                    continue

                if name.startswith(
                    "reference_vault/"
                ):

                    if reference_vault is not None:

                        output = (
                            Path(
                                reference_vault.vault_root
                            )
                            / name.replace(
                                "reference_vault/",
                                "",
                                1,
                            )
                        )

                        output.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        output.write_bytes(
                            archive.read(
                                info
                            )
                        )

                    continue

                output = target / name

                output.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                output.write_bytes(
                    archive.read(
                        info
                    )
                )

        return {
            "project_id": new_id,
            "project_root": str(
                target
            ),
            "manifest": manifest,
        }

    def validate_member(
        self,
        name,
    ):

        path = Path(
            name
        )

        if path.is_absolute():

            raise ValueError(
                "Package chứa absolute path."
            )

        if ".." in path.parts:

            raise ValueError(
                "Package chứa path traversal."
            )

        return str(
            path
        ).replace(
            "\\",
            "/",
        )

    def write_reference_vault(
        self,
        archive,
        manifest,
        reference_vault,
        include_media=False,
    ):

        vault_root = Path(
            reference_vault.vault_root
        )

        folders = [
            "registry",
        ]

        if include_media:

            folders.extend(
                [
                    "audio",
                    "text",
                    "pairs",
                    "segments",
                    "reports",
                    "style_sources",
                    "speaker_references",
                    "normalized",
                    "manifests",
                ]
            )

        for folder in folders:

            source = vault_root / folder

            if not source.exists():

                continue

            for file in source.rglob("*"):

                if not file.is_file():

                    continue

                relative = file.relative_to(
                    vault_root
                ).as_posix()

                archive.write(
                    file,
                    f"reference_vault/{relative}",
                )

                manifest["files"].append(
                    f"reference_vault/{relative}"
                )
