import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models.audio_text_manifest import AudioTextManifest
from models.audio_text_manifest import AudioTextPair
from services.reference_vault_service import ReferenceVaultService


class AudioTextPairService:

    AUDIO_EXTENSIONS = {
        ".mp3",
        ".wav",
    }

    TEXT_EXTENSIONS = {
        ".txt",
    }

    def __init__(
        self,
        vault_service=None,
    ):

        self.vault_service = vault_service

    def collect(
        self,
        folder,
    ):

        folder = Path(
            folder
        )

        audio = []
        text = []

        if not folder.exists():

            return {
                "audio": audio,
                "text": text,
            }

        for file in folder.rglob("*"):

            if not file.is_file():

                continue

            suffix = file.suffix.lower()

            if suffix in self.AUDIO_EXTENSIONS:

                audio.append(
                    file
                )

            if suffix in self.TEXT_EXTENSIONS:

                text.append(
                    file
                )

        return {
            "audio": sorted(
                audio,
                key=self.sort_key,
            ),
            "text": sorted(
                text,
                key=self.sort_key,
            ),
        }

    def match_folder(
        self,
        folder,
        persist_manifest=False,
        manifest_dir=None,
        source_project_id="",
    ):

        files = self.collect(
            folder
        )

        result = self.match(
            files["audio"],
            files["text"],
            persist_manifest=persist_manifest,
            manifest_dir=manifest_dir,
            source_project_id=source_project_id,
            source_folder=folder,
        )

        return result

    def match(
        self,
        audio_files,
        text_files,
        persist_manifest=False,
        manifest_dir=None,
        source_project_id="",
        source_folder="",
    ):

        audio_by_stem, audio_errors = self.index_by_stem(
            audio_files,
            "audio",
        )

        text_by_stem, text_errors = self.index_by_stem(
            text_files,
            "text",
        )

        pairs = []
        errors = audio_errors + text_errors

        all_stems = sorted(
            set(
                audio_by_stem.keys()
            )
            | set(
                text_by_stem.keys()
            )
        )

        for stem in all_stems:

            audio = audio_by_stem.get(
                stem
            )

            text = text_by_stem.get(
                stem
            )

            if audio and text:

                pairs.append(
                    {
                        "stem": stem,
                        "audio": str(
                            audio
                        ),
                        "text": str(
                            text
                        ),
                        "status": "matched",
                    }
                )

                continue

            if audio:

                errors.append(
                    self.issue(
                        audio,
                        "missing_text",
                        "Khong tim thay TXT cung ten.",
                    )
                )

            if text:

                errors.append(
                    self.issue(
                        text,
                        "missing_audio",
                        "Khong tim thay MP3/WAV cung ten.",
                    )
                )

        result = {
            "pairs": pairs,
            "errors": errors,
            "summary": {
                "matched": len(
                    pairs
                ),
                "errors": len(
                    errors
                ),
            },
        }

        if persist_manifest:

            result[
                "manifest"
            ] = self.persist_manifest(
                result,
                manifest_dir=manifest_dir,
                source_project_id=source_project_id,
                source_folder=source_folder,
            )

        return result

    def persist_manifest(
        self,
        result,
        manifest_dir=None,
        source_project_id="",
        source_folder="",
    ):

        vault = self.vault_service

        manifest_id = f"pair_manifest_{uuid4().hex[:12]}"

        pairs = []

        for index, pair in enumerate(
            result.get(
                "pairs",
                []
            )
        ):

            audio_asset = None
            text_asset = None

            if vault is not None:

                audio_asset = vault.import_file(
                    pair[
                        "audio"
                    ],
                    "training_reference_audio",
                    source_project_id=source_project_id,
                    source_origin="audio_text_pair",
                    usage={
                        "kind": "audio_text_pair",
                        "manifest_id": manifest_id,
                    },
                )[
                    "asset"
                ]

                text_asset = vault.import_file(
                    pair[
                        "text"
                    ],
                    "training_reference_text",
                    source_project_id=source_project_id,
                    source_origin="audio_text_pair",
                    usage={
                        "kind": "audio_text_pair",
                        "manifest_id": manifest_id,
                    },
                )[
                    "asset"
                ]

            pairs.append(
                AudioTextPair(
                    pair_id=f"pair_{uuid4().hex[:12]}",
                    audio_asset_id=getattr(
                        audio_asset,
                        "asset_id",
                        "",
                    ),
                    text_asset_id=getattr(
                        text_asset,
                        "asset_id",
                        "",
                    ),
                    audio_checksum=getattr(
                        audio_asset,
                        "checksum",
                        "",
                    ),
                    text_checksum=getattr(
                        text_asset,
                        "checksum",
                        "",
                    ),
                    original_audio_stem=Path(
                        pair[
                            "audio"
                        ]
                    ).stem,
                    original_text_stem=Path(
                        pair[
                            "text"
                        ]
                    ).stem,
                    normalized_stem=pair.get(
                        "stem",
                        "",
                    ),
                    order_index=index,
                    validation_state="valid",
                    source_project_id=source_project_id,
                    source_origin="managed_vault"
                    if vault is not None
                    else "external_manifest",
                    created_at=datetime.now().isoformat(),
                )
            )

        manifest = AudioTextManifest(
            manifest_id=manifest_id,
            pairs=pairs,
            source_folder_metadata={
                "source_folder": str(
                    source_folder or ""
                ),
            },
            validation_summary=dict(
                result.get(
                    "summary",
                    {},
                )
            ),
            missing_audio=[
                item
                for item in result.get(
                    "errors",
                    []
                )
                if item.get(
                    "code"
                )
                == "missing_audio"
            ],
            missing_text=[
                item
                for item in result.get(
                    "errors",
                    []
                )
                if item.get(
                    "code"
                )
                == "missing_text"
            ],
            duplicate_stem=[
                item
                for item in result.get(
                    "errors",
                    []
                )
                if item.get(
                    "code"
                )
                == "duplicate_stem"
            ],
            checksum_summary={
                "audio": [
                    pair.audio_checksum
                    for pair in pairs
                ],
                "text": [
                    pair.text_checksum
                    for pair in pairs
                ],
            },
        )

        data = manifest.to_dict()

        if vault is not None:

            asset = vault.save_json_asset(
                "audio_text_manifest",
                data,
                f"{manifest_id}.json",
                folder="pairs",
                source_project_id=source_project_id,
            )

            data[
                "manifest_asset_id"
            ] = asset.asset_id

        if manifest_dir is not None:

            manifest_dir = Path(
                manifest_dir
            )

            manifest_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            file = manifest_dir / f"{manifest_id}.json"

            file.write_text(
                json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            data[
                "manifest_path"
            ] = str(
                file
            )

        return data

    def index_by_stem(
        self,
        files,
        kind,
    ):

        result = {}
        errors = []

        for file in sorted(
            [
                Path(
                    item
                )
                for item in files
            ],
            key=self.sort_key,
        ):

            stem = file.stem.lower()

            if stem in result:

                errors.append(
                    self.issue(
                        file,
                        "duplicate_stem",
                        f"File {kind} trung ten goc.",
                    )
                )

                continue

            result[stem] = file

        return result, errors

    def issue(
        self,
        file,
        code,
        message,
    ):

        return {
            "file": str(
                file
            ),
            "code": code,
            "reason": message,
            "suggestion": "Kiem tra lai ten file va cap audio/text.",
        }

    def sort_key(
        self,
        file,
    ):

        return str(
            Path(
                file
            )
        ).lower()
