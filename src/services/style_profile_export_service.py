import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from repositories.style_profile_repository import StyleProfileRepository


class StyleProfileExportService:

    PACKAGE_VERSION = 1

    def __init__(
        self,
        repository=None,
    ):

        self.repository = repository or StyleProfileRepository()

    def export_package(
        self,
        style_profile_id,
        output_file,
        include_reference_clips=False,
        include_full_source=False,
    ):

        if include_full_source:

            raise ValueError(
                "full_source_export_not_supported"
            )

        folder = self.repository.profile_dir(
            style_profile_id
        )

        profile = self.repository.load(
            style_profile_id
        )

        output_file = Path(
            output_file
        )

        if output_file.suffix.lower() != ".avstyle":

            output_file = output_file.with_suffix(
                ".avstyle"
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = self.package_files(
            folder,
            include_reference_clips,
        )

        manifest = {
            "package_version": self.PACKAGE_VERSION,
            "style_profile_id": style_profile_id,
            "display_name": profile.display_name,
            "include_reference_clips": include_reference_clips,
            "include_full_source": False,
            "files": sorted(
                self.archive_name(
                    item
                )
                for item in files
            ),
        }

        checksums = {
            self.archive_name(
                relative
            ): self.sha256(
                folder / relative
            )
            for relative in files
        }

        with zipfile.ZipFile(
            output_file,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:

            archive.writestr(
                "manifest.json",
                json.dumps(
                    manifest,
                    ensure_ascii=False,
                    indent=4,
                ),
            )

            archive.writestr(
                "checksums.json",
                json.dumps(
                    checksums,
                    ensure_ascii=False,
                    indent=4,
                ),
            )

            for relative in files:

                archive.write(
                    folder / relative,
                    self.archive_name(
                        relative
                    ),
                )

        return {
            "ok": True,
            "package": str(
                output_file
            ),
            "style_profile_id": style_profile_id,
            "files": manifest["files"],
        }

    def validate_package(
        self,
        package_file,
    ):

        package_file = Path(
            package_file
        )

        if not package_file.exists():

            return {
                "ok": False,
                "error": "package_missing",
            }

        try:

            with zipfile.ZipFile(
                package_file,
                "r",
            ) as archive:

                names = archive.namelist()

                for name in names:

                    self.validate_member_name(
                        name
                    )

                if "manifest.json" not in names:

                    return {
                        "ok": False,
                        "error": "manifest_missing",
                    }

                if "style_profile.json" not in names:

                    return {
                        "ok": False,
                        "error": "style_profile_missing",
                    }

                manifest = json.loads(
                    archive.read(
                        "manifest.json"
                    ).decode(
                        "utf-8"
                    )
                )

                if int(
                    manifest.get(
                        "package_version",
                        0,
                    )
                ) > self.PACKAGE_VERSION:

                    return {
                        "ok": False,
                        "error": "package_schema_newer",
                    }

                checksums = {}

                if "checksums.json" in names:

                    checksums = json.loads(
                        archive.read(
                            "checksums.json"
                        ).decode(
                            "utf-8"
                        )
                    )

                for name, checksum in checksums.items():

                    self.validate_member_name(
                        name
                    )

                    if name not in names:

                        return {
                            "ok": False,
                            "error": "checksum_file_missing",
                            "file": name,
                        }

                    if hashlib.sha256(
                        archive.read(
                            name
                        )
                    ).hexdigest() != checksum:

                        return {
                            "ok": False,
                            "error": "checksum_mismatch",
                            "file": name,
                        }

                return {
                    "ok": True,
                    "manifest": manifest,
                    "checksums": checksums,
                }

        except Exception as e:

            return {
                "ok": False,
                "error": "package_invalid",
                "message": str(
                    e
                ),
            }

    def import_package(
        self,
        package_file,
        keep_id=True,
        new_id="",
    ):

        validation = self.validate_package(
            package_file
        )

        if not validation.get(
            "ok",
            False,
        ):

            return validation

        with zipfile.ZipFile(
            package_file,
            "r",
        ) as archive:

            profile = json.loads(
                archive.read(
                    "style_profile.json"
                ).decode(
                    "utf-8"
                )
            )

            original_id = profile.get(
                "style_profile_id",
                "",
            )

            target_id = (
                original_id
                if keep_id
                else new_id
                or self.repository.next_id()
            )

            if self.repository.exists(
                target_id
            ):

                return {
                    "ok": False,
                    "error": "duplicate_id",
                    "style_profile_id": target_id,
                }

            profile[
                "style_profile_id"
            ] = target_id

            folder = self.repository.profile_dir(
                target_id
            )

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            for name in archive.namelist():

                if name in (
                    "manifest.json",
                    "checksums.json",
                ):

                    continue

                self.validate_member_name(
                    name
                )

                target = (
                    folder / name
                ).resolve()

                try:

                    target.relative_to(
                        folder.resolve()
                    )

                except ValueError:

                    return {
                        "ok": False,
                        "error": "path_traversal",
                    }

                target.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                if name == "style_profile.json":

                    target.write_text(
                        json.dumps(
                            profile,
                            ensure_ascii=False,
                            indent=4,
                        ),
                        encoding="utf-8",
                    )

                else:

                    with archive.open(
                        name
                    ) as source:

                        with open(
                            target,
                            "wb",
                        ) as output:

                            shutil.copyfileobj(
                                source,
                                output,
                            )

            self.repository.ensure_structure(
                folder
            )

            self.repository.write_manifest(
                target_id
            )

            return {
                "ok": True,
                "style_profile_id": target_id,
                "original_style_profile_id": original_id,
            }

    def package_files(
        self,
        folder,
        include_reference_clips,
    ):

        candidates = [
            Path(
                "style_profile.json"
            ),
            Path(
                "prosody/pause_profile.json"
            ),
            Path(
                "prosody/rhythm_profile.json"
            ),
            Path(
                "prosody/punctuation_profile.json"
            ),
            Path(
                "prosody/intonation_profile.json"
            ),
            Path(
                "prosody/emphasis_profile.json"
            ),
            Path(
                "prosody/breathing_profile.json"
            ),
            Path(
                "prosody/reading_fingerprint.json"
            ),
            Path(
                "indexes/reference_index.json"
            ),
            Path(
                "indexes/sentence_index.json"
            ),
            Path(
                "indexes/style_clusters.json"
            ),
            Path(
                "references/manifest.json"
            ),
        ]

        if include_reference_clips:

            clip_root = (
                Path(
                    folder
                )
                / "references"
                / "optional_selected_clips"
            )

            if clip_root.exists():

                for file in clip_root.rglob(
                    "*"
                ):

                    if file.is_file():

                        candidates.append(
                            file.relative_to(
                                folder
                            )
                        )

        return [
            relative
            for relative in candidates
            if (
                Path(
                    folder
                )
                / relative
            ).exists()
        ]

    def validate_member_name(
        self,
        name,
    ):

        path = Path(
            name
        )

        if path.is_absolute() or ".." in path.parts:

            raise ValueError(
                "path_traversal"
            )

    def archive_name(
        self,
        relative,
    ):

        return Path(
            relative
        ).as_posix()

    def sha256(
        self,
        file,
    ):

        return hashlib.sha256(
            Path(
                file
            ).read_bytes()
        ).hexdigest()
