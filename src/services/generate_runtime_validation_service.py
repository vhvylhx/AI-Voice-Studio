import hashlib
import json
import wave
from pathlib import Path

from services.runtime_profile_service import RuntimeProfileService


class GenerateRuntimeValidationService:

    SCHEMA_VERSION = 1

    def __init__(
        self,
        runtime_profiles=None,
        voice_service=None,
        smoke_root=None,
        app_root=None,
    ):

        self.app_root = Path(
            app_root or Path.cwd()
        ).resolve()

        self.runtime_profiles = (
            runtime_profiles
            or RuntimeProfileService(
                app_root=self.app_root
            )
        )

        self.voice_service = voice_service

        self.smoke_root = Path(
            smoke_root
            or self.app_root
            / "cache"
            / "generate_runtime_smoke"
        )

    def readiness(
        self,
        selection=None,
    ):

        environment = self.environment_readiness()

        selected_assets = self.selected_asset_readiness(
            selection or {}
        )

        fingerprint = ""

        if (
            environment.get(
                "status"
            )
            == "READY"
            and selected_assets.get(
                "status"
            )
            == "READY"
        ):

            fingerprint = self.fingerprint(
                environment,
                selected_assets,
            )

        real_inference = self.real_inference_readiness(
            fingerprint
        )

        generate_execution = self.generate_execution_status(
            environment,
            selected_assets,
            real_inference,
        )

        return {
            "schema_version": self.SCHEMA_VERSION,
            "status": generate_execution,
            "environment": environment,
            "selected_assets": selected_assets,
            "real_inference": real_inference,
            "fingerprint": fingerprint,
            "capabilities": {
                "generate_execution": generate_execution,
                "wav_output": "READY"
                if real_inference.get(
                    "status"
                )
                == "PASS"
                else generate_execution,
            },
            "false_positive_prevention": {
                "runtime_doctor_only_is_not_execution_ready": True,
                "requires_selected_voice_variant_reference": True,
                "requires_fresh_real_inference_smoke": True,
                "test_only_provider_does_not_unlock_production": True,
            },
        }

    def environment_readiness(
        self,
    ):

        profile = self.select_runtime_profile()

        if profile is None:

            return {
                "status": "UNAVAILABLE",
                "code": "runtime_profile_missing",
                "message_vi": "Chua cau hinh Runtime Profile GPT-SoVITS.",
                "profile": None,
                "report": None,
                "guidance": self.runtime_profiles.guidance(),
            }

        report = self.runtime_profiles.validate(
            profile,
            require_generate=True,
        )

        return {
            "status": report.get(
                "doctor_status",
                "UNKNOWN",
            ),
            "code": report.get(
                "status",
                "",
            ),
            "message_vi": "Environment runtime san sang."
            if report.get(
                "doctor_status"
            )
            == "READY"
            else "Environment runtime chua san sang.",
            "profile": profile.to_dict(),
            "report": report,
            "guidance": self.runtime_profiles.guidance(),
        }

    def selected_asset_readiness(
        self,
        selection,
    ):

        voice_id = str(
            selection.get(
                "voice_id",
                "",
            )
            or ""
        ).strip()

        variant_id = str(
            selection.get(
                "variant_id",
                "",
            )
            or ""
        ).strip()

        if not voice_id:

            return {
                "status": "BLOCKED",
                "code": "selection_missing",
                "message_vi": "Chua chon Voice/Variant/Reference de kiem tra Generate that.",
                "missing": [
                    "voice_id",
                    "variant_id",
                ],
            }

        if self.voice_service is None:

            return {
                "status": "BLOCKED",
                "code": "voice_service_missing",
                "message_vi": "VoiceService chua san sang.",
                "missing": [
                    "voice_service",
                ],
            }

        voice = self.find_voice(
            voice_id
        )

        if voice is None:

            return {
                "status": "BLOCKED",
                "code": "voice_not_found",
                "message_vi": "Khong tim thay Voice da chon.",
                "voice_id": voice_id,
                "missing": [
                    "voice",
                ],
            }

        variant_status = self.validate_variant(
            voice,
            variant_id,
        )

        voice_report = self.voice_service.validate_gpt_sovits(
            voice
        )

        missing = list(
            voice_report.get(
                "missing",
                [],
            )
        )

        if not variant_status.get(
            "ok",
            False,
        ):

            missing.append(
                "variant_id"
            )

        status = "READY" if not missing else "BLOCKED"

        return {
            "status": status,
            "code": "selected_assets_ready"
            if status == "READY"
            else "selected_assets_missing",
            "message_vi": "Voice/Variant/Reference san sang."
            if status == "READY"
            else "Voice/Variant/Reference chua du de Generate that.",
            "voice_id": voice.id,
            "voice_name": getattr(
                voice,
                "display_name",
                voice.name,
            ),
            "variant_id": variant_status.get(
                "variant_id",
                variant_id,
            ),
            "missing": missing,
            "voice_report": voice_report,
            "assets": self.voice_assets(
                voice
            ),
        }

    def real_inference_readiness(
        self,
        fingerprint,
    ):

        if not fingerprint:

            return {
                "status": "BLOCKED",
                "code": "fingerprint_missing",
                "message_vi": "Chua co fingerprint hop le de xac minh Real Smoke.",
            }

        report_path = self.smoke_report_path(
            fingerprint
        )

        if not report_path.exists():

            return {
                "status": "SKIPPED",
                "code": "real_smoke_not_run",
                "message_vi": "Chua chay Real GPT-SoVITS Smoke cho bo fingerprint nay.",
                "fingerprint": fingerprint,
                "report_path": str(
                    report_path
                ),
            }

        try:

            report = json.loads(
                report_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as exc:

            return {
                "status": "STALE",
                "code": "smoke_report_unreadable",
                "message_vi": "Khong doc duoc smoke report.",
                "fingerprint": fingerprint,
                "error": str(
                    exc
                ),
            }

        if report.get(
            "fingerprint"
        ) != fingerprint:

            return {
                "status": "STALE",
                "code": "fingerprint_mismatch",
                "message_vi": "Smoke report khong khop fingerprint hien tai.",
                "fingerprint": fingerprint,
                "report": report,
            }

        output = report.get(
            "output_wav",
            "",
        )

        wav = self.validate_wav(
            output
        )

        if (
            report.get(
                "status"
            )
            == "PASS"
            and wav.get(
                "ok"
            )
        ):

            return {
                "status": "PASS",
                "code": "real_inference_verified",
                "message_vi": "Real GPT-SoVITS Smoke da tao WAV hop le qua production pipeline.",
                "fingerprint": fingerprint,
                "report_path": str(
                    report_path
                ),
                "output_wav": output,
                "wav": wav,
            }

        return {
            "status": "STALE",
            "code": "smoke_output_invalid",
            "message_vi": "Smoke report ton tai nhung output WAV khong con hop le.",
            "fingerprint": fingerprint,
            "report_path": str(
                report_path
            ),
            "wav": wav,
            "report_status": report.get(
                "status",
                "",
            ),
        }

    def generate_execution_status(
        self,
        environment,
        selected_assets,
        real_inference,
    ):

        if environment.get(
            "status"
        ) != "READY":

            return "UNAVAILABLE"

        if selected_assets.get(
            "status"
        ) != "READY":

            return "BLOCKED"

        if real_inference.get(
            "status"
        ) == "PASS":

            return "READY"

        return "DEGRADED"

    def select_runtime_profile(
        self,
    ):

        profiles = self.runtime_profiles.list_profiles()

        for profile in profiles:

            if profile.is_default:

                return profile

        return profiles[0] if profiles else None

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

    def validate_variant(
        self,
        voice,
        variant_id,
    ):

        if not variant_id:

            variant_id = getattr(
                voice.config,
                "default_variant_id",
                "",
            )

        variant_ids = {
            item.get(
                "id",
                "",
            )
            for item in getattr(
                voice.config,
                "variants",
                []
            )
        }

        return {
            "ok": bool(
                variant_id
            )
            and variant_id in variant_ids,
            "variant_id": variant_id,
            "known_variant_ids": sorted(
                variant_ids
            ),
        }

    def voice_assets(
        self,
        voice,
    ):

        config = voice.config

        return {
            "gpt_model": self.file_snapshot(
                config.gpt_model
            ),
            "sovits_model": self.file_snapshot(
                config.sovits_model
            ),
            "reference_audio": self.file_snapshot(
                config.reference_audio
            ),
            "reference_text_sha256": hashlib.sha256(
                str(
                    config.reference_text or ""
                ).encode(
                    "utf-8"
                )
            ).hexdigest(),
            "runtime_profile_id": getattr(
                config,
                "runtime_profile_id",
                "",
            ),
        }

    def fingerprint(
        self,
        environment,
        selected_assets,
    ):

        report = environment.get(
            "report",
            {}
        ) or {}

        profile = environment.get(
            "profile",
            {}
        ) or {}

        scripts = (
            report.get(
                "checks",
                {},
            )
            .get(
                "gpt_sovits_scripts",
                {},
            )
        )

        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "profile_id": profile.get(
                "profile_id",
                "",
            ),
            "runtime_path": profile.get(
                "runtime_path",
                "",
            ),
            "python_path": profile.get(
                "python_path",
                "",
            ),
            "engine_version": profile.get(
                "engine_version",
                "",
            ),
            "inference_cli": scripts.get(
                "inference_cli",
                {},
            ),
            "voice_id": selected_assets.get(
                "voice_id",
                "",
            ),
            "variant_id": selected_assets.get(
                "variant_id",
                "",
            ),
            "assets": selected_assets.get(
                "assets",
                {},
            ),
            "pipeline": "generate_unit_production_v1",
        }

        raw = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode(
            "utf-8"
        )

        return hashlib.sha256(
            raw
        ).hexdigest()

    def file_snapshot(
        self,
        value,
    ):

        path = Path(
            value or ""
        )

        if not value:

            return {
                "path": "",
                "exists": False,
                "size": 0,
                "mtime_ns": 0,
            }

        try:

            stat = path.stat()

            return {
                "path": str(
                    path
                ),
                "exists": True,
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }

        except Exception:

            return {
                "path": str(
                    path
                ),
                "exists": False,
                "size": 0,
                "mtime_ns": 0,
            }

    def smoke_report_path(
        self,
        fingerprint,
    ):

        return (
            self.smoke_root
            / f"{fingerprint}.json"
        )

    def write_smoke_report(
        self,
        fingerprint,
        report,
    ):

        self.smoke_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = dict(
            report or {}
        )

        data[
            "fingerprint"
        ] = fingerprint

        self.smoke_report_path(
            fingerprint
        ).write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def validate_wav(
        self,
        path,
    ):

        if not path:

            return {
                "ok": False,
                "code": "output_missing",
            }

        file = Path(
            path
        )

        if not file.exists() or file.stat().st_size <= 0:

            return {
                "ok": False,
                "code": "output_missing",
                "path": str(
                    file
                ),
            }

        try:

            with wave.open(
                str(
                    file
                ),
                "rb",
            ) as wav:

                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frames = wav.getnframes()

        except Exception as exc:

            return {
                "ok": False,
                "code": "wav_probe_failed",
                "path": str(
                    file
                ),
                "error": str(
                    exc
                ),
            }

        return {
            "ok": (
                channels == 1
                and sample_rate == 32000
                and sample_width == 2
                and frames > 0
            ),
            "path": str(
                file
            ),
            "channels": channels,
            "sample_rate": sample_rate,
            "sample_width": sample_width,
            "frames": frames,
        }
