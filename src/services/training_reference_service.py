from datetime import datetime
from pathlib import Path

from models.training_reference_config import (
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_CREATE_STYLE_PROFILE,
    REFERENCE_MODE_NONE,
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_SELECTED_FOLDER,
    TrainingReferenceConfig,
)
from services.audio_text_pair_service import AudioTextPairService
from services.reference_audio_validation_service import ReferenceAudioValidationService
from services.training_reference_resolver import TrainingReferenceResolver


class TrainingReferenceService:

    def __init__(
        self,
        style_profile_service=None,
        audio_validator=None,
        pair_service=None,
        resolver=None,
        vault_service=None,
    ):

        self.style_profile_service = style_profile_service

        self.vault_service = vault_service

        self.audio_validator = (
            audio_validator
            or ReferenceAudioValidationService()
        )

        self.pair_service = (
            pair_service
            or AudioTextPairService(
                vault_service=vault_service
            )
        )

        self.resolver = (
            resolver
            or TrainingReferenceResolver(
                vault_service=vault_service
            )
        )

    def default_config(
        self,
    ):

        return TrainingReferenceConfig()

    def validate(
        self,
        config,
        voice=None,
        dataset_reference=None,
    ):

        config = TrainingReferenceConfig.from_dict(
            config
        )

        messages = []

        if config.reference_mode == REFERENCE_MODE_APP_STYLE_PROFILE:

            messages.extend(
                self.validate_style_profile(
                    config.style_profile_id
                )
            )

        elif config.reference_mode == REFERENCE_MODE_CREATE_STYLE_PROFILE:

            if not config.style_profile_draft_id:

                messages.append(
                    self.issue(
                        "style_profile_draft_pending",
                        "Chua tao draft Style Profile.",
                    )
                )

        elif config.reference_mode == REFERENCE_MODE_SPEAKER_REFERENCE_ONLY:

            messages.extend(
                self.validate_speaker_reference(
                    config
                )
            )

        elif config.reference_mode == REFERENCE_MODE_NONE:

            messages.append(
                self.issue(
                    "reference_not_selected",
                    "Chua chon du lieu tham chieu.",
                )
            )

        resolved = self.resolver.resolve(
            config,
            voice=voice,
            dataset_reference=dataset_reference,
        )

        messages.extend(
            resolved.get(
                "messages",
                [],
            )
        )

        state = "valid" if not messages else "invalid"

        config.validation_state = state
        config.validation_messages = messages
        config.last_validated_at = datetime.now().isoformat()

        return {
            "state": state,
            "ok": state == "valid",
            "config": config.to_dict(),
            "resolved": resolved,
            "messages": messages,
        }

    def validate_style_profile(
        self,
        style_profile_id,
    ):

        if not style_profile_id:

            return [
                self.issue(
                    "style_profile_required",
                    "Chua chon Phong cach doc.",
                )
            ]

        if self.style_profile_service is None:

            return []

        readiness = self.style_profile_service.readiness(
            style_profile_id
        )

        if readiness.get(
            "status"
        ) == "missing":

            return [
                self.issue(
                    "style_profile_missing",
                    "Phong cach doc khong ton tai.",
                )
            ]

        if readiness.get(
            "generation_usage"
        ) == "degraded":

            return [
                self.issue(
                    "style_profile_degraded",
                    "Phong cach doc chua duoc engine ap dung day du.",
                    level="warning",
                )
            ]

        return []

    def validate_speaker_reference(
        self,
        config,
    ):

        if config.speaker_reference_mode == SPEAKER_REFERENCE_SELECTED_FILE:

            if config.speaker_reference_asset_id and self.vault_service is not None:

                verify = self.vault_service.verify_asset(
                    config.speaker_reference_asset_id
                )

                if verify.get(
                    "ok"
                ):

                    return []

                return verify.get(
                    "messages",
                    [],
                )

            return self.audio_validator.validate_file(
                config.speaker_reference_audio,
                config.speaker_reference_text,
                transcript_required=False,
            ).get(
                "messages",
                [],
            )

        if config.speaker_reference_mode == SPEAKER_REFERENCE_SELECTED_FOLDER:

            return self.audio_validator.validate_folder(
                config.speaker_reference_folder
            ).get(
                "messages",
                [],
            )

        return []

    def view_model(
        self,
        config=None,
    ):

        config = TrainingReferenceConfig.from_dict(
            config
        )

        styles = []

        if self.style_profile_service is not None:

            try:

                styles = [
                    {
                        "style_profile_id": profile.style_profile_id,
                        "display_name": profile.display_name,
                        "status": profile.status,
                        "description": profile.description,
                    }
                    for profile in self.style_profile_service.list_profiles()
                ]

            except Exception:

                styles = []

        return {
            "config": config.to_dict(),
            "style_profiles": styles,
            "modes": [
                REFERENCE_MODE_APP_STYLE_PROFILE,
                REFERENCE_MODE_CREATE_STYLE_PROFILE,
                REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            ],
        }

    def suggest_reference_from_folder(
        self,
        folder,
        current_config=None,
    ):

        config = TrainingReferenceConfig.from_dict(
            current_config
        )

        if config.reference_source_origin == "manual":

            return config

        folder = Path(
            folder or ""
        )

        if not folder.exists():

            return config

        audio = sorted(
            [
                item
                for item in folder.rglob("*")
                if item.is_file()
                and item.suffix.lower()
                in ReferenceAudioValidationService.AUDIO_EXTENSIONS
            ],
            key=lambda item: str(
                item
            ).lower(),
        )

        if not audio:

            return config

        config.speaker_reference_audio = str(
            audio[0]
        )
        config.speaker_reference_folder = str(
            folder
        )
        config.reference_source_origin = "dataset_suggestion"

        return config

    def issue(
        self,
        code,
        reason,
        level="error",
    ):

        return {
            "code": code,
            "reason": reason,
            "level": level,
            "suggestion": "Kiem tra lai cau hinh du lieu tham chieu.",
        }
