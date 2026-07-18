from pathlib import Path
import json
import platform
import subprocess
import time
import traceback

from core.app_context import AppContext

from models.train_config import TrainConfig
from models.train_state import TrainJobState
from services.audio_service import AudioService
from services.dataset_service import DatasetService
from services.dataset_review_service import DatasetReviewService
from services.log_service import LogService
from services.runtime_profile_service import RuntimeProfileService
from services.app_events import AppEvents


class TrainingService:

    def __init__(self):

        self.audio = AudioService()

        self.dataset = DatasetService()

        self.log = LogService()

        self.runtime_profiles = RuntimeProfileService()

        self.progress_events = []

        self.train_executor = None

        self.last_smoke_result = {}

    def prepare_dataset(
        self,
        source,
        voice,
    ):

        try:

            dataset_dir = (
                voice.path
                / "dataset"
            )

            result = self.dataset.prepare(
                source,
                dataset_dir,
            )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            AppContext.engine_manager.validate_dataset(
                result
            )

            self.log.info(
                "train",
                f"{voice.name} : Dataset OK ({len(result['items'])} cặp)"
            )

            return result

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise

    def prepare_train(
        self,
        voice,
        train_config=None,
        runtime_profile=None,
        review_report=None,
        output_root=None,
        progress_callback=None,
    ):

        config = TrainConfig.from_dict(
            train_config
        )

        config.ensure_run_id()

        started = time.time()

        self.progress_events = []
        self.last_smoke_result = {}

        self.emit_progress(
            "validate",
            1,
            6,
            started,
            "Dang kiem tra dieu kien train.",
            "info",
            progress_callback,
        )

        voice_info = self.voice_info(
            voice
        )

        model_output = self.model_output_dir(
            voice,
            config,
            output_root,
        )

        errors = []

        warnings = []

        review_status = self.validate_review(
            review_report,
            errors,
        )

        self.emit_progress(
            "metadata",
            2,
            6,
            started,
            "Dang kiem tra metadata.list.",
            "info",
            progress_callback,
        )

        metadata = self.validate_metadata(
            config.metadata_path,
            config.sample_rate,
            errors,
        )

        self.emit_progress(
            "voice",
            3,
            6,
            started,
            "Dang kiem tra Voice.",
            "info",
            progress_callback,
        )

        self.validate_voice(
            voice,
            errors,
        )

        self.validate_model_output(
            model_output,
            errors,
        )

        self.emit_progress(
            "runtime",
            4,
            6,
            started,
            "Dang kiem tra Runtime Profile.",
            "info",
            progress_callback,
        )

        runtime = self.validate_runtime(
            config,
            runtime_profile,
            errors,
        )

        self.emit_progress(
            "parameters",
            5,
            6,
            started,
            "Dang kiem tra tham so train.",
            "info",
            progress_callback,
        )

        self.validate_train_parameters(
            config,
            errors,
        )

        status = (
            "validation_failed"
            if errors
            else "validation_ready"
        )

        if (
            not errors
            and config.smoke_test
            and not config.validation_only
        ):

            status = self.run_smoke_test(
                voice,
                config,
                model_output,
                runtime,
                metadata,
                errors,
                warnings,
            )

        elapsed = time.time() - started

        state = TrainJobState(
            run_id=config.run_id,
            voice_id=voice_info["voice_id"],
            status=status,
            model_output=str(
                model_output
            ),
            resume_allowed=True,
            resume_confirmed=False,
        )

        report = self.create_train_report(
            voice_info,
            runtime,
            config,
            metadata,
            model_output,
            status,
            started,
            elapsed,
            state,
            review_status,
            warnings,
            errors,
        )

        report_dir = self.report_dir(
            model_output,
            config.validation_only,
        )

        report_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path = report_dir / "train_report.json"

        state.report_path = str(
            report_path
        )

        report["job_state"] = state.to_dict()

        self.write_json(
            report_path,
            report,
        )

        self.write_json(
            report_dir / "train_state.json",
            state.to_dict(),
        )

        self.emit_progress(
            "done",
            6,
            6,
            started,
            "Hoan tat validation train.",
            "success" if not errors else "error",
            progress_callback,
        )

        return {
            "ready": not errors,
            "status": status,
            "run_id": config.run_id,
            "model_output": str(
                model_output
            ),
            "report": report,
            "report_path": str(
                report_path
            ),
            "state": state.to_dict(),
            "progress": self.progress_events,
        }

    def train(
        self,
        voice,
        dataset,
    ):

        try:

            if not voice.config.engine:

                raise Exception(
                    "Voice chưa chọn Engine."
                )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            self.log.info(
                "train",
                f"Bắt đầu train : {voice.name}"
            )

            AppContext.engine_manager.train(
                voice,
                dataset,
            )

            voice.status = "ready"

            AppContext.voice_service.save(
                voice
            )

            self.log.info(
                "train",
                f"Train thành công : {voice.name}"
            )

            return True

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise

    def create_preview(
        self,
        voice,
    ):

        try:

            if not voice.config.engine:

                raise Exception(
                    "Voice chưa chọn Engine."
                )

            AppContext.engine_manager.select(
                voice.config.engine
            )

            preview = (
                voice.path
                / "preview.wav"
            )

            AppContext.engine_manager.create_preview(
                voice,
                preview,
            )

            self.log.info(
                "train",
                f"Tạo preview : {preview.name}"
            )

            return preview

        except Exception:

            error = traceback.format_exc()

            self.log.error(
                "train",
                error,
            )

            raise

    def validate_review(
        self,
        review_report,
        errors,
    ):

        if review_report is None:

            errors.append(
                self.issue(
                    "dataset_review_required",
                    "Chua co Dataset Review report.",
                    suggestion="Chay buoc Review va approve/reject/ignore cac blocking item truoc khi train.",
                )
            )

            return {
                "train_allowed": False,
                "summary": {},
            }

        train_allowed = DatasetReviewService().can_train(
            review_report=review_report,
        )

        if not train_allowed:

            errors.append(
                self.issue(
                    "dataset_review_not_allowed",
                    "Dataset Review chua cho phep train.",
                    suggestion="Approve, Reject hoac Ignore toan bo blocking item con pending.",
                )
            )

        return {
            "train_allowed": train_allowed,
            "summary": review_report.get(
                "summary",
                {},
            ),
        }

    def validate_metadata(
        self,
        metadata_path,
        sample_rate,
        errors,
    ):

        result = {
            "path": str(
                metadata_path or ""
            ),
            "clip_count": 0,
            "total_duration": 0.0,
            "items": [],
        }

        if not metadata_path:

            errors.append(
                self.issue(
                    "metadata_missing",
                    "Chua cau hinh duong dan metadata.list.",
                    suggestion="Chay Alignment de tao metadata.list hop le truoc khi train.",
                )
            )

            return result

        file = Path(
            metadata_path
        )

        result["path"] = str(
            file
        )

        if not file.exists():

            errors.append(
                self.issue(
                    "metadata_missing",
                    "Khong tim thay metadata.list.",
                    detected_path=str(
                        file
                    ),
                    suggestion="Kiem tra output Alignment hoac chay lai Alignment.",
                )
            )

            return result

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
                    "metadata_empty",
                    "metadata.list rong.",
                    detected_path=str(
                        file
                    ),
                    suggestion="Chi train khi Alignment tao duoc valid clip.",
                )
            )

            return result

        for line_number, line in enumerate(
            lines,
            start=1,
        ):

            item = self.parse_metadata_line(
                line,
                line_number,
                errors,
            )

            if item is None:

                continue

            self.validate_metadata_audio(
                item,
                sample_rate,
                errors,
            )

            result["items"].append(
                item
            )

            result["total_duration"] += float(
                item.get(
                    "duration",
                    0,
                )
            )

        result["clip_count"] = len(
            result["items"]
        )

        return result

    def parse_metadata_line(
        self,
        line,
        line_number,
        errors,
    ):

        parts = line.split(
            "|",
            3,
        )

        if len(parts) != 4:

            errors.append(
                self.issue(
                    "metadata_invalid_format",
                    "Dong metadata khong dung format audio|speaker|language|text.",
                    detected_path=f"line {line_number}",
                    suggestion="Chi dung metadata.list sinh ra tu Alignment valid.",
                )
            )

            return None

        audio_path, speaker, language, text = parts

        if not text.strip():

            errors.append(
                self.issue(
                    "transcript_empty",
                    "Transcript trong metadata rong.",
                    detected_path=f"line {line_number}",
                    suggestion="Loai clip rong khoi metadata.list.",
                )
            )

        return {
            "line": line_number,
            "audio": audio_path,
            "speaker": speaker,
            "language": language,
            "text": text,
            "duration": 0.0,
        }

    def validate_metadata_audio(
        self,
        item,
        sample_rate,
        errors,
    ):

        audio = Path(
            item["audio"]
        )

        if not audio.exists():

            errors.append(
                self.issue(
                    "metadata_audio_missing",
                    "Khong tim thay WAV trong metadata.",
                    detected_path=str(
                        audio
                    ),
                    suggestion="Kiem tra metadata.list va thu muc clips.",
                )
            )

            return

        try:

            info = self.audio.probe(
                audio
            )

        except Exception as e:

            errors.append(
                self.issue(
                    "metadata_audio_probe_failed",
                    f"Khong doc duoc WAV: {e}",
                    detected_path=str(
                        audio
                    ),
                    suggestion="Chay lai Alignment hoac kiem tra ffprobe.",
                )
            )

            return

        item["duration"] = info["duration"]
        item["audio_info"] = info

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
                    "metadata_audio_invalid_format",
                    "WAV khong dung mono/pcm_s16le/32000Hz.",
                    detected_path=str(
                        audio
                    ),
                    current_version=(
                        f"{info.get('channels')}ch/"
                        f"{info.get('codec')}/"
                        f"{info.get('sample_rate')}Hz"
                    ),
                    required_version=f"mono/pcm_s16le/{sample_rate}Hz",
                    suggestion="Chay lai Alignment voi cau hinh sample_rate dung.",
                )
            )

    def validate_voice(
        self,
        voice,
        errors,
    ):

        if voice is None:

            errors.append(
                self.issue(
                    "voice_missing",
                    "Chua chon Voice.",
                )
            )

            return

        if not getattr(
            voice,
            "id",
            "",
        ):

            errors.append(
                self.issue(
                    "voice_id_missing",
                    "Voice khong co ID co dinh.",
                    suggestion="Kiem tra voice.json va migration Voice Schema.",
                )
            )

        if not getattr(
            voice,
            "name",
            "",
        ):

            errors.append(
                self.issue(
                    "voice_name_missing",
                    "Voice khong co ten hien thi.",
                )
            )

    def validate_model_output(
        self,
        model_output,
        errors,
    ):

        if model_output.exists():

            errors.append(
                self.issue(
                    "model_output_exists",
                    "Thu muc output model da ton tai, khong ghi de model cu.",
                    detected_path=str(
                        model_output
                    ),
                    suggestion="Tao run_id moi hoac chon resume sau khi nguoi dung xac nhan.",
                )
            )

    def validate_runtime(
        self,
        config,
        runtime_profile,
        errors,
    ):

        profile = self.select_runtime_profile(
            config,
            runtime_profile,
        )

        if profile is None:

            errors.append(
                self.issue(
                    "runtime_profile_missing",
                    "Chua co Runtime Profile mac dinh hoac profile duoc chon.",
                    suggestion="Cau hinh Runtime Profile GPT-SoVITS truoc khi train.",
                )
            )

            return {
                "profile": {},
                "validation": {},
            }

        validation = self.runtime_profiles.validate(
            profile,
            smoke_test=False,
        )

        for cause in validation.get(
            "causes",
            [],
        ):

            code = cause.get(
                "code",
                "runtime_invalid",
            )

            errors.append(
                self.issue(
                    code,
                    cause.get(
                        "message",
                        "Runtime Profile chua san sang.",
                    ),
                    detected_path=validation.get(
                        "detected_path",
                        {},
                    ),
                    suggestion=self.runtime_suggestion(
                        code
                    ),
                    commands=self.runtime_commands(
                        code
                    ),
                )
            )

        if not getattr(
            profile,
            "pretrained_model_path",
            "",
        ):

            errors.append(
                self.issue(
                    "pretrained_model_missing",
                    "Chua cau hinh pretrained_model_path.",
                    suggestion="Chon pretrained model phu hop GPT-SoVITS v2Pro truoc khi train.",
                )
            )

        return {
            "profile": profile.to_dict(),
            "validation": validation,
            "environment": self.runtime_environment(
                validation,
            ),
        }

    def select_runtime_profile(
        self,
        config,
        runtime_profile,
    ):

        if runtime_profile is not None:

            from models.runtime_profile import RuntimeProfile

            return RuntimeProfile.from_dict(
                runtime_profile
            )

        profiles = self.runtime_profiles.list_profiles()

        if config.runtime_profile_id:

            for profile in profiles:

                if profile.profile_id == config.runtime_profile_id:

                    return profile

            return None

        for profile in profiles:

            if profile.is_default:

                return profile

        return profiles[0] if profiles else None

    def validate_train_parameters(
        self,
        config,
        errors,
    ):

        if config.validation_only or config.smoke_test:

            return

        missing = [
            name
            for name in (
                "batch_size",
                "epochs",
                "save_interval",
                "learning_rate",
                "num_workers",
                "checkpoint_policy",
                "resume_policy",
                "pretrained_model_version",
            )
            if getattr(
                config,
                name,
            )
            in (
                None,
                "",
            )
        ]

        if missing:

            errors.append(
                self.issue(
                    "train_parameters_required",
                    "Chua chot tham so train that.",
                    suggestion=(
                        "Can nguoi dung chot batch size, epoch, save interval, "
                        "learning rate, worker, checkpoint/resume policy va pretrained model version."
                    ),
                    detected_path=", ".join(
                        missing
                    ),
                )
            )

    def run_smoke_test(
        self,
        voice,
        config,
        model_output,
        runtime,
        metadata,
        errors,
        warnings,
    ):

        model_output.mkdir(
            parents=True,
            exist_ok=False,
        )

        if self.train_executor is not None:

            result = self.train_executor(
                {
                    "voice": voice,
                    "config": config.to_dict(),
                    "model_output": str(
                        model_output
                    ),
                }
            )

            self.last_smoke_result = result

            if not result.get(
                "ok",
                False,
            ):

                errors.append(
                    self.issue(
                        "smoke_test_failed",
                        result.get(
                            "message",
                            "Smoke test train that bai.",
                        ),
                    )
                )

                return "smoke_test_failed"

            return "smoke_test_ok"

        command = self.build_smoke_command(
            runtime,
            metadata,
            model_output,
        )

        if not command:

            errors.append(
                self.issue(
                    "smoke_command_missing",
                    "Khong tao duoc command smoke test.",
                )
            )

            return "smoke_test_failed"

        result = self.run_smoke_command(
            command,
            runtime,
            model_output,
        )

        self.last_smoke_result = result

        if not result.get(
            "ok",
            False,
        ):

            errors.append(
                self.issue(
                    "smoke_test_failed",
                    result.get(
                        "message",
                        "Smoke test train that bai.",
                    ),
                    detected_path=result.get(
                        "command",
                        [],
                    ),
                )
            )

            if result.get(
                "out_of_memory",
                False,
            ):

                errors.append(
                    self.issue(
                        "out_of_memory",
                        "CUDA/GPU het VRAM trong smoke test.",
                        suggestion="Giam batch_size, dung fewer clips hoac chot cau hinh VRAM thap hon truoc khi chay lai.",
                    )
                )

            return "smoke_test_failed"

        return "smoke_test_ok"

    def build_smoke_command(
        self,
        runtime,
        metadata,
        model_output,
    ):

        profile = runtime.get(
            "profile",
            {},
        )

        validation = runtime.get(
            "validation",
            {},
        )

        detected_path = validation.get(
            "detected_path",
            {},
        )

        python_path = Path(
            detected_path.get(
                "python_path",
                "",
            )
            or profile.get(
                "python_path",
                "",
            )
        )

        runtime_root = Path(
            detected_path.get(
                "runtime_path",
                "",
            )
            or profile.get(
                "runtime_path",
                "",
            )
        )

        if not python_path.exists() or not runtime_root.exists():

            return []

        model_output = Path(
            model_output
        ).resolve()

        smoke_script = (
            model_output / "smoke_runtime_check.py"
        )

        metadata_path = metadata.get(
            "path",
            "",
        )

        output_json = (
            model_output / "smoke_output.json"
        )

        checkpoint = (
            model_output / "smoke_checkpoint.mock"
        )

        app_root = Path.cwd().resolve()

        smoke_script.write_text(
            self.smoke_script_source(),
            encoding="utf-8",
        )

        return [
            str(
                python_path
            ),
            str(
                smoke_script
            ),
            str(
                runtime_root
            ),
            str(
                metadata_path
            ),
            str(
                output_json
            ),
            str(
                checkpoint
            ),
            str(
                app_root
            ),
        ]

    def run_smoke_command(
        self,
        command,
        runtime,
        model_output,
    ):

        runtime_root = Path(
            command[2]
        )

        model_output = Path(
            model_output
        ).resolve()

        stdout_log = (
            model_output / "smoke_stdout.log"
        )

        stderr_log = (
            model_output / "smoke_stderr.log"
        )

        started = time.time()

        try:

            process = subprocess.run(
                command,
                cwd=str(
                    runtime_root
                ),
                capture_output=True,
                text=True,
                timeout=180,
            )

            stdout = process.stdout or ""

            stderr = process.stderr or ""

            stdout_log.write_text(
                stdout,
                encoding="utf-8",
            )

            stderr_log.write_text(
                stderr,
                encoding="utf-8",
            )

            output_json = Path(
                command[4]
            )

            checkpoint = Path(
                command[5]
            )

            out_of_memory = (
                "out of memory" in stderr.lower()
                or "cuda oom" in stderr.lower()
            )

            return {
                "ok": process.returncode == 0
                and output_json.exists()
                and checkpoint.exists(),
                "message": stderr.strip()
                or stdout.strip()
                or "Smoke test complete.",
                "command": command,
                "exit_code": process.returncode,
                "stdout_log": str(
                    stdout_log
                ),
                "stderr_log": str(
                    stderr_log
                ),
                "output": str(
                    output_json
                ),
                "checkpoint": str(
                    checkpoint
                ),
                "elapsed": time.time() - started,
                "out_of_memory": out_of_memory,
            }

        except Exception as e:

            return {
                "ok": False,
                "message": str(
                    e
                ),
                "command": command,
                "exit_code": None,
                "stdout_log": str(
                    stdout_log
                ),
                "stderr_log": str(
                    stderr_log
                ),
                "elapsed": time.time() - started,
            }

    def smoke_script_source(
        self,
    ):

        return r'''
import json
import sys
import wave
from pathlib import Path

runtime_root = Path(sys.argv[1])
metadata_path = Path(sys.argv[2])
output_json = Path(sys.argv[3])
checkpoint = Path(sys.argv[4])
app_root = Path(sys.argv[5]) if len(sys.argv) > 5 else Path.cwd()

sys.path.insert(0, str(runtime_root))
sys.path.insert(0, str(runtime_root / "GPT_SoVITS"))

import config as gpt_sovits_config
import torch

if not metadata_path.exists():
    raise RuntimeError("metadata_missing")

lines = [line.strip() for line in metadata_path.read_text(encoding="utf-8").splitlines() if line.strip()]
if not lines:
    raise RuntimeError("metadata_empty")

audio_path, speaker, language, text = lines[0].split("|", 3)
if not text.strip():
    raise RuntimeError("transcript_empty")

audio_file = Path(audio_path)
if not audio_file.is_absolute():
    audio_file = app_root / audio_file

with wave.open(str(audio_file), "rb") as audio:
    channels = audio.getnchannels()
    sample_rate = audio.getframerate()
    sample_width = audio.getsampwidth()
    frames = audio.getnframes()

cuda_available = bool(torch.cuda.is_available())
gpu_name = torch.cuda.get_device_name(0) if cuda_available else ""
vram = torch.cuda.get_device_properties(0).total_memory if cuda_available else 0
peak_vram = torch.cuda.max_memory_allocated(0) if cuda_available else 0

if not cuda_available:
    raise RuntimeError("cuda_unavailable")

output_json.write_text(json.dumps({
    "metadata_path": str(metadata_path),
    "audio_path": str(audio_file),
    "speaker": speaker,
    "language": language,
    "text_length": len(text),
    "channels": channels,
    "sample_rate": sample_rate,
    "sample_width": sample_width,
    "frames": frames,
    "cuda_available": cuda_available,
    "gpu_name": gpu_name,
    "vram": vram,
    "peak_vram": peak_vram,
    "engine_version": "v2Pro" if (runtime_root / "GPT_SoVITS" / "configs" / "s2v2Pro.json").exists() else "",
    "pretrained_sovits": gpt_sovits_config.pretrained_sovits_name.get("v2Pro", ""),
    "pretrained_gpt": gpt_sovits_config.pretrained_gpt_name.get("v2Pro", ""),
}, indent=4, ensure_ascii=False), encoding="utf-8")

checkpoint.write_text("smoke checkpoint placeholder", encoding="utf-8")
print("GPT-SoVITS smoke OK")
'''

    def voice_info(
        self,
        voice,
    ):

        return {
            "voice_id": getattr(
                voice,
                "id",
                "",
            ),
            "voice_name": getattr(
                voice,
                "name",
                "",
            ),
        }

    def model_output_dir(
        self,
        voice,
        config,
        output_root=None,
    ):

        voice_id = getattr(
            voice,
            "id",
            "unknown",
        ) or "unknown"

        root = Path(
            output_root
            or "voices"
        )

        return (
            root
            / voice_id
            / "model"
            / config.run_id
        )

    def report_dir(
        self,
        model_output,
        validation_only,
    ):

        if validation_only:

            return (
                Path(
                    "cache"
                )
                / "train_validation"
                / model_output.name
            )

        return model_output

    def create_train_report(
        self,
        voice_info,
        runtime,
        config,
        metadata,
        model_output,
        status,
        started,
        elapsed,
        state,
        review_status,
        warnings,
        errors,
    ):

        environment = runtime.get(
            "environment",
            {},
        )

        profile = runtime.get(
            "profile",
            {},
        )

        return {
            "schema_version": 1,
            "voice_id": voice_info["voice_id"],
            "voice_name": voice_info["voice_name"],
            "runtime_profile": profile.get(
                "profile_id",
                "",
            ),
            "engine_version": profile.get(
                "engine_version",
                "",
            ),
            "python_version": environment.get(
                "python_version",
                platform.python_version(),
            ),
            "torch_version": environment.get(
                "torch_version",
                "",
            ),
            "device": environment.get(
                "device",
                "",
            ),
            "gpu": environment.get(
                "gpu",
                "",
            ),
            "vram": environment.get(
                "vram",
                "",
            ),
            "metadata_path": metadata.get(
                "path",
                "",
            ),
            "clip_count": metadata.get(
                "clip_count",
                0,
            ),
            "total_duration": metadata.get(
                "total_duration",
                0,
            ),
            "train_parameters": config.to_dict(),
            "start_time": started,
            "elapsed": elapsed,
            "status": status,
            "checkpoint": state.checkpoint,
            "model_output": str(
                model_output
            ),
            "dataset_review": review_status,
            "warnings": warnings,
            "errors": errors,
            "progress": self.progress_events,
            "runtime_validation": runtime.get(
                "validation",
                {},
            ),
            "script_paths": runtime.get(
                "validation",
                {},
            ).get(
                "checks",
                {},
            ).get(
                "gpt_sovits_scripts",
                {},
            ),
            "pretrained_paths": runtime.get(
                "validation",
                {},
            ).get(
                "checks",
                {},
            ).get(
                "pretrained_models",
                {},
            ),
            "smoke_test": self.last_smoke_result,
        }

    def runtime_environment(
        self,
        validation,
    ):

        checks = validation.get(
            "checks",
            {},
        )

        python_version = checks.get(
            "python",
            {},
        ).get(
            "stdout",
            "",
        )

        torch_info = self.parse_json(
            checks.get(
                "torch",
                {},
            ).get(
                "stdout",
                "{}",
            )
        )

        gpu = self.detect_gpu()

        return {
            "python_version": python_version,
            "torch_version": torch_info.get(
                "version",
                "",
            ),
            "device": (
                "cuda"
                if torch_info.get(
                    "cuda",
                    False,
                )
                else "cpu"
            ),
            "gpu": gpu.get(
                "name",
                "",
            ),
            "vram": gpu.get(
                "vram",
                "",
            ),
        }

    def parse_json(
        self,
        text,
    ):

        try:

            return json.loads(
                text or "{}"
            )

        except Exception:

            return {}

    def detect_gpu(
        self,
    ):

        try:

            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

        except Exception:

            return {
                "name": "",
                "vram": "",
            }

        if result.returncode != 0 or not result.stdout.strip():

            return {
                "name": "",
                "vram": "",
            }

        parts = [
            item.strip()
            for item in result.stdout.splitlines()[0].split(
                ","
            )
        ]

        return {
            "name": parts[0] if parts else "",
            "vram": parts[1] if len(
                parts
            )
            > 1
            else "",
        }

    def runtime_suggestion(
        self,
        code,
    ):

        guidance = self.runtime_profiles.guidance()

        item = guidance.get(
            code,
            {},
        )

        return item.get(
            "note",
            "Kiem tra Runtime Profile va cai dat dependency thieu.",
        )

    def runtime_commands(
        self,
        code,
    ):

        return self.runtime_profiles.guidance().get(
            code,
            {},
        ).get(
            "commands",
            [],
        )

    def issue(
        self,
        code,
        reason,
        detected_path="",
        current_version="",
        required_version="",
        suggestion="",
        commands=None,
    ):

        return {
            "code": code,
            "reason": reason,
            "detected_path": detected_path,
            "current_version": current_version,
            "required_version": required_version,
            "suggestion": suggestion,
            "commands": commands or [],
        }

    def emit_progress(
        self,
        stage,
        current_step,
        total_steps,
        started,
        message,
        level,
        progress_callback=None,
    ):

        elapsed = max(
            0.0,
            time.time() - started,
        )

        percent = (
            current_step / total_steps * 100
            if total_steps
            else 0
        )

        estimated = (
            elapsed / current_step * (total_steps - current_step)
            if current_step and current_step < total_steps
            else 0
        )

        payload = {
            "job": "training",
            "stage": stage,
            "current_step": current_step,
            "total_steps": total_steps,
            "current_item": current_step,
            "total_items": total_steps,
            "current_file": "",
            "percent": percent,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": estimated,
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

        AppEvents.job_progress(
            payload
        )

        return payload

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )
