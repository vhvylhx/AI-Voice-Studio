from __future__ import annotations

import json
import wave
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

from src.services.controlled_runtime_smoke_test_service import (
    DIAGNOSTIC_TEXT,
    ControlledRuntimeSmokeTestService,
)
from src.services.production_reference_binding_service import (
    ProductionReferenceBinding,
    ProductionReferenceBindingError,
)


class _SnapshotService:

    def __init__(self, binding=None, error=None):
        self.binding = binding
        self.error = error
        self.calls = 0

    def get_binding(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.binding


class _Provider:

    def __init__(self, *, error=None, invalid_wav=False):
        self.error = error
        self.invalid_wav = invalid_wav
        self.calls = []
        self.last_report = {
            "runtime": {
                "doctor_status": "READY",
                "profile_id": "runtime_01424",
            }
        }

    def __call__(self, artifact, output_path, diagnostic_text=None):
        self.calls.append(
            {
                "artifact": artifact,
                "output_path": output_path,
                "diagnostic_text": diagnostic_text,
            }
        )
        if self.error is not None:
            raise self.error
        if self.invalid_wav:
            Path(output_path).write_bytes(b"invalid-wav")
            return output_path
        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(32000)
            wav.writeframes(b"\x00\x00" * 320)
        return output_path


def _binding():
    return ProductionReferenceBinding(
        winner_reference_variant="R3_DC_TRIM_HP",
        reference_selection=MappingProxyType({}),
        generalization=MappingProxyType({}),
        production_readiness=MappingProxyType(
            {
                "binding_id": "binding_01424",
                "readiness_status": "READY",
            }
        ),
    )


def _artifact():
    return SimpleNamespace(
        artifact_id="artifact_01424",
        session_id="session_01424",
        job_id="job_01424",
    )


def test_valid_binding_invokes_provider_and_writes_isolated_diagnostic_evidence(
    tmp_path,
):
    diagnostic_root = tmp_path / "diagnostics" / "controlled_runtime_smoke"
    provider = _Provider()
    service = ControlledRuntimeSmokeTestService(
        reference_binding_snapshot_service=_SnapshotService(_binding()),
        generate_provider=provider,
        diagnostic_root=diagnostic_root,
    )

    result = service.run(_artifact())

    expected_output = diagnostic_root / "artifact_01424" / "diagnostic.wav"
    assert result.status == "SUCCESS"
    assert result.output_path == expected_output
    assert len(provider.calls) == 1
    assert provider.calls[0]["diagnostic_text"] == DIAGNOSTIC_TEXT
    assert provider.calls[0]["output_path"] == expected_output
    assert expected_output.is_file()
    assert not (tmp_path / "outputs").exists()
    assert not (tmp_path / "projects").exists()

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    assert evidence["session_id"] == "session_01424"
    assert evidence["job_id"] == "job_01424"
    assert evidence["binding_identity"] == "binding_01424"
    assert evidence["winner_reference_variant"] == "R3_DC_TRIM_HP"
    assert evidence["engine_provider"] == "_Provider"
    assert evidence["runtime_configuration"]["profile_id"] == "runtime_01424"
    assert evidence["output_path"] == str(expected_output)
    assert evidence["output_checksum_sha256"]
    assert evidence["artifact_validation"]["ok"] is True
    assert evidence["success"] is True
    assert evidence["blocker"] is None


def test_existing_diagnostic_files_are_not_overwritten_or_reinvoked(tmp_path):
    diagnostic_root = tmp_path / "diagnostics" / "controlled_runtime_smoke"
    provider = _Provider()
    snapshot_service = _SnapshotService(_binding())
    service = ControlledRuntimeSmokeTestService(
        reference_binding_snapshot_service=snapshot_service,
        generate_provider=provider,
        diagnostic_root=diagnostic_root,
    )

    first_result = service.run(_artifact())
    assert first_result.status == "SUCCESS"
    assert first_result.output_path is not None
    output_path = first_result.output_path
    evidence_path = first_result.evidence_path
    original_wav = output_path.read_bytes()
    original_evidence = evidence_path.read_bytes()

    second_result = service.run(_artifact())

    assert second_result.status == "BLOCKED"
    assert second_result.blocker == "DIAGNOSTIC_OUTPUT_ALREADY_EXISTS"
    assert second_result.output_path is None
    assert snapshot_service.calls == 1
    assert len(provider.calls) == 1
    assert output_path.read_bytes() == original_wav
    assert evidence_path.read_bytes() == original_evidence


def test_invalid_binding_does_not_create_diagnostic_input_or_wav_or_call_provider(
    tmp_path,
):
    diagnostic_root = tmp_path / "diagnostics" / "controlled_runtime_smoke"
    provider = _Provider()
    service = ControlledRuntimeSmokeTestService(
        reference_binding_snapshot_service=_SnapshotService(
            error=ProductionReferenceBindingError(
                "PRODUCTION_REFERENCE_BINDING_READINESS_NOT_READY"
            )
        ),
        generate_provider=provider,
        diagnostic_root=diagnostic_root,
    )

    result = service.run(_artifact())

    run_dir = diagnostic_root / "artifact_01424"
    assert result.status == "BLOCKED"
    assert result.output_path is None
    assert provider.calls == []
    assert not (run_dir / "diagnostic.wav").exists()
    assert not (run_dir / "input" / "diagnostic_input.txt").exists()

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    assert evidence["success"] is False
    assert evidence["blocker"] == "PRODUCTION_REFERENCE_BINDING_READINESS_NOT_READY"
    assert evidence["output_path"] is None


def test_invalid_wav_is_not_reported_as_success(tmp_path):
    provider = _Provider(invalid_wav=True)
    service = ControlledRuntimeSmokeTestService(
        reference_binding_snapshot_service=_SnapshotService(_binding()),
        generate_provider=provider,
        diagnostic_root=tmp_path / "diagnostics" / "controlled_runtime_smoke",
    )

    result = service.run(_artifact())

    assert result.status == "FAILED"
    assert result.output_path is None
    assert result.blocker == "DIAGNOSTIC_WAV_PROBE_FAILED"
    assert len(provider.calls) == 1

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    assert evidence["session_id"] == "session_01424"
    assert evidence["job_id"] == "job_01424"
    assert evidence["success"] is False
    assert evidence["artifact_validation"] is None
    assert evidence["blocker"] == "DIAGNOSTIC_WAV_PROBE_FAILED"


def test_engine_failure_is_recorded_without_reporting_diagnostic_output(
    tmp_path,
):
    provider = _Provider(error=RuntimeError("GPT_SOVITS_RUNTIME_BLOCKED"))
    service = ControlledRuntimeSmokeTestService(
        reference_binding_snapshot_service=_SnapshotService(_binding()),
        generate_provider=provider,
        diagnostic_root=tmp_path / "diagnostics" / "controlled_runtime_smoke",
    )

    result = service.run(_artifact())

    assert result.status == "FAILED"
    assert result.output_path is None
    assert result.blocker == "GPT_SOVITS_RUNTIME_BLOCKED"
    assert len(provider.calls) == 1
    assert not (
        tmp_path
        / "diagnostics"
        / "controlled_runtime_smoke"
        / "artifact_01424"
        / "diagnostic.wav"
    ).exists()

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    assert evidence["binding_identity"] == "binding_01424"
    assert evidence["success"] is False
    assert evidence["blocker"] == "GPT_SOVITS_RUNTIME_BLOCKED"
    assert evidence["output_path"] is None