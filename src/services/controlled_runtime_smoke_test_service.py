"""Controlled runtime smoke test cho consumer generate production.

Workflow chỉ dành cho diagnostic và không thay đổi readiness production.
"""

from __future__ import annotations

import hashlib
import json
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from services.production_reference_binding_service import ProductionReferenceBinding


DIAGNOSTIC_TEXT = "Đây là kiểm tra runtime có kiểm soát."


@dataclass(frozen=True)
class ControlledRuntimeSmokeResult:
    """Kết quả có evidence của một controlled runtime smoke test."""

    status: str
    evidence_path: Path
    output_path: Path | None
    blocker: str | None


class ControlledRuntimeSmokeTestService:
    """Điều phối smoke test diagnostic, fail-closed trước khi gọi provider."""

    def __init__(
        self,
        *,
        reference_binding_snapshot_service,
        generate_provider: Callable[..., Path],
        diagnostic_root: str | Path = "diagnostics/controlled_runtime_smoke",
        wav_validator: Callable[[str | Path], dict[str, object]] | None = None,
    ) -> None:
        self.reference_binding_snapshot_service = reference_binding_snapshot_service
        self.generate_provider = generate_provider
        self.diagnostic_root = Path(diagnostic_root)
        self.wav_validator = wav_validator or self._validate_wav

    def run(self, artifact: object) -> ControlledRuntimeSmokeResult:
        """Chạy một smoke test với binding snapshot hợp lệ và output isolated."""
        run_dir = self.diagnostic_root / self._artifact_id(artifact)
        evidence_path = run_dir / "runtime_smoke_evidence.json"
        output_path = run_dir / "diagnostic.wav"

        if output_path.exists() or evidence_path.exists():
            return ControlledRuntimeSmokeResult(
                status="BLOCKED",
                evidence_path=evidence_path,
                output_path=None,
                blocker="DIAGNOSTIC_OUTPUT_ALREADY_EXISTS",
            )

        try:
            binding = self.reference_binding_snapshot_service.get_binding()
        except RuntimeError as error:
            return self._write_failure(
                evidence_path=evidence_path,
                artifact=artifact,
                blocker=str(error),
            )

        try:
            run_dir.mkdir(parents=True, exist_ok=True)
            result_path = Path(
                self.generate_provider(
                    artifact,
                    output_path,
                    diagnostic_text=DIAGNOSTIC_TEXT,
                )
            )
            if result_path != output_path or not output_path.is_file():
                raise RuntimeError("DIAGNOSTIC_WAV_OUTPUT_INVALID")

            artifact_validation = self.wav_validator(output_path)
            if not artifact_validation.get("ok", False):
                raise RuntimeError(
                    str(
                        artifact_validation.get(
                            "code",
                            "DIAGNOSTIC_WAV_OUTPUT_INVALID",
                        )
                    )
                )

            checksum = self._checksum(output_path)
            payload = {
                "status": "SUCCESS",
                "session_id": self._artifact_value(artifact, "session_id"),
                "job_id": self._artifact_value(artifact, "job_id"),
                "binding_identity": self._binding_identity(binding),
                "winner_reference_variant": binding.winner_reference_variant,
                "engine_provider": type(self.generate_provider).__name__,
                "runtime_configuration": self._runtime_configuration(),
                "output_path": str(output_path),
                "output_checksum_sha256": checksum,
                "artifact_validation": artifact_validation,
                "success": True,
                "blocker": None,
            }
            self._write_evidence(evidence_path, payload)
            return ControlledRuntimeSmokeResult(
                status="SUCCESS",
                evidence_path=evidence_path,
                output_path=output_path,
                blocker=None,
            )
        except Exception as error:
            return self._write_failure(
                evidence_path=evidence_path,
                artifact=artifact,
                blocker=str(error),
                binding=binding,
            )

    def _write_failure(
        self,
        *,
        evidence_path,
        artifact,
        blocker,
        binding: ProductionReferenceBinding | None = None,
    ):
        payload = {
            "status": "BLOCKED" if binding is None else "FAILED",
            "session_id": self._artifact_value(artifact, "session_id"),
            "job_id": self._artifact_value(artifact, "job_id"),
            "binding_identity": (
                None if binding is None else self._binding_identity(binding)
            ),
            "winner_reference_variant": (
                None if binding is None else binding.winner_reference_variant
            ),
            "engine_provider": type(self.generate_provider).__name__,
            "runtime_configuration": self._runtime_configuration(),
            "output_path": None,
            "output_checksum_sha256": None,
            "artifact_validation": None,
            "success": False,
            "blocker": blocker,
        }
        self._write_evidence(evidence_path, payload)
        return ControlledRuntimeSmokeResult(
            status=payload["status"],
            evidence_path=evidence_path,
            output_path=None,
            blocker=blocker,
        )

    @staticmethod
    def _artifact_id(artifact: object) -> str:
        artifact_id = getattr(artifact, "artifact_id", None)
        if artifact_id is None and isinstance(artifact, dict):
            artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise ValueError("DIAGNOSTIC_ARTIFACT_ID_INVALID")
        return artifact_id

    @staticmethod
    def _artifact_value(artifact: object, key: str) -> str | None:
        value = getattr(artifact, key, None)
        if value is None and isinstance(artifact, dict):
            value = artifact.get(key)
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _binding_identity(binding: ProductionReferenceBinding) -> str:
        readiness = binding.production_readiness
        value = readiness.get("binding_id") or readiness.get("run_id")
        if isinstance(value, str) and value:
            return value
        return binding.winner_reference_variant

    def _runtime_configuration(self):
        report = getattr(self.generate_provider, "last_report", {})
        if not isinstance(report, dict):
            return {}
        runtime = report.get("runtime")
        return runtime if isinstance(runtime, dict) else {}

    @staticmethod
    def _checksum(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _validate_wav(path: str | Path) -> dict[str, object]:
        try:
            with wave.open(str(path), "rb") as wav:
                channels = wav.getnchannels()
                sample_rate = wav.getframerate()
                sample_width = wav.getsampwidth()
                frames = wav.getnframes()
        except Exception as error:
            return {
                "ok": False,
                "code": "DIAGNOSTIC_WAV_PROBE_FAILED",
                "error": str(error),
            }

        return {
            "ok": (
                channels == 1
                and sample_rate == 32000
                and sample_width == 2
                and frames > 0
            ),
            "code": "DIAGNOSTIC_WAV_VALID"
            if (
                channels == 1
                and sample_rate == 32000
                and sample_width == 2
                and frames > 0
            )
            else "DIAGNOSTIC_WAV_FORMAT_INVALID",
            "channels": channels,
            "sample_rate": sample_rate,
            "sample_width": sample_width,
            "frames": frames,
        }

    @staticmethod
    def _write_evidence(path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )