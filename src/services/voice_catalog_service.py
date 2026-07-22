from pathlib import Path

from services.engine_capability_router import EngineCapabilityRouter
from services.style_profile_service import StyleProfileService
from services.voice_service import VoiceService


class VoiceCatalogService:

    def __init__(
        self,
        voice_service=None,
        style_profile_service=None,
    ):

        self.voice_service = (
            voice_service
            or VoiceService()
        )

        self.style_profile_service = (
            style_profile_service
            or StyleProfileService(
                voice_service=self.voice_service
            )
        )

        self.language_router = EngineCapabilityRouter(
            voice_service=self.voice_service
        )

    def list_voices(
        self,
    ):

        items = []

        for name in self.voice_service.list():

            try:

                voice = self.voice_service.load(
                    name
                )

            except Exception:

                continue

            items.append(
                self.voice_summary(
                    voice
                )
            )

        return {
            "items": items,
        }

    def get_voice(
        self,
        voice_id,
    ):

        voice = self.find_voice(
            voice_id
        )

        if voice is None:

            return None

        data = self.voice_summary(
            voice
        )

        data["variants_url"] = (
            f"/api/v1/voices/{voice_id}/variants"
        )

        return data

    def list_variants(
        self,
        voice_id,
    ):

        voice = self.find_voice(
            voice_id
        )

        if voice is None:

            return None

        return {
            "voice_id": voice.id,
            "items": [
                self.variant_summary(
                    voice,
                    variant,
                )
                for variant in voice.variants
            ],
        }

    def catalog(
        self,
    ):

        voices = self.list_voices()[
            "items"
        ]

        variants = {}

        for voice in voices:

            voice_id = voice[
                "voice_id"
            ]

            variants[
                voice_id
            ] = self.list_variants(
                voice_id
            )[
                "items"
            ]

        return {
            "catalog_version": 1,
            "voices": voices,
            "variants": variants,
            "presets": [],
            "capabilities": {
                "formats": [
                    "wav",
                    "mp3",
                ],
                "sample_rates": [
                    32000,
                ],
                "job_api": True,
                "timeline_support": True,
                "variant_support": True,
                "style_profile_support": True,
            },
            "style_profiles": self.safe_style_profiles(),
        }

    def find_voice(
        self,
        voice_id,
    ):

        if hasattr(
            self.voice_service,
            "find_by_id",
        ):

            return self.voice_service.find_by_id(
                voice_id
            )

        for name in self.voice_service.list():

            try:

                voice = self.voice_service.load(
                    name
                )

            except Exception:

                continue

            if voice.id == voice_id:

                return voice

        return None

    def voice_summary(
        self,
        voice,
    ):

        validation = self.voice_service.validate_gpt_sovits(
            voice
        )

        config = voice.config

        reading_style = dict(
            getattr(
                config,
                "reading_style",
                {},
            )
            or {}
        )

        style_profile_id = reading_style.get(
            "default_style_profile_id",
            "",
        )

        style_profile = self.safe_style_profile(
            style_profile_id
        )

        return {
            "voice_id": voice.id,
            "display_name": voice.display_name,
            "folder_name": voice.name,
            "description": voice.description,
            "language": config.language,
            "default_language": getattr(
                config,
                "default_language",
                config.language,
            ),
            "enabled_languages": getattr(
                config,
                "enabled_languages",
                [
                    config.language,
                ],
            ),
            "language_selection_mode": getattr(
                config,
                "language_selection_mode",
                "selected",
            ),
            "language_capabilities_url": (
                f"/api/v1/voices/{voice.id}/language-capabilities"
            ),
            "model_status": (
                "ready"
                if validation.get(
                    "ready",
                    False,
                )
                else config.training_status
            ),
            "generation_ready": validation.get(
                "ready",
                False,
            ),
            "default_variant_id": config.default_variant_id,
            "reading_style": {
                "default_style_profile_id": style_profile_id,
                "allow_variant_override": reading_style.get(
                    "allow_variant_override",
                    True,
                ),
                "fallback_mode": reading_style.get(
                    "fallback_mode",
                    "degraded",
                ),
                "style_profile": style_profile,
            },
            "supported_formats": [
                "wav",
                "mp3",
            ],
            "supported_sample_rates": [
                32000,
            ],
            "supported_features": [
                "variant",
                "speed",
                "style",
                "timeline",
                "style_profile",
            ],
            "thumbnail": (
                f"/api/v1/assets/voices/{voice.id}/thumbnail"
                if Path(
                    voice.avatar
                ).exists()
                else ""
            ),
            "updated_at": config.updated_at,
            "missing": validation.get(
                "missing",
                [],
            ),
            "publish": {
                "publish_id": getattr(
                    config,
                    "publish_id",
                    "",
                ),
                "training_run_id": getattr(
                    config,
                    "published_training_run_id",
                    "",
                ),
                "validation_status": getattr(
                    config,
                    "publish_validation_status",
                    "unpublished",
                ),
                "published_at": getattr(
                    config,
                    "published_at",
                    "",
                ),
                "fingerprint": getattr(
                    config,
                    "publish_fingerprint",
                    "",
                ),
            },
        }

    def language_capabilities(
        self,
        voice_id,
    ):

        return self.language_router.voice_language_capabilities(
            voice_id
        )

    def variant_summary(
        self,
        voice,
        variant,
    ):

        variant_id = variant.get(
            "id",
            "",
        )

        return {
            "variant_id": variant_id,
            "display_name": variant.get(
                "name",
                variant_id,
            ),
            "category": variant.get(
                "category",
                "general",
            ),
            "description": variant.get(
                "description",
                "",
            ),
            "language": voice.config.language,
            "style_tags": variant.get(
                "style_tags",
                [],
            ),
            "speed": variant.get(
                "speed",
                1.0,
            ),
            "pitch": variant.get(
                "pitch",
                1.0,
            ),
            "emotion": variant.get(
                "emotion",
                "",
            ),
            "reference_style_id": variant.get(
                "reference_style_id",
                "",
            ),
            "style_profile_id": variant.get(
                "style_profile_id",
                "",
            ),
            "style_mode": variant.get(
                "style_mode",
                "inherit_voice_default",
            ),
            "style_strength": variant.get(
                "style_strength",
                1.0,
            ),
            "is_default": (
                variant_id
                == voice.config.default_variant_id
            ),
            "enabled": variant.get(
                "enabled",
                True,
            ),
            "compatibility": "generate_profile",
            "preview_url": (
                f"/api/v1/voices/{voice.id}/variants/{variant_id}/preview"
                if variant.get(
                    "preview",
                    "",
                )
                else ""
            ),
        }

    def safe_style_profiles(
        self,
    ):

        items = []

        try:

            profiles = self.style_profile_service.list_profiles()

        except Exception:

            return items

        for profile in profiles:

            items.append(
                self.safe_style_profile_from_model(
                    profile
                )
            )

        return items

    def safe_style_profile(
        self,
        style_profile_id,
    ):

        if not style_profile_id:

            return None

        try:

            profile = self.style_profile_service.get_profile(
                style_profile_id
            )

        except Exception:

            return {
                "style_profile_id": style_profile_id,
                "status": "missing",
            }

        return self.safe_style_profile_from_model(
            profile
        )

    def safe_style_profile_from_model(
        self,
        profile,
    ):

        return {
            "style_profile_id": profile.style_profile_id,
            "display_name": profile.display_name,
            "language": profile.language,
            "status": profile.status,
            "intended_use": getattr(
                profile,
                "intended_use",
                "generate_style_profile",
            ),
            "style_classification": getattr(
                profile,
                "style_classification",
                "style_only",
            ),
            "compatibility": getattr(
                profile,
                "compatibility",
                {},
            ),
            "capabilities": profile.capabilities,
            "default_tags": profile.default_tags,
            "updated_at": profile.updated_at,
        }
