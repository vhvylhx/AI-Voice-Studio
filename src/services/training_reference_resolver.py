from pathlib import Path

from models.training_reference_config import (
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_CREATE_STYLE_PROFILE,
    REFERENCE_MODE_NONE,
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_SELECTED_FOLDER,
    SPEAKER_REFERENCE_TRAINING_DATASET,
    SPEAKER_REFERENCE_VOICE_DEFAULT,
    TrainingReferenceConfig,
)


class TrainingReferenceResolver:

    def __init__(
        self,
        vault_service=None,
    ):

        self.vault_service = vault_service

    def resolve(
        self,
        config,
        voice=None,
        dataset_reference=None,
    ):

        config = TrainingReferenceConfig.from_dict(
            config
        )

        result = {
            "reference_mode": config.reference_mode,
            "style_profile_id": "",
            "speaker_reference": {},
            "state": "valid",
            "messages": [],
        }

        if config.reference_mode == REFERENCE_MODE_NONE:

            result["state"] = "pending"

            return result

        if config.reference_mode == REFERENCE_MODE_APP_STYLE_PROFILE:

            result["style_profile_id"] = config.style_profile_id

            if not config.style_profile_id:

                self.add_message(
                    result,
                    "style_profile_required",
                    "Chua chon Phong cach doc.",
                )

            return result

        if config.reference_mode == REFERENCE_MODE_CREATE_STYLE_PROFILE:

            result["style_profile_id"] = config.style_profile_draft_id

            if not config.style_profile_draft_id:

                self.add_message(
                    result,
                    "style_profile_draft_required",
                    "Chua tao yeu cau Phong cach doc moi.",
                )

            return result

        if config.reference_mode == REFERENCE_MODE_SPEAKER_REFERENCE_ONLY:

            result["speaker_reference"] = self.resolve_speaker(
                config,
                voice,
                dataset_reference,
                result,
            )

            return result

        self.add_message(
            result,
            "reference_mode_invalid",
            "Che do du lieu tham chieu khong hop le.",
        )

        return result

    def resolve_speaker(
        self,
        config,
        voice,
        dataset_reference,
        result,
    ):

        mode = config.speaker_reference_mode

        if mode == SPEAKER_REFERENCE_SELECTED_FILE:

            asset_reference = self.resolve_asset_reference(
                config.speaker_reference_asset_id,
                config.speaker_reference_text_asset_id,
            )

            if asset_reference:

                return {
                    "mode": mode,
                    "audio_asset_id": config.speaker_reference_asset_id,
                    "text_asset_id": config.speaker_reference_text_asset_id,
                    "audio": asset_reference.get(
                        "audio",
                        "",
                    ),
                    "text": asset_reference.get(
                        "text",
                        config.speaker_reference_text,
                    ),
                    "origin": "managed_vault",
                }

            return {
                "mode": mode,
                "audio": config.speaker_reference_audio,
                "text": config.speaker_reference_text,
                "origin": "manual",
            }

        if mode == SPEAKER_REFERENCE_SELECTED_FOLDER:

            return {
                "mode": mode,
                "folder": config.speaker_reference_folder,
                "text": config.speaker_reference_text,
                "origin": "manual",
            }

        if mode == SPEAKER_REFERENCE_TRAINING_DATASET:

            if config.audio_text_manifest_id:

                result[
                    "audio_text_manifest_id"
                ] = config.audio_text_manifest_id

            if dataset_reference:

                return {
                    "mode": mode,
                    "dataset_reference": dataset_reference,
                    "dataset_id": config.dataset_id,
                    "dataset_item_ids": list(
                        config.dataset_item_ids
                    ),
                    "segment_ids": config.selected_training_segment_ids,
                    "selected_segment_asset_ids": list(
                        config.selected_segment_asset_ids
                    ),
                    "origin": "training_dataset",
                }

            self.add_message(
                result,
                "dataset_reference_missing",
                "Chua co segment dataset lam audio tham chieu.",
            )

            return {
                "mode": mode,
                "origin": "training_dataset",
            }

        if mode == SPEAKER_REFERENCE_VOICE_DEFAULT:

            voice_config = getattr(
                voice,
                "config",
                None,
            )

            audio = getattr(
                voice_config,
                "reference_audio",
                "",
            )

            text = getattr(
                voice_config,
                "reference_text",
                "",
            )

            speaker_reference = getattr(
                voice_config,
                "speaker_reference",
                {},
            ) or {}

            asset_reference = self.resolve_asset_reference(
                speaker_reference.get(
                    "audio_asset_id",
                    "",
                ),
                speaker_reference.get(
                    "text_asset_id",
                    "",
                ),
            )

            if asset_reference:

                audio = asset_reference.get(
                    "audio",
                    audio,
                )

                text = asset_reference.get(
                    "text",
                    text,
                )

            if not audio:

                self.add_message(
                    result,
                    "voice_default_reference_missing",
                    "Voice chua co audio tham chieu mac dinh.",
                )

            return {
                "mode": mode,
                "audio": audio,
                "text": text,
                "audio_asset_id": speaker_reference.get(
                    "audio_asset_id",
                    "",
                ),
                "text_asset_id": speaker_reference.get(
                    "text_asset_id",
                    "",
                ),
                "origin": "voice_default",
            }

        self.add_message(
            result,
            "speaker_reference_required",
            "Chua chon audio tham chieu clone giong.",
        )

        return {
            "mode": mode,
        }

    def resolve_asset_reference(
        self,
        audio_asset_id,
        text_asset_id="",
    ):

        if self.vault_service is None or not audio_asset_id:

            return {}

        result = {}

        try:

            audio_path = self.vault_service.resolve_asset_path(
                audio_asset_id
            )

            if audio_path.exists():

                result[
                    "audio"
                ] = str(
                    audio_path
                )

        except Exception:

            return {}

        if text_asset_id:

            try:

                text_path = self.vault_service.resolve_asset_path(
                    text_asset_id
                )

                if text_path.exists():

                    result[
                        "text"
                    ] = text_path.read_text(
                        encoding="utf-8"
                    )

            except Exception:

                pass

        return result

    def add_message(
        self,
        result,
        code,
        reason,
    ):

        result["state"] = "invalid"

        result["messages"].append(
            {
                "code": code,
                "reason": reason,
            }
        )
