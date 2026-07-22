from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from src.models.generate_pipeline_foundation import GenerateArtifactRecord
from src.services.gpt_sovits_generate_provider import GPTSoVITSGenerateProvider
from src.services.production_reference_binding_service import (
    ProductionReferenceBindingError,
)


class _Repository:

    def __init__(
        self,
        root,
        request,
        plan,
    ):

        self.root = Path(
            root
        )
        self.request = request
        self.plan = plan

    def load_request(
        self,
        session_id,
    ):

        assert session_id == self.plan.session_id
        return self.request

    def load_plan(
        self,
        session_id,
    ):

        assert session_id == self.plan.session_id
        return self.plan

    def session_dir(
        self,
        session_id,
    ):

        assert session_id == self.plan.session_id
        return self.root / session_id


class _GenerateSessionService:

    def __init__(
        self,
        repository,
    ):

        self.repository = repository


class _VoiceService:

    def validate_gpt_sovits(
        self,
        voice,
    ):

        return {
            "ready": True,
            "missing": [],
        }


class _Engine:

    def __init__(
        self,
    ):

        self.root = "runtime"

    def is_available(
        self,
    ):

        return True


class _EngineManager:

    def __init__(
        self,
    ):

        self.engine = _Engine()
        self.calls = []

    def get(
        self,
        engine_id,
    ):

        assert engine_id == "gpt_sovits"
        return self.engine

    def generate(
        self,
        **kwargs,
    ):

        self.calls.append(
            kwargs
        )
        return kwargs["output_file"]


class _BindingGate:

    def __init__(
        self,
        error=None,
    ):

        self.error = error
        self.calls = 0

    def get_binding(
        self,
    ):

        self.calls += 1

        if self.error is not None:

            raise self.error

        return SimpleNamespace(
            winner_reference_variant="R3_DC_TRIM_HP"
        )


def _build_provider(
    tmp_path,
    binding_gate,
):
    session_id = "session_01424"
    unit_id = "unit_01424"
    request = SimpleNamespace(
        voice_id="voice_01424",
        selection=SimpleNamespace(
            variant_id="default",
            speed=1.15,
            style_id="natural",
        ),
    )
    unit = SimpleNamespace(
        unit_id=unit_id,
        text="Nội dung inference giữ nguyên.",
    )
    plan = SimpleNamespace(
        session_id=session_id,
        units=[unit],
    )
    repository = _Repository(
        tmp_path,
        request,
        plan,
    )
    engine_manager = _EngineManager()
    voice = SimpleNamespace(
        id="voice_01424",
        config=SimpleNamespace(
            runtime_profile_id="",
            engine_path="",
        ),
    )
    provider = GPTSoVITSGenerateProvider(
        generate_session_service=_GenerateSessionService(
            repository
        ),
        engine_manager=engine_manager,
        voice_service=_VoiceService(),
        current_voice=None,
        runtime_profiles=SimpleNamespace(
            list_profiles=lambda: [],
        ),
        reference_binding_snapshot_service=binding_gate,
    )
    provider.resolve_voice = lambda voice_id: voice

    artifact = GenerateArtifactRecord(
        artifact_id="artifact_01424",
        session_id=session_id,
        unit_id=unit_id,
        project_id="project_01424",
        plan_id="plan_01424",
    )

    return provider, engine_manager, artifact


def test_production_consumer_uses_binding_gate_without_changing_engine_arguments(
    tmp_path,
):
    binding_gate = _BindingGate()
    provider, engine_manager, artifact = _build_provider(
        tmp_path,
        binding_gate,
    )
    output_file = tmp_path / "temp" / "unit.wav"

    result = provider(
        artifact.to_dict(),
        output_file,
    )

    assert result == output_file
    assert binding_gate.calls == 1
    assert len(
        engine_manager.calls
    ) == 1

    call = engine_manager.calls[0]

    assert call["output_file"] == output_file
    assert call["voice"].id == "voice_01424"
    assert call["variant"] == "default"
    assert call["speed"] == 1.15
    assert call["style"] == "natural"
    assert call["text_file"].read_text(
        encoding="utf-8"
    ) == "Nội dung inference giữ nguyên."


def test_production_consumer_fails_closed_before_text_or_engine_when_binding_not_ready(
    tmp_path,
):
    binding_gate = _BindingGate(
        ProductionReferenceBindingError(
            "SNAPSHOT_NOT_READY"
        )
    )
    provider, engine_manager, artifact = _build_provider(
        tmp_path,
        binding_gate,
    )
    output_file = tmp_path / "temp" / "unit.wav"

    with pytest.raises(
        ProductionReferenceBindingError,
        match="SNAPSHOT_NOT_READY",
    ):
        provider(
            artifact.to_dict(),
            output_file,
        )

    text_file = (
        tmp_path
        / artifact.session_id
        / "temp"
        / "unit_text"
        / f"{artifact.unit_id}.txt"
    )

    assert binding_gate.calls == 1
    assert engine_manager.calls == []
    assert not text_file.exists()
    assert not output_file.parent.exists()


def test_production_consumer_has_no_direct_artifact_winner_resolution():
    provider_source = Path(
        "src/services/gpt_sovits_generate_provider.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "reference_binding_snapshot_service.get_binding()" in provider_source
    assert "winner_reference_variant" not in provider_source
    assert "load_winner_reference_variant" not in provider_source
    assert "reference_selection" not in provider_source
    assert "generalization" not in provider_source
    assert "production_readiness" not in provider_source