import hashlib
import json
from datetime import datetime
from pathlib import Path

from models.voice_publish import VoicePublishRequest
from models.voice_publish import VoicePublishResult
from services.voice_service import VoiceService


class VoicePublishService:

    def __init__(
        self,
        voice_service=None,
    ):

        self.voice_service = voice_service or VoiceService()

    def discover_checkpoints(
        self,
        voice_id,
        run_root=None,
    ):

        voice = self.voice_service.find_by_id(
            voice_id
        )

        if voice is None:

            return {
                "ok": False,
                "code": "voice_not_found",
                "voice_id": voice_id,
                "gpt_candidates": [],
                "sovits_candidates": [],
                "warnings": [],
            }

        root = Path(
            run_root or voice.model_dir or voice.path / "model"
        )

        warnings = []

        if not root.exists():

            return {
                "ok": False,
                "code": "run_root_missing",
                "voice_id": voice.id,
                "run_root": str(
                    root
                ),
                "gpt_candidates": [],
                "sovits_candidates": [],
                "warnings": [
                    "run_root_missing",
                ],
            }

        gpt_candidates = self.scan_candidates(
            root,
            {
                ".ckpt",
            },
        )

        sovits_candidates = self.scan_candidates(
            root,
            {
                ".pth",
            },
        )

        if len(
            gpt_candidates
        ) > 1 or len(
            sovits_candidates
        ) > 1:

            warnings.append(
                "multiple_checkpoint_candidates"
            )

        return {
            "ok": bool(
                gpt_candidates
            )
            and bool(
                sovits_candidates
            ),
            "code": "checkpoint_candidates_found"
            if gpt_candidates
            and sovits_candidates
            else "checkpoint_candidates_missing",
            "voice_id": voice.id,
            "run_root": str(
                root
            ),
            "gpt_candidates": gpt_candidates,
            "sovits_candidates": sovits_candidates,
            "suggestion": self.suggest_pair(
                gpt_candidates,
                sovits_candidates,
            ),
            "warnings": warnings,
        }

    def scan_candidates(
        self,
        root,
        suffixes,
    ):

        result = []

        for file in Path(
            root
        ).rglob(
            "*"
        ):

            if not file.is_file():

                continue

            if file.suffix.lower() not in suffixes:

                continue

            if any(
                token in file.name.lower()
                for token in [
                    ".tmp",
                    ".partial",
                    ".incomplete",
                ]
            ):

                continue

            try:

                stat = file.stat()

            except Exception:

                continue

            if stat.st_size <= 0:

                continue

            result.append(
                {
                    "path": str(
                        file
                    ),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "run_id": self.infer_run_id(
                        file,
                        root,
                    ),
                }
            )

        return sorted(
            result,
            key=lambda item: (
                item[
                    "run_id"
                ],
                item[
                    "path"
                ],
            ),
        )

    def suggest_pair(
        self,
        gpt_candidates,
        sovits_candidates,
    ):

        if (
            len(
                gpt_candidates
            )
            == 1
            and len(
                sovits_candidates
            )
            == 1
        ):

            return {
                "gpt_model": gpt_candidates[0][
                    "path"
                ],
                "sovits_model": sovits_candidates[0][
                    "path"
                ],
                "confidence": "single_pair",
            }

        return {
            "gpt_model": "",
            "sovits_model": "",
            "confidence": "manual_selection_required",
        }

    def infer_run_id(
        self,
        file,
        root,
    ):

        try:

            relative = Path(
                file
            ).relative_to(
                root
            )

        except Exception:

            return ""

        parts = relative.parts

        return parts[0] if len(
            parts
        ) > 1 else ""

    def validate_publish(
        self,
        request,
    ):

        request = VoicePublishRequest.from_dict(
            request
        )

        created_at = datetime.now().isoformat()

        voice = self.voice_service.find_by_id(
            request.voice_id
        )

        blockers = []
        warnings = []

        if voice is None:

            blockers.append(
                "voice_not_found"
            )

            voice_root = None

        else:

            voice_root = voice.path

        assets = {
            "gpt_model": self.validate_file(
                request.gpt_model,
                {
                    ".ckpt",
                },
                voice_root,
            ),
            "sovits_model": self.validate_file(
                request.sovits_model,
                {
                    ".pth",
                },
                voice_root,
            ),
            "reference_audio": self.validate_file(
                request.reference_audio,
                {
                    ".wav",
                    ".mp3",
                    ".flac",
                    ".m4a",
                },
                voice_root,
                allow_outside_voice=True,
            ),
            "reference_text": {
                "ok": bool(
                    str(
                        request.reference_text or ""
                    ).strip()
                ),
                "kind": "inline_text",
                "sha256": hashlib.sha256(
                    str(
                        request.reference_text or ""
                    ).encode(
                        "utf-8"
                    )
                ).hexdigest(),
            },
        }

        for key, info in assets.items():

            if not info.get(
                "ok",
                False,
            ):

                blockers.append(
                    key
                )

        if request.prompt_language != "vi":

            warnings.append(
                "prompt_language_not_vi"
            )

        if request.text_language != "vi":

            warnings.append(
                "text_language_not_vi"
            )

        if not request.training_run_id:

            warnings.append(
                "training_run_id_missing"
            )

        fingerprint = self.fingerprint(
            request,
            assets,
        )

        status = "ready" if not blockers else "blocked"

        return VoicePublishResult(
            publish_id=self.publish_id(
                request.voice_id,
                fingerprint,
            ),
            voice_id=request.voice_id,
            training_run_id=request.training_run_id,
            status=status,
            validation_status=status,
            blockers=blockers,
            warnings=warnings,
            fingerprint=fingerprint,
            assets=assets,
            created_at=created_at,
        )

    def publish(
        self,
        request,
    ):

        request = VoicePublishRequest.from_dict(
            request
        )

        result = self.validate_publish(
            request.to_dict()
        )

        if result.blockers:

            return result

        if not request.confirm_publish:

            result.status = "confirmation_required"
            result.validation_status = "ready"
            result.blockers = [
                "confirm_publish_required",
            ]

            return result

        voice = self.voice_service.find_by_id(
            request.voice_id
        )

        if voice is None:

            result.status = "blocked"
            result.validation_status = "blocked"
            result.blockers.append(
                "voice_not_found"
            )

            return result

        config = voice.config

        config.gpt_model = request.gpt_model
        config.sovits_model = request.sovits_model
        config.reference_audio = request.reference_audio
        config.reference_text = request.reference_text
        config.prompt_language = request.prompt_language or "vi"
        config.text_language = request.text_language or "vi"
        config.model_run_id = request.training_run_id
        config.runtime_profile_id = request.runtime_profile_id
        config.publish_id = result.publish_id
        config.published_training_run_id = request.training_run_id
        config.published_at = result.created_at
        config.publish_validation_status = "ready"
        config.publish_blockers = []
        config.publish_warnings = result.warnings
        config.publish_fingerprint = result.fingerprint
        config.training_status = "published"
        config.updated_at = datetime.now().isoformat()

        self.voice_service.save(
            voice
        )

        result.status = "published"
        result.validation_status = "ready"

        return result

    def validate_file(
        self,
        value,
        suffixes,
        voice_root,
        allow_outside_voice=False,
    ):

        path = Path(
            value or ""
        )

        if not value:

            return {
                "ok": False,
                "code": "missing",
                "path": "",
            }

        try:

            stat = path.stat()

        except Exception:

            return {
                "ok": False,
                "code": "file_missing",
                "path": str(
                    path
                ),
            }

        if path.suffix.lower() not in suffixes:

            return {
                "ok": False,
                "code": "file_type_invalid",
                "path": str(
                    path
                ),
            }

        if stat.st_size <= 0:

            return {
                "ok": False,
                "code": "file_empty",
                "path": str(
                    path
                ),
            }

        if (
            voice_root is not None
            and not allow_outside_voice
            and not self.is_inside(
                path,
                voice_root,
            )
        ):

            return {
                "ok": False,
                "code": "outside_voice_root",
                "path": str(
                    path
                ),
            }

        return {
            "ok": True,
            "path": str(
                path
            ),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "suffix": path.suffix.lower(),
        }

    def is_inside(
        self,
        path,
        root,
    ):

        try:

            Path(
                path
            ).resolve().relative_to(
                Path(
                    root
                ).resolve()
            )

            return True

        except Exception:

            return False

    def fingerprint(
        self,
        request,
        assets,
    ):

        payload = {
            "schema_version": 1,
            "voice_id": request.voice_id,
            "training_run_id": request.training_run_id,
            "runtime_profile_id": request.runtime_profile_id,
            "prompt_language": request.prompt_language,
            "text_language": request.text_language,
            "assets": assets,
        }

        return hashlib.sha256(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    def publish_id(
        self,
        voice_id,
        fingerprint,
    ):

        return (
            f"publish_{voice_id}_{fingerprint[:12]}"
        )
