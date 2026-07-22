from pathlib import Path

from engines.gpt_sovits_engine import GPTSoVITSEngine
from models.generate_pipeline_foundation import GenerateArtifactRecord
from services.production_reference_binding_snapshot_service import (
    ProductionReferenceBindingSnapshotService,
)
from services.runtime_profile_service import RuntimeProfileService


class GPTSoVITSGenerateProvider:

    def __init__(
        self,
        generate_session_service,
        engine_manager,
        voice_service=None,
        current_voice=None,
        runtime_profiles=None,
        reference_binding_snapshot_service=None,
    ):

        self.generate_session_service = generate_session_service

        self.engine_manager = engine_manager

        self.voice_service = voice_service

        self.current_voice = current_voice

        self.runtime_profiles = (
            runtime_profiles
            or RuntimeProfileService()
        )

        self.reference_binding_snapshot_service = (
            reference_binding_snapshot_service
            or ProductionReferenceBindingSnapshotService()
        )

        self.last_report = {}

    def __call__(
        self,
        artifact,
        temp_path,
        diagnostic_text=None,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        request = self.generate_session_service.repository.load_request(
            artifact.session_id
        )

        plan = self.generate_session_service.repository.load_plan(
            artifact.session_id
        )

        if request is None or plan is None:

            raise RuntimeError(
                "generate_session_context_missing"
            )

        unit = self.find_unit(
            plan,
            artifact.unit_id,
        )

        if unit is None:

            raise RuntimeError(
                "generate_unit_not_found"
            )

        voice = self.resolve_voice(
            request.voice_id
        )

        self.validate_voice(
            voice
        )

        engine = self.resolve_engine(
            voice
        )

        runtime_report = self.validate_runtime(
            voice,
            engine,
        )

        self.reference_binding_snapshot_service.get_binding()

        text_file = self.write_unit_text(
            artifact,
            unit.text if diagnostic_text is None else diagnostic_text,
            diagnostic_root=(
                None
                if diagnostic_text is None
                else Path(temp_path).parent / "input"
            ),
        )

        Path(
            temp_path
        ).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = self.engine_manager.generate(
            text_file=text_file,
            output_file=temp_path,
            voice=voice,
            variant=request.selection.variant_id,
            speed=request.selection.speed,
            style=request.selection.style_id,
        )

        self.last_report = {
            "ok": True,
            "runtime": runtime_report,
            "unit_id": unit.unit_id,
            "voice_id": voice.id,
            "output_file": str(
                result
            ),
            "command": getattr(
                getattr(
                    engine,
                    "adapter",
                    None,
                ),
                "last_command",
                [],
            ),
        }

        return result

    def find_unit(
        self,
        plan,
        unit_id,
    ):

        for unit in plan.units:

            if unit.unit_id == unit_id:

                return unit

        return None

    def resolve_voice(
        self,
        voice_id,
    ):

        if self.current_voice is not None:

            try:

                if self.current_voice.has_voice():

                    voice = self.current_voice.get()

                    if voice.id == voice_id:

                        return voice

            except Exception:

                pass

        if self.voice_service is None:

            raise RuntimeError(
                "voice_service_missing"
            )

        for name in self.voice_service.list():

            voice = self.voice_service.load(
                name
            )

            if voice.id == voice_id:

                return voice

        raise RuntimeError(
            f"voice_not_found:{voice_id}"
        )

    def validate_voice(
        self,
        voice,
    ):

        if self.voice_service is None:

            raise RuntimeError(
                "voice_service_missing"
            )

        report = self.voice_service.validate_gpt_sovits(
            voice
        )

        if not report.get(
            "ready",
            False,
        ):

            missing = ", ".join(
                report.get(
                    "missing",
                    []
                )
            )

            raise RuntimeError(
                f"voice_not_generate_ready:{missing}"
            )

        return report

    def resolve_engine(
        self,
        voice,
    ):

        engine = self.engine_manager.get(
            "gpt_sovits"
        )

        if engine is None:

            engine = GPTSoVITSEngine()

            self.engine_manager.register(
                engine
            )

        engine_path = getattr(
            voice.config,
            "engine_path",
            "",
        )

        if engine_path:

            engine.set_path(
                engine_path
            )

        return engine

    def validate_runtime(
        self,
        voice,
        engine,
    ):

        profile = self.select_runtime_profile(
            getattr(
                voice.config,
                "runtime_profile_id",
                "",
            )
        )

        if profile is not None:

            report = self.runtime_profiles.validate(
                profile,
                require_generate=True,
            )

            if report.get(
                "doctor_status"
            ) != "READY":

                raise RuntimeError(
                    "runtime_doctor_not_ready:"
                    + report.get(
                        "doctor_status",
                        "UNKNOWN",
                    )
                )

            if not getattr(
                engine,
                "root",
                None,
            ):

                engine.set_path(
                    self.runtime_profiles.resolve_path(
                        profile.runtime_path
                    )
                )

            return report

        if not engine.is_available():

            raise RuntimeError(
                "gpt_sovits_runtime_not_configured"
            )

        return {
            "doctor_status": "READY",
            "profile_id": "",
        }

    def select_runtime_profile(
        self,
        profile_id="",
    ):

        profiles = self.runtime_profiles.list_profiles()

        if profile_id:

            for profile in profiles:

                if profile.profile_id == profile_id:

                    return profile

            return None

        for profile in profiles:

            if profile.is_default:

                return profile

        return profiles[0] if profiles else None

    def write_unit_text(
        self,
        artifact,
        text,
        diagnostic_root=None,
    ):

        path = (
            Path(diagnostic_root)
            / "diagnostic_input.txt"
            if diagnostic_root is not None
            else self.generate_session_service.repository.session_dir(
                artifact.session_id
            )
            / "temp"
            / "unit_text"
            / f"{artifact.unit_id}.txt"
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            text,
            encoding="utf-8",
        )

        return path
