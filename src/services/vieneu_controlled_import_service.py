from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from models.vieneu_controlled_import import (
    VieneuCanaryReport,
    VieneuCodecSelection,
    VieneuControlledDownloadPlan,
    VieneuModelSelection,
    VieneuReferenceValidation,
    VieneuResourceSafetyProfile,
    VieneuRuntimeManifest,
    VieneuSourceContract,
)
from services.audio_service import AudioService


class VieneuControlledImportService:

    CPU_FRONTEND_REQUIREMENT = (
        "cpu_torch_frontend_required_for_fresh_reference_enrollment"
    )

    CPU_FRONTEND_PERMISSION_BLOCKER = "cpu_torch_frontend_permission_required"

    GPU_RUNTIME_BLOCKER = "gpu_runtime_not_allowed_for_vieneu_cpu_canary"

    FORBIDDEN_GPU_PACKAGES = [
        "onnxruntime-gpu",
        "xformers",
        "flash-attention",
        "triton",
    ]

    CODEC_REPO_ID = "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"

    CODEC_REQUIRED_FILES = [
        "moss_audio_tokenizer_decode_full.onnx",
        "moss_audio_tokenizer_decode_shared.data",
        "moss_audio_tokenizer_decode_step.onnx",
        "codec_browser_onnx_meta.json",
        "moss_audio_tokenizer_encode.onnx",
        "moss_audio_tokenizer_encode.data",
    ]

    CANARY_TEXTS = [
        "Xin chào, đây là bài kiểm tra giọng nói.",
        "Đường tu tiên vốn nghịch thiên, chẳng ai biết trước được kết quả.",
        "Nguyễn Huệ tiến quân ra Thăng Long.",
    ]

    EVIDENCE_URLS = [
        "https://pypi.org/project/vieneu/",
        "https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo",
        "https://docs.vieneu.io/docs/",
        "https://docs.vieneu.io/docs/sdk/standard-mode/",
    ]

    def __init__(
        self,
        app_root=None,
        audio_service=None,
    ):

        self.app_root = Path(
            app_root or Path.cwd()
        ).resolve()

        self.audio_service = audio_service or AudioService()

    def default_selection(
        self,
    ):

        return VieneuModelSelection(
            evidence_urls=list(
                self.EVIDENCE_URLS
            )
        )

    def default_codec_selection(
        self,
    ):

        return VieneuCodecSelection(
            repo_id=self.CODEC_REPO_ID,
            required_files=list(
                self.CODEC_REQUIRED_FILES
            ),
        )

    def resource_safety_profile(
        self,
    ):

        return VieneuResourceSafetyProfile()

    def codec_cache_root(
        self,
        revision="75ff82a",
    ):

        return (
            self.app_root
            / "cache"
            / "engines"
            / "vieneu_tts"
            / revision
            / "codecs"
        )

    def verify_codec_completeness(
        self,
        codec_root,
        expected_files=None,
        expected_sizes=None,
    ):

        root = Path(
            codec_root
        )

        expected_files = expected_files or self.CODEC_REQUIRED_FILES
        expected_sizes = expected_sizes or {}

        missing = []
        empty = []
        size_mismatches = []

        for filename in expected_files:

            path = root / filename

            if not path.is_file():

                missing.append(
                    filename
                )
                continue

            size = path.stat().st_size

            if size <= 0:

                empty.append(
                    filename
                )

            expected = expected_sizes.get(
                filename
            )

            if expected is not None and size != int(
                expected
            ):

                size_mismatches.append(
                    {
                        "file": filename,
                        "expected": int(
                            expected
                        ),
                        "actual": size,
                    }
                )

        blockers = []

        if missing:

            blockers.append(
                "codec_required_file_missing"
            )

        if empty:

            blockers.append(
                "codec_empty_file"
            )

        if size_mismatches:

            blockers.append(
                "codec_size_mismatch"
            )

        return {
            "status": "READY"
            if not blockers
            else "BLOCKED",
            "blockers": blockers,
            "missing": missing,
            "empty": empty,
            "size_mismatches": size_mismatches,
            "root": str(
                root
            ),
        }

    def resource_preflight_decision(
        self,
        available_ram_gb,
        ai_process_running=False,
        runtime_process_running=False,
        process_tree_ram_gb=0.0,
    ):

        profile = self.resource_safety_profile()
        blockers = []
        warnings = []

        if available_ram_gb < profile.minimum_free_ram_before_start_gb:

            blockers.append(
                "available_ram_below_start_threshold"
            )

        if ai_process_running:

            blockers.append(
                "other_ai_process_running"
            )

        if runtime_process_running:

            blockers.append(
                "stale_vieneu_runtime_process_running"
            )

        if process_tree_ram_gb >= profile.hard_safety_process_tree_ram_limit_gb:

            blockers.append(
                "process_tree_ram_hard_limit_exceeded"
            )

        if available_ram_gb < profile.warning_free_ram_gb:

            warnings.append(
                "available_ram_below_warning_threshold"
            )

        return {
            "status": "PASS"
            if not blockers
            else "BLOCKED",
            "blockers": blockers,
            "warnings": warnings,
            "profile": profile.to_dict(),
        }

    def can_start_next_canary_phase(
        self,
        available_ram_gb,
    ):

        profile = self.resource_safety_profile()

        if available_ram_gb < profile.critical_free_ram_gb:

            return {
                "decision": "cancel_and_cleanup",
                "code": "available_ram_critical",
            }

        if available_ram_gb < profile.warning_free_ram_gb:

            return {
                "decision": "stop_at_safe_boundary",
                "code": "available_ram_low",
            }

        if available_ram_gb < profile.minimum_free_ram_before_start_gb:

            return {
                "decision": "do_not_start_next_phase",
                "code": "available_ram_below_next_phase_threshold",
            }

        return {
            "decision": "continue",
            "code": "resource_ok",
        }

    def source_contract(
        self,
    ):

        return VieneuSourceContract(
            evidence=[
                {
                    "file": "vieneu/factory.py",
                    "symbol": "Vieneu",
                    "finding": "mode='v3turbo' constructs V3TurboVieNeuTTS; CPU path is documented as ONNX Runtime.",
                },
                {
                    "file": "vieneu/v3turbo.py",
                    "symbol": "V3TurboVieNeuTTS.__init__",
                    "finding": "backend='onnx' forces OnnxV3LiteEngine on CPU; GPU is not required for this backend.",
                },
                {
                    "file": "vieneu/v3turbo.py",
                    "symbol": "V3TurboVieNeuTTS.infer",
                    "finding": "infer accepts ref_audio and resolves it before synthesis.",
                },
                {
                    "file": "vieneu/_v3_turbo_engine/onnx_runtime_lite.py",
                    "symbol": "OnnxV3LiteEngine.infer",
                    "finding": "CPU/ONNX infer accepts ref_audio and calls prepare_reference when ref_codes are missing.",
                },
                {
                    "file": "vieneu/_v3_turbo_engine/onnx_runtime_lite.py",
                    "symbol": "OnnxV3LiteEngine.prepare_reference",
                    "finding": "fresh reference enrollment uses _ensure_speaker_encoder().embed(...).",
                },
                {
                    "file": "vieneu/_v3_turbo_engine/speaker/onnx_extractor.py",
                    "symbol": "OnnxSpeakerEncoder",
                    "finding": "speaker fbank frontend imports torch at module load and uses torch.Tensor helpers.",
                },
                {
                    "file": "vieneu/_v3_turbo_engine/speaker/fbank.py",
                    "symbol": "extract_speaker_fbank",
                    "finding": "fbank module imports torch directly.",
                },
            ]
        )

    def build_plan(
        self,
        allow_download=False,
        allow_gpu_runtime=False,
        require_torch_free=False,
        allow_cpu_torch_frontend=False,
    ):

        selection = self.default_selection()
        contract = self.source_contract()

        target_root = (
            self.app_root
            / "cache"
            / "engines"
            / "vieneu_tts"
            / selection.model_revision
        )

        runtime_root = target_root / "runtime"
        model_cache_root = target_root / "models"
        diagnostics_root = (
            self.app_root
            / "diagnostics"
            / "vietnamese_engine_evaluation"
        )

        blockers = []
        warnings = []

        license_gate = "PASS"
        revision_gate = "PASS"
        model_gate = "PASS"
        runtime_gate = "PASS"
        low_resource_gate = "PASS"

        if selection.license.lower() != "apache-2.0":

            license_gate = "BLOCKED"
            blockers.append(
                "license_not_apache_2"
            )

        if not selection.model_revision:

            revision_gate = "BLOCKED"
            blockers.append(
                "model_revision_not_locked"
            )

        if selection.model_repo != "pnnbao-ump/VieNeu-TTS-v3-Turbo":

            model_gate = "BLOCKED"
            blockers.append(
                "unexpected_model_repo"
            )

        if not self.is_under_app_root(
            target_root
        ):

            runtime_gate = "BLOCKED"
            blockers.append(
                "target_root_outside_app_cache"
            )

        if not allow_download:

            blockers.append(
                "download_permission_not_enabled_for_service_call"
            )

        if require_torch_free and not contract.strict_torch_free_fresh_ref_audio_supported:

            low_resource_gate = "BLOCKED"
            blockers.append(
                self.CPU_FRONTEND_REQUIREMENT
            )
            warnings.append(
                "VieNeu 3.2.3 CPU/ONNX supports ref_audio, but fresh reference enrollment requires CPU torch/torchaudio frontend."
            )

        if contract.cpu_torch_frontend_required_for_fresh_reference_enrollment and not allow_cpu_torch_frontend:

            low_resource_gate = "BLOCKED"
            blockers.append(
                self.CPU_FRONTEND_PERMISSION_BLOCKER
            )
            warnings.append(
                "CPU-only torch/torchaudio must be explicitly allowed for fresh reference enrollment."
            )

        if allow_gpu_runtime:

            low_resource_gate = "BLOCKED"
            blockers.append(
                self.GPU_RUNTIME_BLOCKER
            )
            warnings.append(
                "AVS-014.22 canary is CPU-only. GPU runtime, CUDA wheels and CUDA fallback are not allowed."
            )

        python_path = (
            runtime_root
            / ".venv"
            / "Scripts"
            / "python.exe"
        )

        install_commands = [
            [
                sys.executable,
                "-m",
                "venv",
                str(
                    runtime_root / ".venv"
                ),
            ],
            [
                str(
                    python_path
                ),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
            ],
            [
                str(
                    python_path
                ),
                "-m",
                "pip",
                "install",
                "torch==2.8.0",
                "torchaudio==2.8.0",
                "--index-url",
                "https://download.pytorch.org/whl/cpu",
            ],
            [
                str(
                    python_path
                ),
                "-m",
                "pip",
                "install",
                f"{selection.package_name}=={selection.package_version}",
                "truststore==0.10.4",
            ],
        ]

        ready = not blockers

        return VieneuControlledDownloadPlan(
            plan_id=self.plan_id(
                selection
            ),
            selection=selection.to_dict(),
            target_root=str(
                target_root
            ),
            runtime_root=str(
                runtime_root
            ),
            model_cache_root=str(
                model_cache_root
            ),
            diagnostics_root=str(
                diagnostics_root
            ),
            allowed_roots=[
                str(
                    self.app_root / "cache"
                ),
                str(
                    self.app_root / "diagnostics"
                ),
            ],
            license_gate=license_gate,
            revision_gate=revision_gate,
            model_gate=model_gate,
            runtime_gate=runtime_gate,
            low_resource_gate=low_resource_gate,
            ready_to_download=ready,
            ready_to_import=ready,
            ready_for_canary=ready,
            blockers=blockers,
            warnings=warnings,
            install_commands=install_commands,
            canary_texts=list(
                self.CANARY_TEXTS
            ),
        )

    def cpu_runtime_environment(
        self,
    ):

        env = dict(
            os.environ
        )

        env[
            "CUDA_VISIBLE_DEVICES"
        ] = ""

        env[
            "VIE_NEU_CPU_ONLY"
        ] = "1"

        return env

    def verify_cpu_only_runtime_payload(
        self,
        payload,
    ):

        blockers = []
        warnings = []

        if payload.get(
            "torch_cuda_available"
        ):

            blockers.append(
                "torch_cuda_available"
            )

        providers = payload.get(
            "onnx_providers",
            [],
        ) or []

        if "CUDAExecutionProvider" in providers:

            blockers.append(
                "onnx_cuda_provider_available"
            )

        installed = {
            str(
                name
            ).lower()
            for name in payload.get(
                "installed_packages",
                []
            )
        }

        forbidden = [
            name
            for name in self.FORBIDDEN_GPU_PACKAGES
            if name.lower() in installed
        ]

        if forbidden:

            blockers.append(
                "forbidden_gpu_package_installed"
            )
            warnings.append(
                "Forbidden GPU packages installed: "
                + ", ".join(
                    forbidden
                )
            )

        return {
            "status": "READY"
            if not blockers
            else "BLOCKED",
            "blockers": blockers,
            "warnings": warnings,
            "cpu_only": not blockers,
        }

    def runtime_fingerprint(
        self,
        payload,
    ):

        normalized = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        )

        return hashlib.sha256(
            normalized.encode(
                "utf-8"
            )
        ).hexdigest()

    def build_runtime_manifest(
        self,
        plan,
        runtime_payload,
        package_hashes=None,
    ):

        plan = (
            plan
            if isinstance(
                plan,
                VieneuControlledDownloadPlan,
            )
            else VieneuControlledDownloadPlan(
                **plan
            )
        )

        verification = self.verify_cpu_only_runtime_payload(
            runtime_payload
        )

        manifest_payload = {
            "engine_id": plan.selection.get(
                "engine_id",
                "vieneu_tts",
            ),
            "package_version": plan.selection.get(
                "package_version",
                "",
            ),
            "python_version": runtime_payload.get(
                "python_version",
                "",
            ),
            "model_revision": plan.selection.get(
                "model_revision",
                "",
            ),
            "onnxruntime_version": runtime_payload.get(
                "onnxruntime_version"
            ),
            "torch_version": runtime_payload.get(
                "torch_version"
            ),
            "torchaudio_version": runtime_payload.get(
                "torchaudio_version"
            ),
            "cpu_only": verification[
                "cpu_only"
            ],
            "cuda_expected": False,
            "cuda_available": bool(
                runtime_payload.get(
                    "torch_cuda_available"
                )
            ),
            "onnx_providers": runtime_payload.get(
                "onnx_providers",
                [],
            ),
            "install_commands": plan.install_commands,
            "package_hashes": package_hashes or {},
            "created_at": datetime.now().isoformat(),
            "status": verification[
                "status"
            ],
            "blockers": verification[
                "blockers"
            ],
            "warnings": verification[
                "warnings"
            ],
        }

        manifest_payload[
            "fingerprint"
        ] = self.runtime_fingerprint(
            manifest_payload
        )

        return VieneuRuntimeManifest(
            **manifest_payload
        )

    def experimental_adapter_capabilities(
        self,
    ):

        return {
            "scope": "EXPERIMENTAL_CANARY_ONLY",
            "doctor": True,
            "install_or_import": True,
            "validate_model": True,
            "prepare_reference": True,
            "enroll_reference_cpu": True,
            "generate_canary_cpu": True,
            "unload": True,
            "cancel": True,
            "capabilities": True,
            "runtime_fingerprint": True,
            "model_fingerprint": True,
            "production_provider_registered": False,
        }

    def validate_reference(
        self,
        audio_path,
        reference_text,
        language="vi",
        target_sample_rate=48000,
    ):

        result = VieneuReferenceValidation(
            audio_path=str(
                audio_path or ""
            ),
            text=str(
                reference_text or ""
            ),
            language=language,
        )

        if not str(
            audio_path or ""
        ).strip():

            result.blockers.append(
                "reference_audio_missing"
            )

            return result

        path = Path(
            audio_path
        )

        if not path.exists():

            result.blockers.append(
                "reference_audio_not_found"
            )

            return result

        if not str(
            reference_text or ""
        ).strip():

            result.blockers.append(
                "reference_text_missing"
            )

        try:

            info = self.audio_service.probe(
                path
            )

        except Exception as exc:

            result.blockers.append(
                "reference_audio_probe_failed"
            )
            result.warnings.append(
                str(
                    exc
                )
            )

            return result

        result.duration = float(
            info.get(
                "duration",
                0.0,
            )
        )
        result.sample_rate = int(
            info.get(
                "sample_rate",
                0,
            )
        )
        result.channels = int(
            info.get(
                "channels",
                0,
            )
        )
        result.codec = str(
            info.get(
                "codec",
                "",
            )
        )

        if result.duration < 3.0 or result.duration > 8.0:

            result.blockers.append(
                "reference_duration_out_of_range"
            )

        if result.channels != 1:

            result.blockers.append(
                "reference_not_mono"
            )

        if result.codec != "pcm_s16le":

            result.blockers.append(
                "reference_codec_not_pcm_s16le"
            )

        if result.sample_rate != target_sample_rate:

            result.requires_resample_copy = True
            result.warnings.append(
                "reference_requires_diagnostics_resample_copy"
            )

        result.status = (
            "valid"
            if not result.blockers
            else "blocked"
        )

        return result

    def prepare_canary_report(
        self,
        plan,
        reference,
        run_id=None,
    ):

        plan = (
            plan
            if isinstance(
                plan,
                VieneuControlledDownloadPlan,
            )
            else VieneuControlledDownloadPlan(
                **plan
            )
        )

        reference = (
            reference
            if isinstance(
                reference,
                VieneuReferenceValidation,
            )
            else VieneuReferenceValidation(
                **reference
            )
        )

        run_id = run_id or self.run_id()

        output_root = (
            Path(
                plan.diagnostics_root
            )
            / run_id
        )

        blockers = []

        if not plan.ready_for_canary:

            blockers.extend(
                plan.blockers
            )

        if reference.status != "valid":

            blockers.extend(
                reference.blockers
            )

        python_path = (
            Path(
                plan.runtime_root
            )
            / ".venv"
            / "Scripts"
            / "python.exe"
        )

        command = [
            str(
                python_path
            ),
            "-m",
            "vieneu_controlled_canary",
            "--model-repo",
            plan.selection.get(
                "model_repo",
                "",
            ),
            "--revision",
            plan.selection.get(
                "model_revision",
                "",
            ),
            "--ref-audio",
            reference.audio_path,
            "--language",
            reference.language,
            "--output-root",
            str(
                output_root
            ),
        ]

        return VieneuCanaryReport(
            run_id=run_id,
            status="BLOCKED"
            if blockers
            else "READY_TO_RUN",
            output_root=str(
                output_root
            ),
            selected_model=plan.selection,
            reference=reference.to_dict(),
            command=command,
            blockers=blockers,
            warnings=list(
                plan.warnings
            )
            + list(
                reference.warnings
            ),
            readiness_effect={
                "vietnamese_engine_production_integration": "BLOCKED",
                "generate_execution": "BLOCKED",
                "wav_output": "BLOCKED",
            },
        )

    def write_report(
        self,
        report,
    ):

        data = (
            report.to_dict()
            if hasattr(
                report,
                "to_dict",
            )
            else dict(
                report
            )
        )

        output_root = Path(
            data[
                "output_root"
            ]
        )

        if not self.is_under_allowed_output(
            output_root
        ):

            raise ValueError(
                "diagnostics_output_outside_allowed_root"
            )

        output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = output_root / "vieneu_canary_report.json"

        temp = path.with_suffix(
            ".json.tmp"
        )

        temp.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        os.replace(
            temp,
            path,
        )

        return path

    def validate_wav_output(
        self,
        wav_path,
    ):

        path = Path(
            wav_path
        )

        if not path.exists():

            return {
                "ok": False,
                "code": "wav_missing",
                "path": str(
                    path
                ),
            }

        if path.stat().st_size <= 44:

            return {
                "ok": False,
                "code": "wav_header_only",
                "path": str(
                    path
                ),
                "size": path.stat().st_size,
            }

        try:

            info = self.audio_service.probe(
                path
            )

        except Exception as exc:

            return {
                "ok": False,
                "code": "wav_probe_failed",
                "path": str(
                    path
                ),
                "error": str(
                    exc
                ),
            }

        ok = float(
            info.get(
                "duration",
                0.0,
            )
        ) > 0.0 and int(
            info.get(
                "channels",
                0,
            )
        ) >= 1

        return {
            "ok": ok,
            "code": "wav_valid"
            if ok
            else "wav_invalid",
            "path": str(
                path
            ),
            "metadata": info,
        }

    def run_command(
        self,
        command,
        cwd,
        timeout_seconds=120,
    ):

        started = datetime.now()

        try:

            result = subprocess.run(
                command,
                cwd=str(
                    cwd
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
            )

        except subprocess.TimeoutExpired as exc:

            return {
                "ok": False,
                "code": "timeout",
                "exit_code": None,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "elapsed_seconds": (
                    datetime.now() - started
                ).total_seconds(),
            }

        stderr = result.stderr or ""

        code = "ok"

        if result.returncode != 0:

            code = "process_failed"

        if "out of memory" in stderr.lower() or "cuda" in stderr.lower() and "memory" in stderr.lower():

            code = "cuda_out_of_memory"

        return {
            "ok": result.returncode == 0,
            "code": code,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": stderr,
            "elapsed_seconds": (
                datetime.now() - started
            ).total_seconds(),
        }

    def plan_id(
        self,
        selection,
    ):

        payload = json.dumps(
            selection.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
        )

        return "vieneu_plan_" + hashlib.sha256(
            payload.encode(
                "utf-8"
            )
        ).hexdigest()[
            :12
        ]

    def run_id(
        self,
    ):

        return "vieneu_canary_" + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

    def is_under_app_root(
        self,
        path,
    ):

        try:

            Path(
                path
            ).resolve().relative_to(
                self.app_root
            )
            return True

        except Exception:

            return False

    def is_under_allowed_output(
        self,
        path,
    ):

        resolved = Path(
            path
        ).resolve()

        allowed = [
            self.app_root / "diagnostics",
            self.app_root / "cache",
        ]

        for root in allowed:

            try:

                resolved.relative_to(
                    root.resolve()
                )
                return True

            except Exception:

                continue

        return False

    def command_available(
        self,
        executable,
    ):

        return shutil.which(
            executable
        ) or ""
