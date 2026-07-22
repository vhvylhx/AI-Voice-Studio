from __future__ import annotations

import hashlib
import json
from pathlib import Path

from models.language_capability import (
    ENGINE_GPT_SOVITS,
    ENGINE_VIETNAMESE,
    LANGUAGE_STATUS_BLOCKED,
    LANGUAGE_STATUS_READY,
    LANGUAGE_STATUS_UNAVAILABLE,
    LANGUAGE_STATUS_UNVERIFIED,
    LanguageRoute,
    VoiceEngineBinding,
)
from services.language_catalog_service import LanguageCatalogService
from services.language_detection_service import LanguageDetectionService
from services.voice_service import VoiceService


class EngineCapabilityRouter:

    def __init__(
        self,
        voice_service=None,
        language_catalog=None,
        language_detector=None,
    ):

        self.voice_service = voice_service or VoiceService()

        self.language_catalog = (
            language_catalog
            or LanguageCatalogService()
        )

        self.language_detector = (
            language_detector
            or LanguageDetectionService(
                self.language_catalog
            )
        )

    def voice_language_capabilities(
        self,
        voice_id,
    ):

        voice = self.voice_service.find_by_id(
            voice_id
        )

        if voice is None:

            return None

        languages = []

        enabled = set(
            self.enabled_languages(
                voice
            )
        )

        for definition in self.language_catalog.list_languages():

            code = definition[
                "code"
            ]

            route = self.route_language(
                voice,
                code,
            )

            languages.append(
                {
                    **definition,
                    "enabled": code in enabled,
                    "route": route.to_dict(),
                }
            )

        return {
            "voice_id": voice.id,
            "display_name": voice.display_name,
            "language_selection_mode": getattr(
                voice.config,
                "language_selection_mode",
                "selected",
            ),
            "default_language": getattr(
                voice.config,
                "default_language",
                "vi",
            ),
            "enabled_languages": self.enabled_languages(
                voice
            ),
            "languages": languages,
            "summary": self.readiness_summary(
                languages
            ),
        }

    def enabled_languages(
        self,
        voice,
    ):

        configured = getattr(
            voice.config,
            "enabled_languages",
            None,
        )

        normalized = self.language_catalog.normalize_many(
            configured or []
        )

        return normalized or [
            "vi",
        ]

    def route_text(
        self,
        voice_id,
        text,
        explicit_language="",
    ):

        voice = self.voice_service.find_by_id(
            voice_id
        )

        if voice is None:

            return {
                "ok": False,
                "code": "VOICE_NOT_FOUND",
                "segments": [],
            }

        segments = self.language_detector.segment_text(
            text,
            explicit_language=explicit_language,
        )

        return {
            "ok": True,
            "voice_id": voice.id,
            "segments": [
                {
                    **segment.to_dict(),
                    "route": self.route_language(
                        voice,
                        segment.language_code,
                    ).to_dict(),
                }
                for segment in segments
            ],
        }

    def route_language(
        self,
        voice,
        language_code,
    ):

        code = self.language_catalog.normalize(
            language_code
        )

        enabled = self.enabled_languages(
            voice
        )

        if code not in enabled:

            return LanguageRoute(
                language_code=code,
                status=LANGUAGE_STATUS_BLOCKED,
                reason="LANGUAGE_NOT_ENABLED",
                blockers=[
                    "language_not_enabled",
                ],
            )

        binding = self.binding_for(
            voice,
            code,
        )

        if not binding.engine_id:

            return LanguageRoute(
                language_code=code,
                status=LANGUAGE_STATUS_BLOCKED,
                reason="LANGUAGE_ENGINE_UNCONFIGURED",
                blockers=[
                    "language_engine_unconfigured",
                ],
            )

        if (
            code == "vi"
            and binding.engine_id == ENGINE_GPT_SOVITS
        ):

            return LanguageRoute(
                language_code=code,
                engine_id=binding.engine_id,
                runtime_profile_id=binding.runtime_profile_id,
                status=LANGUAGE_STATUS_BLOCKED,
                reason="VI_REQUIRES_VIETNAMESE_ENGINE",
                blockers=[
                    "vietnamese_engine_required",
                ],
            )

        blockers = self.binding_blockers(
            voice,
            binding,
        )

        if blockers:

            return LanguageRoute(
                language_code=code,
                engine_id=binding.engine_id,
                runtime_profile_id=binding.runtime_profile_id,
                status=LANGUAGE_STATUS_BLOCKED,
                reason=blockers[
                    0
                ].upper(),
                gpt_sovits_language=(
                    self.language_catalog.gpt_sovits_mapping().get(
                        code,
                        "",
                    )
                ),
                fingerprint=self.binding_fingerprint(
                    voice,
                    binding,
                ),
                blockers=blockers,
                warnings=binding.compatibility_notes,
            )

        if not binding.inference_verified:

            return LanguageRoute(
                language_code=code,
                engine_id=binding.engine_id,
                runtime_profile_id=binding.runtime_profile_id,
                status=LANGUAGE_STATUS_UNVERIFIED,
                reason="LANGUAGE_INFERENCE_UNVERIFIED",
                gpt_sovits_language=(
                    self.language_catalog.gpt_sovits_mapping().get(
                        code,
                        "",
                    )
                ),
                fingerprint=self.binding_fingerprint(
                    voice,
                    binding,
                ),
                blockers=[
                    "language_inference_unverified",
                ],
                warnings=binding.compatibility_notes,
            )

        return LanguageRoute(
            language_code=code,
            engine_id=binding.engine_id,
            runtime_profile_id=binding.runtime_profile_id,
            status=LANGUAGE_STATUS_READY,
            reason="READY",
            gpt_sovits_language=(
                self.language_catalog.gpt_sovits_mapping().get(
                    code,
                    "",
                )
            ),
            fingerprint=self.binding_fingerprint(
                voice,
                binding,
            ),
            warnings=binding.compatibility_notes,
        )

    def binding_for(
        self,
        voice,
        language_code,
    ):

        bindings = getattr(
            voice.config,
            "engine_bindings",
            {},
        ) or {}

        data = bindings.get(
            language_code,
            {},
        )

        if not data:

            data = self.default_binding_data(
                language_code
            )

        return VoiceEngineBinding.from_dict(
            data
        )

    def default_binding_data(
        self,
        language_code,
    ):

        engine_id = self.language_catalog.default_engine_for(
            language_code
        )

        status = (
            "blocked_unconfigured_engine"
            if engine_id == ENGINE_VIETNAMESE
            else "unconfigured"
        )

        return {
            "language_code": language_code,
            "engine_id": engine_id,
            "status": status,
            "active": True,
        }

    def binding_blockers(
        self,
        voice,
        binding,
    ):

        if binding.engine_id == ENGINE_VIETNAMESE:

            return [
                "vietnamese_engine_unconfigured",
            ]

        if binding.engine_id != ENGINE_GPT_SOVITS:

            return [
                "engine_adapter_unavailable",
            ]

        missing = []

        model_binding = dict(
            binding.model_binding or {}
        )

        reference_binding = dict(
            binding.reference_binding or {}
        )

        gpt_model = model_binding.get(
            "gpt_model",
        ) or voice.config.gpt_model

        sovits_model = model_binding.get(
            "sovits_model",
        ) or voice.config.sovits_model

        reference_audio = reference_binding.get(
            "reference_audio",
        ) or voice.config.reference_audio

        reference_text = reference_binding.get(
            "reference_text",
        ) or voice.config.reference_text

        for key, value, suffixes in [
            (
                "gpt_model",
                gpt_model,
                {
                    ".ckpt",
                },
            ),
            (
                "sovits_model",
                sovits_model,
                {
                    ".pth",
                },
            ),
            (
                "reference_audio",
                reference_audio,
                {
                    ".wav",
                    ".mp3",
                    ".flac",
                    ".m4a",
                },
            ),
        ]:

            if not str(
                value or ""
            ).strip():

                missing.append(
                    f"{key}_missing"
                )

                continue

            path = Path(
                value
            )

            if not path.exists() or path.suffix.lower() not in suffixes:

                missing.append(
                    f"{key}_invalid"
                )

        if not str(
            reference_text or ""
        ).strip():

            missing.append(
                "reference_text_missing"
            )

        if not binding.runtime_profile_id and not voice.config.runtime_profile_id:

            missing.append(
                "runtime_profile_missing"
            )

        return missing

    def binding_fingerprint(
        self,
        voice,
        binding,
    ):

        payload = {
            "fingerprint_version": 1,
            "voice_id": voice.id,
            "language_code": binding.language_code,
            "engine_id": binding.engine_id,
            "runtime_profile_id": (
                binding.runtime_profile_id
                or voice.config.runtime_profile_id
            ),
            "model_binding": binding.model_binding,
            "reference_binding": binding.reference_binding,
            "text_frontend_version": "language_router_v1",
            "adapter_version": "avs01420_foundation",
            "gpt_sovits_language": (
                self.language_catalog.gpt_sovits_mapping().get(
                    binding.language_code,
                    "",
                )
            ),
        }

        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        )

        return hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()

    def readiness_summary(
        self,
        languages,
    ):

        enabled = [
            item
            for item in languages
            if item.get(
                "enabled"
            )
        ]

        if not enabled:

            return {
                "status": LANGUAGE_STATUS_UNAVAILABLE,
                "reason": "NO_LANGUAGE_ENABLED",
            }

        ready = [
            item
            for item in enabled
            if item.get(
                "route",
                {},
            ).get(
                "status"
            )
            == LANGUAGE_STATUS_READY
        ]

        if len(
            ready
        ) == len(
            enabled
        ):

            return {
                "status": "READY_ALL_ENABLED",
                "ready": len(
                    ready
                ),
                "enabled": len(
                    enabled
                ),
            }

        if ready:

            return {
                "status": "READY_PARTIAL",
                "ready": len(
                    ready
                ),
                "enabled": len(
                    enabled
                ),
            }

        return {
            "status": "BLOCKED",
            "ready": 0,
            "enabled": len(
                enabled
            ),
        }
