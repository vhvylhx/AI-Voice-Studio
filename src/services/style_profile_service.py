from datetime import datetime
from pathlib import Path
import unicodedata

from models.style_profile import STYLE_MODE_DISABLED
from models.style_profile import STYLE_MODE_EXPLICIT
from models.style_profile import STYLE_MODE_INHERIT
from models.style_profile import STYLE_STATUS_EXTRACTION_PENDING
from models.style_profile import STYLE_STATUS_SOURCE_READY
from models.style_profile import STYLE_SOURCE_ALIGNED_DATASET
from models.style_profile import StyleProfile
from repositories.style_profile_repository import StyleProfileRepository
from services.style_profile_extraction_service import StyleProfileExtractionService
from services.style_profile_integrity_service import StyleProfileIntegrityService
from services.voice_service import VoiceService


class StyleProfileService:

    def __init__(
        self,
        repository=None,
        voice_service=None,
        integrity=None,
        extraction=None,
    ):

        self.repository = repository or StyleProfileRepository()

        self.voice_service = voice_service or VoiceService()

        self.integrity = integrity or StyleProfileIntegrityService(
            self.repository
        )

        self.extraction = extraction or StyleProfileExtractionService(
            self.repository
        )

    def create_profile(
        self,
        display_name,
        description="",
        language="vi",
        source_type=STYLE_SOURCE_ALIGNED_DATASET,
        dataset_reference=None,
        default_tags=None,
        intended_use="generate_style_profile",
        style_classification="style_only",
        parameters=None,
        prompt_instructions=None,
        reference_requirements=None,
        compatibility=None,
    ):

        now = datetime.now().isoformat()

        status = (
            STYLE_STATUS_SOURCE_READY
            if dataset_reference
            else STYLE_STATUS_EXTRACTION_PENDING
        )

        display_name = self.normalize_display_name(
            display_name
        )

        errors = self.validate_display_name(
            display_name
        )

        if errors:

            raise ValueError(
                ",".join(
                    errors
                )
            )

        profile = StyleProfile(
            style_profile_id=self.repository.next_id(),
            display_name=display_name,
            description=str(
                description or ""
            ),
            language=language or "vi",
            source_type=source_type,
            status=status,
            created_at=now,
            updated_at=now,
            dataset_reference=dataset_reference or {},
            default_tags=default_tags or [],
            intended_use=intended_use
            or "generate_style_profile",
            style_classification=style_classification
            or "style_only",
            parameters=parameters or {},
            prompt_instructions=prompt_instructions or {
                "system_prompt": "",
                "positive_prompt": "",
                "negative_prompt": "",
            },
            reference_requirements=reference_requirements or {
                "requires_reference_audio": False,
                "requires_reference_text": False,
                "allow_voice_default_reference": True,
            },
            compatibility=compatibility or {
                "voice_model_required": True,
                "separate_checkpoint_required": False,
                "supported_engines": [
                    "gpt_sovits",
                ],
            },
        )

        return self.repository.create(
            profile
        )

    def list_profiles(
        self,
        include_archived=False,
    ):

        return self.repository.list(
            include_archived=include_archived
        )

    def get_profile(
        self,
        style_profile_id,
    ):

        return self.repository.load(
            style_profile_id
        )

    def rename(
        self,
        style_profile_id,
        display_name,
    ):

        profile = self.repository.load(
            style_profile_id
        )

        display_name = self.normalize_display_name(
            display_name
        )

        errors = self.validate_display_name(
            display_name
        )

        if errors:

            raise ValueError(
                ",".join(
                    errors
                )
            )

        profile.display_name = display_name

        profile.updated_at = datetime.now().isoformat()

        return self.repository.update(
            profile
        )

    def normalize_display_name(
        self,
        display_name,
    ):

        return unicodedata.normalize(
            "NFC",
            str(
                display_name or ""
            ).strip(),
        )

    def validate_display_name(
        self,
        display_name,
    ):

        errors = []

        if not display_name:

            errors.append(
                "style_profile_name_required"
            )

        if len(
            display_name
        ) > 120:

            errors.append(
                "style_profile_name_too_long"
            )

        if any(
            ord(
                char
            )
            < 32
            for char in display_name
        ):

            errors.append(
                "style_profile_name_control_character"
            )

        return errors

    def update_description(
        self,
        style_profile_id,
        description,
    ):

        profile = self.repository.load(
            style_profile_id
        )

        profile.description = str(
            description or ""
        )

        profile.updated_at = datetime.now().isoformat()

        return self.repository.update(
            profile
        )

    def link_dataset(
        self,
        style_profile_id,
        dataset_reference,
    ):

        profile = self.repository.load(
            style_profile_id
        )

        profile.dataset_reference = dataset_reference or {}

        profile.status = STYLE_STATUS_SOURCE_READY

        profile.updated_at = datetime.now().isoformat()

        return self.repository.update(
            profile
        )

    def link_source_assets(
        self,
        style_profile_id,
        audio_asset_ids=None,
        text_asset_ids=None,
        manifest_asset_id="",
        validation_report_asset_id="",
    ):

        profile = self.repository.load(
            style_profile_id
        )

        profile.source_assets = {
            "audio_asset_ids": [
                str(
                    item
                )
                for item in audio_asset_ids or []
            ],
            "text_asset_ids": [
                str(
                    item
                )
                for item in text_asset_ids or []
            ],
            "manifest_asset_id": str(
                manifest_asset_id or ""
            ),
            "validation_report_asset_id": str(
                validation_report_asset_id or ""
            ),
        }

        profile.updated_at = datetime.now().isoformat()

        if (
            profile.source_assets[
                "audio_asset_ids"
            ]
            or profile.source_assets[
                "text_asset_ids"
            ]
            or profile.source_assets[
                "manifest_asset_id"
            ]
        ):

            profile.status = STYLE_STATUS_SOURCE_READY

        return self.repository.update(
            profile
        )

    def readiness(
        self,
        style_profile_id,
    ):

        try:

            profile = self.repository.load(
                style_profile_id
            )

        except FileNotFoundError:

            return {
                "style_profile_id": style_profile_id,
                "status": "missing",
                "available": False,
                "degraded": True,
                "blocked": False,
                "message_vi": (
                    "Du lieu tham chieu da lien ket khong con ton tai hoac chua duoc nhap tren may nay."
                ),
            }

        integrity = self.integrity.verify(
            style_profile_id,
            self.repository,
        )

        generation_usage = "degraded"

        return {
            "style_profile_id": style_profile_id,
            "display_name": profile.display_name,
            "status": profile.status,
            "available": integrity.get(
                "ok",
                False,
            ),
            "degraded": not integrity.get(
                "ok",
                False,
            )
            or generation_usage == "degraded",
            "blocked": False,
            "capabilities": profile.capabilities,
            "generation_usage": generation_usage,
            "message_vi": (
                "Style Profile san sang quan ly; engine hien tai chua bao dam tach prosody tuyet doi."
            ),
            "integrity": integrity,
        }

    def prepare_extraction(
        self,
        style_profile_id,
        capabilities=None,
    ):

        return self.extraction.prepare_extraction(
            style_profile_id,
            capabilities=capabilities,
        )

    def link_voice_default(
        self,
        voice,
        style_profile_id,
        allow_variant_override=True,
        fallback_mode="degraded",
    ):

        config = voice.config

        config.reading_style = {
            "default_style_profile_id": style_profile_id,
            "allow_variant_override": bool(
                allow_variant_override
            ),
            "fallback_mode": fallback_mode,
        }

        self.voice_service.save(
            voice
        )

        return voice

    def bind_variant_style(
        self,
        voice,
        variant_id,
        style_profile_id,
        style_mode=STYLE_MODE_EXPLICIT,
        style_strength=1.0,
        reference_override=None,
    ):

        profile = self.repository.load(
            style_profile_id
        )

        found = False

        for variant in voice.config.variants:

            if variant.get(
                "id",
                "",
            ) != variant_id:

                continue

            variant["style_profile_id"] = profile.style_profile_id
            variant["style_mode"] = style_mode
            variant["style_strength"] = float(
                style_strength
            )
            variant["reference_override"] = reference_override or {}
            variant["separate_model_required"] = False
            variant["readiness"] = {
                "status": "DEGRADED",
                "reason": "style_profile_generate_usage_degraded",
            }
            found = True

        if not found:

            raise ValueError(
                "variant_not_found"
            )

        self.voice_service.save(
            voice
        )

        return voice

    def variant_readiness(
        self,
        voice,
        variant_id,
    ):

        for variant in voice.config.variants:

            if variant.get(
                "id",
                "",
            ) != variant_id:

                continue

            style_profile_id = variant.get(
                "style_profile_id",
                "",
            )

            if not style_profile_id:

                return {
                    "status": "READY",
                    "reason": "voice_default_style",
                    "separate_model_required": False,
                }

            style = self.readiness(
                style_profile_id
            )

            return {
                "status": "DEGRADED"
                if style.get(
                    "degraded",
                    False,
                )
                else "READY",
                "reason": style.get(
                    "generation_usage",
                    "",
                ),
                "style_profile_id": style_profile_id,
                "separate_model_required": False,
            }

        return {
            "status": "MISSING",
            "reason": "variant_not_found",
            "separate_model_required": False,
        }

    def unlink_voice_default(
        self,
        voice,
    ):

        voice.config.reading_style = {
            "default_style_profile_id": "",
            "allow_variant_override": True,
            "fallback_mode": "degraded",
        }

        self.voice_service.save(
            voice
        )

        return voice

    def voices_using_profile(
        self,
        style_profile_id,
    ):

        result = []

        for name in self.voice_service.list():

            try:

                voice = self.voice_service.load(
                    name
                )

            except Exception:

                continue

            reading_style = getattr(
                voice.config,
                "reading_style",
                {},
            )

            if reading_style.get(
                "default_style_profile_id"
            ) == style_profile_id:

                result.append(
                    {
                        "voice_id": voice.id,
                        "voice_name": voice.name,
                        "link_type": "voice_default",
                    }
                )

            for variant in voice.variants:

                if variant.get(
                    "style_profile_id",
                    "",
                ) == style_profile_id:

                    result.append(
                        {
                            "voice_id": voice.id,
                            "voice_name": voice.name,
                            "variant_id": variant.get(
                                "id",
                                "",
                            ),
                            "link_type": "variant",
                        }
                    )

        return result

    def validate_source(
        self,
        dataset_reference,
    ):

        path = str(
            (
                dataset_reference
                or {}
            ).get(
                "metadata_path",
                "",
            )
            or (
                dataset_reference
                or {}
            ).get(
                "path",
                "",
            )
        )

        if not path:

            return {
                "ok": False,
                "errors": [
                    "source_path_required",
                ],
            }

        if not Path(
            path
        ).exists():

            return {
                "ok": False,
                "errors": [
                    "source_path_missing",
                ],
            }

        return {
            "ok": True,
            "errors": [],
        }


def variant_style_defaults():

    return {
        "style_profile_id": "",
        "style_mode": STYLE_MODE_INHERIT,
        "style_strength": 1.0,
    }


def normalize_variant_style(
    variant,
):

    variant = dict(
        variant or {}
    )

    for key, value in variant_style_defaults().items():

        variant.setdefault(
            key,
            value,
        )

    if variant[
        "style_mode"
    ] not in {
        STYLE_MODE_INHERIT,
        STYLE_MODE_EXPLICIT,
        STYLE_MODE_DISABLED,
    }:

        variant["style_mode"] = STYLE_MODE_INHERIT

    try:

        variant["style_strength"] = float(
            variant.get(
                "style_strength",
                1.0,
            )
        )

    except Exception:

        variant["style_strength"] = 1.0

    return variant
