import hashlib
import json
from datetime import datetime
from pathlib import Path

from models.style_profile import STYLE_STATUS_DEGRADED


class StyleProfileIntegrityService:

    def __init__(
        self,
        repository=None,
    ):

        self.repository = repository

    def verify(
        self,
        style_profile_id,
        repository=None,
    ):

        repository = repository or self.repository

        if repository is None:

            raise ValueError(
                "repository_required"
            )

        folder = repository.profile_dir(
            style_profile_id
        )

        profile = repository.load(
            style_profile_id
        )

        required = [
            "style_profile.json",
            "manifest.json",
            "extraction_state.json",
            "extraction_report.json",
            "references/manifest.json",
        ]

        missing = []

        invalid = []

        for relative in required:

            file = folder / relative

            if not file.exists():

                missing.append(
                    relative
                )

                continue

            if file.suffix == ".json":

                try:

                    json.loads(
                        file.read_text(
                            encoding="utf-8"
                        )
                    )

                except Exception:

                    invalid.append(
                        relative
                    )

        checksums = self.checksums(
            folder,
            required,
        )

        ok = not missing and not invalid

        if not ok:

            profile.status = STYLE_STATUS_DEGRADED

        profile.integrity["missing_files"] = missing

        profile.integrity["invalid_files"] = invalid

        profile.integrity["last_verified_at"] = (
            datetime.now().isoformat()
        )

        return {
            "style_profile_id": style_profile_id,
            "ok": ok,
            "status": profile.status,
            "missing_files": missing,
            "invalid_files": invalid,
            "checksums": checksums,
            "suggestions": self.suggestions(
                missing,
                invalid,
            ),
        }

    def checksums(
        self,
        folder,
        relative_files,
    ):

        result = {}

        for relative in relative_files:

            file = Path(
                folder
            ) / relative

            if file.exists() and file.is_file():

                result[relative] = hashlib.sha256(
                    file.read_bytes()
                ).hexdigest()

        return result

    def suggestions(
        self,
        missing,
        invalid,
    ):

        suggestions = []

        if missing:

            suggestions.append(
                "Kiem tra backup gan nhat hoac import lai goi .avstyle."
            )

        if invalid:

            suggestions.append(
                "File JSON bi loi. Khong tu khoi phuc am tham; hay chon backup de phuc hoi."
            )

        return suggestions

