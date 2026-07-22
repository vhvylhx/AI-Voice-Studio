import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from models.job_model import JobModel
from models.preprocessing_run import (
    PREPROCESSING_SCHEMA_VERSION,
    PreprocessingPlan,
    PreprocessingRun,
    PreprocessingStage,
    now_iso,
)
from models.resource_model import ResourceRequirement
from services.audio_service import AudioService
from services.runtime_profile_service import RuntimeProfileService


class TrainingPreprocessingService:

    REQUIRED_ARTIFACTS = {
        "name2text": "2-name2text.txt",
        "bert": "3-bert",
        "cnhubert": "4-cnhubert",
        "semantic": "6-name2semantic.tsv",
    }

    OPTIONAL_ARTIFACTS = {
        "wav32k": "5-wav32k",
        "speaker_vector": "7-sv_cn",
    }

    def __init__(
        self,
        app_root=None,
        runtime_profiles=None,
        audio_service=None,
        lease_manager=None,
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

        self.audio = audio_service or AudioService()

        self.lease_manager = lease_manager

        self.progress_events = []

    def create_run_id(
        self,
        voice_id,
        timestamp=None,
    ):

        stamp = timestamp or time.strftime(
            "%Y%m%d_%H%M%S"
        )

        safe_voice_id = re.sub(
            r"[^0-9A-Za-z_-]+",
            "_",
            str(
                voice_id
            ),
        ).strip(
            "_"
        )

        return f"avs01419a_voice_{safe_voice_id}_{stamp}"

    def create_run(
        self,
        voice,
        metadata_path,
        runtime_profile=None,
        preprocessing_run_id="",
        output_root=None,
    ):

        voice_id = getattr(
            voice,
            "id",
            "",
        )

        run_id = preprocessing_run_id or self.create_run_id(
            voice_id
        )

        root = Path(
            output_root
            or self.app_root
            / "cache"
            / "training_preprocessing"
            / run_id
        ).resolve()

        run = PreprocessingRun(
            preprocessing_run_id=run_id,
            voice_id=voice_id,
            display_name_snapshot=getattr(
                voice,
                "display_name",
                getattr(
                    voice,
                    "name",
                    "",
                ),
            ),
            input_metadata_path=str(
                metadata_path
            ),
            output_root=str(
                root
            ),
            manifest_path=str(
                root
                / "preprocessing_manifest.json"
            ),
            log_root=str(
                root
                / "logs"
            ),
        )

        return run

    def build_plan(
        self,
        voice,
        metadata_path,
        runtime_profile=None,
        preprocessing_run_id="",
        output_root=None,
        language="vi",
        sample_rate=32000,
    ):

        run = self.create_run(
            voice=voice,
            metadata_path=metadata_path,
            runtime_profile=runtime_profile,
            preprocessing_run_id=preprocessing_run_id,
            output_root=output_root,
        )

        output = Path(
            run.output_root
        )

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        (output / "logs").mkdir(
            parents=True,
            exist_ok=True,
        )

        dataset = self.validate_dataset(
            metadata_path,
            language=language,
            sample_rate=sample_rate,
        )

        profile = self.select_runtime_profile(
            runtime_profile
        )

        runtime = self.validate_runtime(
            profile,
            language=language,
        )

        normalized_metadata = (
            output
            / "input"
            / "metadata.normalized.list"
        )

        if dataset["ok"]:

            self.write_normalized_metadata(
                dataset["items"],
                normalized_metadata,
            )

        stages = self.build_stages(
            run,
            runtime,
            normalized_metadata,
            language=language,
        )

        plan = PreprocessingPlan(
            preprocessing_run_id=run.preprocessing_run_id,
            voice_id=run.voice_id,
            display_name_snapshot=run.display_name_snapshot,
            metadata_path=str(
                metadata_path
            ),
            metadata_sha256=dataset.get(
                "sha256",
                "",
            ),
            clip_count=dataset.get(
                "clip_count",
                0,
            ),
            total_duration=dataset.get(
                "total_duration",
                0.0,
            ),
            language=language,
            sample_rate=sample_rate,
            runtime_profile_id=runtime.get(
                "profile_id",
                "",
            ),
            runtime_fingerprint=runtime.get(
                "fingerprint",
                "",
            ),
            runtime_root=runtime.get(
                "runtime_root",
                "",
            ),
            python_path=runtime.get(
                "python_path",
                "",
            ),
            output_root=str(
                output
            ),
            normalized_metadata_path=str(
                normalized_metadata
            ),
            stages=stages,
        )

        plan.plan_fingerprint = self.fingerprint_json(
            {
                "metadata_sha256": plan.metadata_sha256,
                "runtime_fingerprint": plan.runtime_fingerprint,
                "voice_id": plan.voice_id,
                "language": plan.language,
                "sample_rate": plan.sample_rate,
                "stages": [
                    stage.to_dict()
                    for stage in plan.stages
                ],
            }
        )

        blockers = []

        if not dataset["ok"]:

            blockers.extend(
                dataset["errors"]
            )

        if not runtime["ok"]:

            blockers.extend(
                runtime["errors"]
            )

        run.dataset_fingerprint = plan.metadata_sha256
        run.runtime_profile_id = plan.runtime_profile_id
        run.runtime_fingerprint = plan.runtime_fingerprint
        run.stages = plan.stages
        run.blockers = blockers
        run.warnings = dataset.get(
            "warnings",
            [],
        ) + runtime.get(
            "warnings",
            [],
        )
        run.status = (
            "blocked"
            if blockers
            else "planned"
        )

        self.write_json_atomic(
            output / "preprocessing_plan.json",
            plan.to_dict(),
        )

        self.write_manifest(
            run,
            plan,
            dataset,
            runtime,
        )

        return {
            "ok": not blockers,
            "run": run.to_dict(),
            "plan": plan.to_dict(),
            "dataset": dataset,
            "runtime": runtime,
            "blockers": blockers,
            "warnings": run.warnings,
        }

    def run(
        self,
        voice,
        metadata_path,
        runtime_profile=None,
        preprocessing_run_id="",
        output_root=None,
        language="vi",
        sample_rate=32000,
        progress_callback=None,
        timeout_seconds=3600,
    ):

        started = time.time()
        self.progress_events = []

        planned = self.build_plan(
            voice=voice,
            metadata_path=metadata_path,
            runtime_profile=runtime_profile,
            preprocessing_run_id=preprocessing_run_id,
            output_root=output_root,
            language=language,
            sample_rate=sample_rate,
        )

        run = PreprocessingRun.from_dict(
            planned["run"]
        )

        plan = PreprocessingPlan.from_dict(
            planned["plan"]
        )

        dataset = planned["dataset"]
        runtime = planned["runtime"]

        if not planned["ok"]:

            run.status = "blocked"

            self.write_manifest(
                run,
                plan,
                dataset,
                runtime,
            )

            return {
                **planned,
                "status": "blocked",
                "progress": self.progress_events,
            }

        run.status = "running"
        run.started_at = now_iso()

        for index, stage in enumerate(
            plan.stages,
            start=1,
        ):

            self.emit_progress(
                stage.stage_id,
                index,
                len(
                    plan.stages
                ),
                started,
                f"Dang chay {stage.display_name}.",
                "info",
                progress_callback,
            )

            result = self.run_stage(
                stage,
                plan,
                timeout_seconds=timeout_seconds,
            )

            stage = PreprocessingStage.from_dict(
                result
            )

            run.stages[
                index - 1
            ] = stage

            self.write_manifest(
                run,
                plan,
                dataset,
                runtime,
            )

            if stage.status != "success":

                run.status = "failed"
                run.completed_at = now_iso()
                run.blockers.append(
                    {
                        "code": stage.error_code
                        or "PREPROCESS_PROCESS_FAILED",
                        "reason": stage.message,
                        "stage": stage.stage_id,
                    }
                )

                self.write_manifest(
                    run,
                    plan,
                    dataset,
                    runtime,
                )

                return {
                    "ok": False,
                    "status": run.status,
                    "run": run.to_dict(),
                    "plan": plan.to_dict(),
                    "dataset": dataset,
                    "runtime": runtime,
                    "progress": self.progress_events,
                }

        artifact_validation = self.validate_artifacts(
            plan
        )

        run.training_ready = artifact_validation.get(
            "training_ready",
            False,
        )

        run.status = (
            "success"
            if run.training_ready
            else "failed"
        )

        run.completed_at = now_iso()

        if not run.training_ready:

            run.blockers.extend(
                artifact_validation.get(
                    "errors",
                    [],
                )
            )

        self.write_manifest(
            run,
            plan,
            dataset,
            runtime,
            artifact_validation=artifact_validation,
        )

        self.emit_progress(
            "done",
            len(
                plan.stages
            ),
            len(
                plan.stages
            ),
            started,
            "Hoan tat preprocessing." if run.training_ready else "Preprocessing chua san sang.",
            "success" if run.training_ready else "error",
            progress_callback,
        )

        return {
            "ok": run.training_ready,
            "status": run.status,
            "run": run.to_dict(),
            "plan": plan.to_dict(),
            "dataset": dataset,
            "runtime": runtime,
            "artifact_validation": artifact_validation,
            "progress": self.progress_events,
        }

    def run_stage(
        self,
        stage,
        plan,
        timeout_seconds=3600,
    ):

        stage = PreprocessingStage.from_dict(
            stage
        )

        stage.started_at = now_iso()
        started = time.time()

        output_root = Path(
            plan.output_root
        )

        logs = (
            output_root
            / "logs"
        )

        logs.mkdir(
            parents=True,
            exist_ok=True,
        )

        stdout_log = logs / f"{stage.stage_id}_stdout.log"
        stderr_log = logs / f"{stage.stage_id}_stderr.log"

        if self.stage_can_reuse(
            stage,
            plan,
        ):

            stage.status = "success"
            stage.message = "reuse_valid_artifact"
            stage.completed_at = now_iso()
            stage.elapsed_seconds = time.time() - started
            stage.artifact_validation = self.validate_stage_artifacts(
                stage,
                plan,
            )

            return self.finish_stage(
                stage,
                started,
            )

        lease = None

        try:

            if stage.requires_gpu and self.lease_manager is not None:

                lease, reason = self.acquire_gpu_lease(
                    stage,
                    plan,
                )

                if lease is None:

                    stage.status = "failed"
                    stage.error_code = "PREPROCESS_CUDA_UNAVAILABLE"
                    stage.message = reason or "gpu_lease_unavailable"

                    return self.finish_stage(
                        stage,
                        started,
                    )

            env = os.environ.copy()
            env.update(
                stage.env
            )
            env.setdefault(
                "PYTHONUTF8",
                "1",
            )
            env.setdefault(
                "PYTHONIOENCODING",
                "utf-8",
            )

            process = subprocess.run(
                stage.command,
                cwd=plan.runtime_root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                shell=False,
            )

            stdout_log.write_text(
                process.stdout or "",
                encoding="utf-8",
            )

            stderr_log.write_text(
                process.stderr or "",
                encoding="utf-8",
            )

            stage.stdout_log = str(
                stdout_log
            )
            stage.stderr_log = str(
                stderr_log
            )
            stage.exit_code = process.returncode

            if process.returncode != 0:

                stage.status = "failed"
                stage.error_code = (
                    "PREPROCESS_CUDA_OOM"
                    if self.is_cuda_oom(
                        process.stderr
                        + process.stdout
                    )
                    else "PREPROCESS_PROCESS_FAILED"
                )
                stage.message = (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "preprocess_process_failed"
                )

                return self.finish_stage(
                    stage,
                    started,
                )

            self.combine_stage_output(
                stage,
                plan,
            )

            validation = self.validate_stage_artifacts(
                stage,
                plan,
            )

            stage.artifact_validation = validation

            if not validation.get(
                "ok",
                False,
            ):

                stage.status = "failed"
                stage.error_code = "PREPROCESS_OUTPUT_INVALID"
                stage.message = "; ".join(
                    error.get(
                        "reason",
                        ""
                    )
                    for error in validation.get(
                        "errors",
                        [],
                    )
                )

                return self.finish_stage(
                    stage,
                    started,
                )

            stage.status = "success"
            stage.message = "stage_success"

            return self.finish_stage(
                stage,
                started,
            )

        except subprocess.TimeoutExpired:

            stage.status = "failed"
            stage.error_code = "PREPROCESS_TIMEOUT"
            stage.message = "preprocess_timeout"

            return self.finish_stage(
                stage,
                started,
            )

        except PermissionError as e:

            stage.status = "failed"
            stage.error_code = "PREPROCESS_PERMISSION_DENIED"
            stage.message = str(
                e
            )

            return self.finish_stage(
                stage,
                started,
            )

        except Exception as e:

            stage.status = "failed"
            stage.error_code = "PREPROCESS_UNKNOWN_ERROR"
            stage.message = str(
                e
            )

            return self.finish_stage(
                stage,
                started,
            )

        finally:

            if lease is not None and self.lease_manager is not None:

                self.lease_manager.release(
                    lease.lease_id
                )

    def finish_stage(
        self,
        stage,
        started,
    ):

        stage.completed_at = now_iso()
        stage.elapsed_seconds = time.time() - started

        return stage.to_dict()

    def select_runtime_profile(
        self,
        runtime_profile=None,
    ):

        if runtime_profile is not None:

            from models.runtime_profile import RuntimeProfile

            return RuntimeProfile.from_dict(
                runtime_profile
            )

        profiles = self.runtime_profiles.list_profiles()

        for profile in profiles:

            if profile.is_default:

                return profile

        return profiles[0] if profiles else None

    def validate_runtime(
        self,
        profile,
        language="vi",
    ):

        errors = []
        warnings = []

        if profile is None:

            return {
                "ok": False,
                "profile_id": "",
                "errors": [
                    self.issue(
                        "PREPROCESS_RUNTIME_MISSING",
                        "Chua co Runtime Profile mac dinh.",
                    )
                ],
                "warnings": [],
            }

        validation = self.runtime_profiles.validate(
            profile,
            smoke_test=False,
        )

        runtime_root = self.runtime_profiles.resolve_path(
            profile.runtime_path
        )

        python_path = self.runtime_profiles.resolve_path(
            profile.python_path
        )

        scripts = self.discover_scripts(
            runtime_root
        )

        pretrained = self.discover_pretrained(
            runtime_root
        )

        for cause in validation.get(
            "causes",
            [],
        ):

            errors.append(
                self.issue(
                    "PREPROCESS_RUNTIME_MISSING",
                    cause.get(
                        "message",
                        "Runtime Profile chua san sang.",
                    ),
                    detected_path=validation.get(
                        "detected_path",
                        {},
                    ),
                )
            )

        for key, info in scripts.items():

            if key in {
                "prepare_sv",
            }:

                continue

            if not info.get(
                "exists",
                False,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_SCRIPT_MISSING",
                        f"Thieu script preprocessing: {key}.",
                        detected_path=info.get(
                            "path",
                            "",
                        ),
                    )
                )

        for key, info in pretrained.items():

            if not info.get(
                "exists",
                False,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_RUNTIME_MISSING",
                        f"Thieu pretrained dependency: {key}.",
                        detected_path=info.get(
                            "path",
                            "",
                        ),
                    )
                )

        supported = self.detect_supported_languages(
            scripts.get(
                "prepare_text",
                {},
            ).get(
                "path",
                "",
            ),
            runtime_root,
        )

        if language not in supported:

            errors.append(
                self.issue(
                    "PREPROCESS_CONFIG_INVALID",
                    (
                        f"Runtime preprocessing hien tai khong ho tro language '{language}'. "
                        f"Supported: {', '.join(sorted(supported)) or 'unknown'}."
                    ),
                    detected_path=scripts.get(
                        "prepare_text",
                        {},
                    ).get(
                        "path",
                        "",
                    ),
                    suggestion=(
                        "Can GPT-SoVITS runtime/script co cleaner ngon ngu Viet hoac "
                        "mot mapping upstream hop le truoc khi preprocess metadata language vi."
                    ),
                )
            )

        fingerprint = self.fingerprint_json(
            {
                "profile": profile.to_dict(),
                "scripts": self.file_fingerprints(
                    [
                        item.get(
                            "path",
                            "",
                        )
                        for item in scripts.values()
                    ]
                ),
                "pretrained": self.file_fingerprints(
                    [
                        item.get(
                            "path",
                            "",
                        )
                        for item in pretrained.values()
                    ]
                ),
                "supported_languages": sorted(
                    supported
                ),
            }
        )

        return {
            "ok": not errors,
            "profile_id": profile.profile_id,
            "runtime_root": str(
                runtime_root
            ),
            "python_path": str(
                python_path
            ),
            "validation": validation,
            "scripts": scripts,
            "pretrained": pretrained,
            "supported_languages": sorted(
                supported
            ),
            "fingerprint": fingerprint,
            "errors": errors,
            "warnings": warnings,
        }

    def discover_scripts(
        self,
        runtime_root,
    ):

        root = Path(
            runtime_root
        )

        paths = self.runtime_profiles.gpt_sovits_scripts(
            root
        )

        paths["prepare_sv"] = {
            "path": str(
                root
                / "GPT_SoVITS"
                / "prepare_datasets"
                / "2-get-sv.py"
            ),
            "exists": (
                root
                / "GPT_SoVITS"
                / "prepare_datasets"
                / "2-get-sv.py"
            ).exists(),
        }

        return {
            key: value
            for key, value in paths.items()
            if key
            in {
                "prepare_text",
                "prepare_hubert",
                "prepare_semantic",
                "prepare_sv",
            }
        }

    def discover_pretrained(
        self,
        runtime_root,
    ):

        root = Path(
            runtime_root
        )

        models = self.runtime_profiles.detect_pretrained_models(
            root
        )

        models["speaker_vector"] = {
            "path": str(
                root
                / "GPT_SoVITS"
                / "pretrained_models"
                / "sv"
                / "pretrained_eres2netv2w24s4ep4.ckpt"
            ),
            "exists": (
                root
                / "GPT_SoVITS"
                / "pretrained_models"
                / "sv"
                / "pretrained_eres2netv2w24s4ep4.ckpt"
            ).exists(),
        }

        return {
            key: value
            for key, value in models.items()
            if key
            in {
                "gpt",
                "sovits_g",
                "sovits_d",
                "bert",
                "hubert",
                "speaker_vector",
            }
        }

    def detect_supported_languages(
        self,
        prepare_text_script,
        runtime_root,
    ):

        supported = set()

        script = Path(
            prepare_text_script
        )

        if script.exists():

            text = script.read_text(
                encoding="utf-8",
                errors="replace",
            )

            match = re.search(
                r"language_v1_to_language_v2\s*=\s*\{(?P<body>.*?)\}",
                text,
                re.S,
            )

            if match:

                supported.update(
                    re.findall(
                        r"[\"']([^\"']+)[\"']\s*:",
                        match.group(
                            "body"
                        ),
                    )
                )

        cleaner = (
            Path(
                runtime_root
            )
            / "GPT_SoVITS"
            / "text"
            / "cleaner.py"
        )

        if cleaner.exists():

            text = cleaner.read_text(
                encoding="utf-8",
                errors="replace",
            )

            for match in re.finditer(
                r"language_module_map\s*=\s*\{(?P<body>.*?)\}",
                text,
                re.S,
            ):

                supported.update(
                    re.findall(
                        r"[\"']([^\"']+)[\"']\s*:",
                        match.group(
                            "body"
                        ),
                    )
                )

        return {
            item.lower()
            for item in supported
        }

    def validate_dataset(
        self,
        metadata_path,
        language="vi",
        sample_rate=32000,
    ):

        errors = []
        warnings = []
        items = []
        seen = set()
        total_duration = 0.0

        file = Path(
            metadata_path
        )

        if not file.exists():

            return {
                "ok": False,
                "path": str(
                    file
                ),
                "sha256": "",
                "clip_count": 0,
                "total_duration": 0.0,
                "items": [],
                "errors": [
                    self.issue(
                        "PREPROCESS_METADATA_INVALID",
                        "Khong tim thay metadata.list.",
                        detected_path=str(
                            file
                        ),
                    )
                ],
                "warnings": [],
            }

        if not self.is_allowed_path(
            file,
        ):

            errors.append(
                self.issue(
                    "PREPROCESS_METADATA_INVALID",
                    "metadata.list nam ngoai allowed root cua app.",
                    detected_path=str(
                        file
                    ),
                )
            )

        lines = [
            line.strip()
            for line in file.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        if not lines:

            errors.append(
                self.issue(
                    "PREPROCESS_METADATA_INVALID",
                    "metadata.list rong.",
                    detected_path=str(
                        file
                    ),
                )
            )

        for line_number, line in enumerate(
            lines,
            start=1,
        ):

            parts = line.split(
                "|",
                3,
            )

            if len(
                parts
            ) != 4:

                errors.append(
                    self.issue(
                        "PREPROCESS_METADATA_INVALID",
                        "Dong metadata khong dung audio|speaker|language|text.",
                        detected_path=f"line {line_number}",
                    )
                )

                continue

            audio_path, speaker, item_language, text = parts
            audio = Path(
                audio_path
            )

            if not audio.is_absolute():

                audio = (
                    self.app_root
                    / audio
                )

            audio = audio.resolve()

            key = str(
                audio
            ).lower()

            if key in seen:

                errors.append(
                    self.issue(
                        "PREPROCESS_METADATA_INVALID",
                        "metadata.list co duplicate audio path.",
                        detected_path=str(
                            audio
                        ),
                    )
                )

                continue

            seen.add(
                key
            )

            if not self.is_allowed_path(
                audio,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_DATASET_INVALID",
                        "Audio nam ngoai allowed root cua app.",
                        detected_path=str(
                            audio
                        ),
                    )
                )

                continue

            if re.search(
                r"t[e3]s[t7]|tes|tset",
                audio.name,
                re.I,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_DATASET_INVALID",
                        "Metadata chua file test/version.",
                        detected_path=str(
                            audio
                        ),
                    )
                )

            if item_language != language:

                errors.append(
                    self.issue(
                        "PREPROCESS_METADATA_INVALID",
                        f"Language metadata khong phai {language}.",
                        detected_path=f"line {line_number}",
                        current_version=item_language,
                        required_version=language,
                    )
                )

            if not text.strip():

                errors.append(
                    self.issue(
                        "PREPROCESS_METADATA_INVALID",
                        "Transcript rong.",
                        detected_path=f"line {line_number}",
                    )
                )

            if not audio.exists():

                errors.append(
                    self.issue(
                        "PREPROCESS_DATASET_INVALID",
                        "Khong tim thay WAV.",
                        detected_path=str(
                            audio
                        ),
                    )
                )

                continue

            try:

                info = self.audio.probe(
                    audio
                )

            except Exception as e:

                errors.append(
                    self.issue(
                        "PREPROCESS_DATASET_INVALID",
                        f"ffprobe khong doc duoc WAV: {e}",
                        detected_path=str(
                            audio
                        ),
                    )
                )

                continue

            if (
                info.get(
                    "channels"
                )
                != 1
                or info.get(
                    "codec"
                )
                != "pcm_s16le"
                or info.get(
                    "sample_rate"
                )
                != sample_rate
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_DATASET_INVALID",
                        "WAV khong dung mono/pcm_s16le/sample_rate.",
                        detected_path=str(
                            audio
                        ),
                        current_version=(
                            f"{info.get('channels')}ch/"
                            f"{info.get('codec')}/"
                            f"{info.get('sample_rate')}Hz"
                        ),
                        required_version=f"mono/pcm_s16le/{sample_rate}Hz",
                    )
                )

            item = {
                "line": line_number,
                "audio": str(
                    audio
                ),
                "speaker": speaker,
                "language": item_language,
                "text": text,
                "duration": info.get(
                    "duration",
                    0.0,
                ),
            }

            items.append(
                item
            )

            total_duration += float(
                item["duration"]
            )

        return {
            "ok": not errors,
            "path": str(
                file
            ),
            "sha256": self.sha256_file(
                file
            ),
            "clip_count": len(
                items
            ),
            "total_duration": total_duration,
            "items": items,
            "errors": errors,
            "warnings": warnings,
        }

    def write_normalized_metadata(
        self,
        items,
        output_file,
    ):

        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        lines = [
            "|".join(
                [
                    item["audio"],
                    item["speaker"],
                    item["language"],
                    item["text"].replace(
                        "\n",
                        " ",
                    ),
                ]
            )
            for item in items
        ]

        self.write_text_atomic(
            output_file,
            "\n".join(
                lines
            )
            + "\n",
        )

    def build_stages(
        self,
        run,
        runtime,
        normalized_metadata,
        language="vi",
    ):

        output = Path(
            run.output_root
        )

        scripts = runtime.get(
            "scripts",
            {},
        )

        pretrained = runtime.get(
            "pretrained",
            {},
        )

        common_env = {
            "inp_text": str(
                normalized_metadata
            ),
            "inp_wav_dir": "",
            "exp_name": run.preprocessing_run_id,
            "opt_dir": str(
                output
            ),
            "i_part": "0",
            "all_parts": "1",
            "_CUDA_VISIBLE_DEVICES": "0",
            "is_half": "True",
            "version": "v2Pro",
        }

        def command(
            script_key,
        ):

            return [
                runtime["python_path"],
                "-s",
                scripts[script_key]["path"],
            ]

        return [
            PreprocessingStage(
                stage_id="text_phoneme",
                display_name="Text/phoneme va BERT feature",
                script_key="prepare_text",
                command=command(
                    "prepare_text"
                ),
                env={
                    **common_env,
                    "bert_pretrained_dir": pretrained[
                        "bert"
                    ][
                        "path"
                    ],
                },
                expected_artifacts=[
                    "2-name2text.txt",
                    "3-bert",
                ],
                requires_gpu=True,
            ),
            PreprocessingStage(
                stage_id="cnhubert",
                display_name="CNHubert va WAV 32k",
                script_key="prepare_hubert",
                command=command(
                    "prepare_hubert"
                ),
                env={
                    **common_env,
                    "cnhubert_base_dir": pretrained[
                        "hubert"
                    ][
                        "path"
                    ],
                },
                expected_artifacts=[
                    "4-cnhubert",
                    "5-wav32k",
                ],
                requires_gpu=True,
            ),
            PreprocessingStage(
                stage_id="speaker_vector",
                display_name="Speaker vector v2Pro",
                script_key="prepare_sv",
                command=command(
                    "prepare_sv"
                ),
                env={
                    **common_env,
                    "sv_path": pretrained[
                        "speaker_vector"
                    ][
                        "path"
                    ],
                },
                expected_artifacts=[
                    "7-sv_cn",
                ],
                requires_gpu=True,
            ),
            PreprocessingStage(
                stage_id="semantic",
                display_name="Semantic token",
                script_key="prepare_semantic",
                command=command(
                    "prepare_semantic"
                ),
                env={
                    **common_env,
                    "pretrained_s2G": pretrained[
                        "sovits_g"
                    ][
                        "path"
                    ],
                    "s2config_path": str(
                        Path(
                            runtime["runtime_root"]
                        )
                        / "GPT_SoVITS"
                        / "configs"
                        / "s2v2Pro.json"
                    ),
                },
                expected_artifacts=[
                    "6-name2semantic.tsv",
                ],
                requires_gpu=True,
            ),
        ]

    def combine_stage_output(
        self,
        stage,
        plan,
    ):

        output = Path(
            plan.output_root
        )

        if stage.stage_id == "text_phoneme":

            self.combine_parts(
                output,
                "2-name2text",
                "txt",
                output / "2-name2text.txt",
                header="",
            )

        if stage.stage_id == "semantic":

            self.combine_parts(
                output,
                "6-name2semantic",
                "tsv",
                output / "6-name2semantic.tsv",
                header="item_name\tsemantic_audio",
            )

    def combine_parts(
        self,
        root,
        stem,
        suffix,
        final_file,
        header="",
    ):

        parts = sorted(
            Path(
                root
            ).glob(
                f"{stem}-*.{suffix}"
            )
        )

        if not parts:

            return

        lines = []

        if header:

            lines.append(
                header
            )

        for part in parts:

            lines.extend(
                [
                    line
                    for line in part.read_text(
                        encoding="utf-8"
                    ).splitlines()
                    if line.strip()
                ]
            )

        self.write_text_atomic(
            final_file,
            "\n".join(
                lines
            )
            + "\n",
        )

        for part in parts:

            part.unlink(
                missing_ok=True
            )

    def stage_can_reuse(
        self,
        stage,
        plan,
    ):

        validation = self.validate_stage_artifacts(
            stage,
            plan,
        )

        return validation.get(
            "ok",
            False,
        )

    def validate_stage_artifacts(
        self,
        stage,
        plan,
    ):

        output = Path(
            plan.output_root
        )

        errors = []
        artifacts = {}

        for relative in stage.expected_artifacts:

            path = (
                output
                / relative
            )

            item = self.validate_artifact_path(
                path,
                plan.clip_count,
            )

            artifacts[
                relative
            ] = item

            if not item.get(
                "ok",
                False,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_OUTPUT_INVALID",
                        item.get(
                            "reason",
                            "artifact_invalid",
                        ),
                        detected_path=str(
                            path
                        ),
                    )
                )

        return {
            "ok": not errors,
            "artifacts": artifacts,
            "errors": errors,
        }

    def validate_artifacts(
        self,
        plan,
    ):

        artifacts = {}
        errors = []

        for name, relative in {
            **self.REQUIRED_ARTIFACTS,
            **self.OPTIONAL_ARTIFACTS,
        }.items():

            path = (
                Path(
                    plan.output_root
                )
                / relative
            )

            item = self.validate_artifact_path(
                path,
                plan.clip_count,
            )

            artifacts[
                name
            ] = item

            if name in self.REQUIRED_ARTIFACTS and not item.get(
                "ok",
                False,
            ):

                errors.append(
                    self.issue(
                        "PREPROCESS_OUTPUT_INVALID",
                        item.get(
                            "reason",
                            "artifact_invalid",
                        ),
                        detected_path=str(
                            path
                        ),
                    )
                )

        return {
            "training_ready": not errors,
            "artifacts": artifacts,
            "errors": errors,
        }

    def validate_artifact_path(
        self,
        path,
        expected_count=0,
    ):

        path = Path(
            path
        )

        if not path.exists():

            return {
                "ok": False,
                "path": str(
                    path
                ),
                "reason": "artifact_missing",
                "count": 0,
                "size": 0,
                "sha256": "",
            }

        if path.is_file():

            size = path.stat().st_size

            if size <= 0:

                return {
                    "ok": False,
                    "path": str(
                        path
                    ),
                    "reason": "artifact_empty",
                    "count": 0,
                    "size": size,
                    "sha256": "",
                }

            count = len(
                [
                    line
                    for line in path.read_text(
                        encoding="utf-8",
                        errors="replace",
                    ).splitlines()
                    if line.strip()
                ]
            )

            if path.name == "6-name2semantic.tsv" and count > 0:

                count = max(
                    0,
                    count - 1,
                )

            return {
                "ok": True,
                "path": str(
                    path
                ),
                "reason": "",
                "count": count,
                "size": size,
                "sha256": self.sha256_file(
                    path
                ),
            }

        files = [
            item
            for item in path.rglob(
                "*"
            )
            if item.is_file()
        ]

        if not files:

            return {
                "ok": False,
                "path": str(
                    path
                ),
                "reason": "artifact_dir_empty",
                "count": 0,
                "size": 0,
                "sha256": "",
            }

        size = sum(
            item.stat().st_size
            for item in files
        )

        return {
            "ok": True,
            "path": str(
                path
            ),
            "reason": "",
            "count": len(
                files
            ),
            "size": size,
            "fingerprint": self.fingerprint_json(
                self.file_fingerprints(
                    files
                )
            ),
        }

    def acquire_gpu_lease(
        self,
        stage,
        plan,
    ):

        job = JobModel(
            job_id=plan.preprocessing_run_id,
            job_type="training_preprocess",
            voice_id=plan.voice_id,
        )

        requirement = ResourceRequirement(
            profile_id=f"gpu_{stage.stage_id}",
            cpu_threads=1,
            ram_mb=2048,
            disk_free_mb=1024,
            requires_gpu=True,
            gpu_count=1,
            vram_mb=2048,
            allow_cpu_fallback=False,
            exclusive_gpu=True,
            notes="GPT-SoVITS preprocessing GPU stage.",
        )

        return self.lease_manager.acquire(
            job,
            requirement,
            selected_gpu_device_id="0",
            owner="training_preprocessing",
        )

    def preprocessing_status_for_training(
        self,
        manifest_path,
        expected_dataset_fingerprint="",
        expected_runtime_fingerprint="",
    ):

        file = Path(
            manifest_path or ""
        )

        if not manifest_path or not file.exists():

            return {
                "status": "MISSING",
                "training_ready": False,
                "manifest": {},
                "blockers": [
                    self.issue(
                        "PREPROCESS_OUTPUT_MISSING",
                        "Chua co preprocessing_manifest.json.",
                        detected_path=str(
                            file
                        ),
                    )
                ],
            }

        manifest = json.loads(
            file.read_text(
                encoding="utf-8"
            )
        )

        stale = []

        if (
            expected_dataset_fingerprint
            and manifest.get(
                "dataset_fingerprint"
            )
            != expected_dataset_fingerprint
        ):

            stale.append(
                "dataset_fingerprint_changed"
            )

        if (
            expected_runtime_fingerprint
            and manifest.get(
                "runtime_fingerprint"
            )
            != expected_runtime_fingerprint
        ):

            stale.append(
                "runtime_fingerprint_changed"
            )

        if stale:

            return {
                "status": "STALE",
                "training_ready": False,
                "manifest": manifest,
                "blockers": [
                    self.issue(
                        "PREPROCESS_OUTPUT_INVALID",
                        ",".join(
                            stale
                        ),
                    )
                ],
            }

        if manifest.get(
            "training_ready",
            False,
        ):

            return {
                "status": "READY",
                "training_ready": True,
                "manifest": manifest,
                "blockers": [],
            }

        return {
            "status": "BLOCKED",
            "training_ready": False,
            "manifest": manifest,
            "blockers": manifest.get(
                "blockers",
                [],
            ),
        }

    def write_manifest(
        self,
        run,
        plan,
        dataset,
        runtime,
        artifact_validation=None,
    ):

        artifact_validation = artifact_validation or self.validate_artifacts(
            plan
        )

        manifest = {
            "schema_version": PREPROCESSING_SCHEMA_VERSION,
            "run_id": run.preprocessing_run_id,
            "preprocessing_run_id": run.preprocessing_run_id,
            "voice_id": run.voice_id,
            "display_name_snapshot": run.display_name_snapshot,
            "dataset_path": plan.metadata_path,
            "dataset_fingerprint": plan.metadata_sha256,
            "runtime_profile_id": plan.runtime_profile_id,
            "runtime_fingerprint": plan.runtime_fingerprint,
            "runtime": {
                "profile_id": runtime.get(
                    "profile_id",
                    "",
                ),
                "runtime_root": runtime.get(
                    "runtime_root",
                    "",
                ),
                "python_path": runtime.get(
                    "python_path",
                    "",
                ),
                "supported_languages": runtime.get(
                    "supported_languages",
                    [],
                ),
            },
            "input_metadata": {
                "path": plan.metadata_path,
                "normalized_path": plan.normalized_metadata_path,
                "clip_count": plan.clip_count,
                "total_duration": plan.total_duration,
                "language": plan.language,
                "sample_rate": plan.sample_rate,
            },
            "output_root": plan.output_root,
            "stages": [
                stage.to_dict()
                for stage in run.stages
            ],
            "artifacts": artifact_validation.get(
                "artifacts",
                {},
            ),
            "counts": {
                "input_clips": dataset.get(
                    "clip_count",
                    0,
                ),
                "name2text": artifact_validation.get(
                    "artifacts",
                    {},
                ).get(
                    "name2text",
                    {},
                ).get(
                    "count",
                    0,
                ),
                "semantic": artifact_validation.get(
                    "artifacts",
                    {},
                ).get(
                    "semantic",
                    {},
                ).get(
                    "count",
                    0,
                ),
            },
            "blockers": run.blockers,
            "warnings": run.warnings,
            "status": run.status,
            "validation_state": run.status,
            "training_ready": artifact_validation.get(
                "training_ready",
                False,
            ),
            "generated_at": now_iso(),
        }

        self.write_json_atomic(
            run.manifest_path,
            manifest,
        )

        return manifest

    def emit_progress(
        self,
        stage,
        current_step,
        total_steps,
        started,
        message,
        level="info",
        progress_callback=None,
    ):

        elapsed = max(
            0.0,
            time.time() - started,
        )

        payload = {
            "job": "training_preprocessing",
            "stage": stage,
            "current_step": current_step,
            "total_steps": total_steps,
            "current_item": current_step,
            "total_items": total_steps,
            "current_file": stage,
            "percent": (
                current_step * 100.0 / total_steps
                if total_steps
                else 0.0
            ),
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": 0.0,
            "message": message,
            "level": level,
        }

        self.progress_events.append(
            payload
        )

        if progress_callback:

            progress_callback(
                payload
            )

        try:

            from services.app_events import AppEvents

            AppEvents.job_progress(
                payload
            )

        except Exception:

            pass

        return payload

    def is_allowed_path(
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

    def is_cuda_oom(
        self,
        text,
    ):

        lowered = (
            text
            or ""
        ).lower()

        return (
            "out of memory" in lowered
            or "cuda oom" in lowered
            or "cublas_status_alloc_failed" in lowered
        )

    def sha256_file(
        self,
        path,
    ):

        h = hashlib.sha256()

        with open(
            path,
            "rb",
        ) as f:

            for chunk in iter(
                lambda: f.read(
                    1024 * 1024
                ),
                b"",
            ):

                h.update(
                    chunk
                )

        return h.hexdigest()

    def file_fingerprints(
        self,
        paths,
    ):

        result = {}

        for path in paths:

            if not path:

                continue

            item = Path(
                path
            )

            if not item.exists():

                result[
                    str(
                        item
                    )
                ] = {
                    "exists": False,
                }

                continue

            if item.is_dir():

                result[
                    str(
                        item
                    )
                ] = {
                    "exists": True,
                    "kind": "dir",
                    "count": len(
                        [
                            file
                            for file in item.rglob(
                                "*"
                            )
                            if file.is_file()
                        ]
                    ),
                }

                continue

            result[
                str(
                    item
                )
            ] = {
                "exists": True,
                "kind": "file",
                "size": item.stat().st_size,
                "sha256": self.sha256_file(
                    item
                ),
            }

        return result

    def fingerprint_json(
        self,
        data,
    ):

        payload = json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode(
            "utf-8"
        )

        return hashlib.sha256(
            payload
        ).hexdigest()

    def write_json_atomic(
        self,
        file,
        data,
    ):

        file = Path(
            file
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = file.with_suffix(
            file.suffix + ".tmp"
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
            file,
        )

    def write_text_atomic(
        self,
        file,
        text,
    ):

        file = Path(
            file
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = file.with_suffix(
            file.suffix + ".tmp"
        )

        temp.write_text(
            text,
            encoding="utf-8",
        )

        os.replace(
            temp,
            file,
        )

    def issue(
        self,
        code,
        reason,
        detected_path="",
        current_version="",
        required_version="",
        suggestion="",
    ):

        return {
            "code": code,
            "reason": reason,
            "detected_path": detected_path,
            "current_version": current_version,
            "required_version": required_version,
            "suggestion": suggestion,
        }
