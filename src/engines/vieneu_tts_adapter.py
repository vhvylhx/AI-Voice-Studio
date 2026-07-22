from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


class VieNeuTTSAdapter:

    ENGINE_ID = "vieneu"
    SAMPLE_RATE = 48000
    DEFAULT_TIMEOUT_SECONDS = 180

    def __init__(
        self,
        app_root=None,
        runtime_python=None,
        model_root=None,
        codec_root=None,
        runner=None,
    ):

        self.app_root = Path(
            app_root
            or Path(__file__).resolve().parents[2]
        )

        cache_root = (
            self.app_root
            / "cache"
            / "engines"
            / "vieneu_tts"
            / "75ff82a"
        )

        self.runtime_python = Path(
            runtime_python
            or cache_root
            / "runtime"
            / ".venv"
            / "Scripts"
            / "python.exe"
        )

        self.model_root = Path(
            model_root
            or cache_root
            / "models"
            / (
                "pnnbao-ump__VieNeu-TTS-v3-Turbo__"
                "75ff82a72f54d55ed389e1eeb12041d3c4bac7d4"
            )
        )

        self.codec_root = Path(
            codec_root
            or cache_root
            / "codecs"
            / (
                "OpenMOSS-Team__MOSS-Audio-Tokenizer-Nano-ONNX__"
                "ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae"
            )
        )

        self.cli_script = (
            Path(__file__).resolve().parent
            / "vieneu_runtime_cli.py"
        )

        self.runner = runner or subprocess.run

        self.last_command = []
        self.last_stdout = ""
        self.last_stderr = ""
        self.last_returncode = None

    def required_paths(self):

        onnx_dir = self.model_root / "onnx_int8"

        return {
            "runtime_python": self.runtime_python,
            "model_root": self.model_root,
            "model_onnx_dir": onnx_dir,
            "model_prefill": onnx_dir / "vieneu_prefill.onnx",
            "model_decode_step": onnx_dir / "vieneu_decode_step.onnx",
            "model_acoustic_cached": onnx_dir / "vieneu_acoustic_cached.onnx",
            "model_heads": onnx_dir / "vieneu_v3_heads.npz",
            "codec_root": self.codec_root,
            "cli_script": self.cli_script,
        }

    def missing_files(self):

        return [
            name
            for name, path in self.required_paths().items()
            if not path.exists()
        ]

    def exists(self):

        return not self.missing_files()

    def scoped_env(self):

        env = os.environ.copy()

        python_path = str(
            self.app_root
        )

        if env.get(
            "PYTHONPATH"
        ):

            python_path = (
                python_path
                + os.pathsep
                + env["PYTHONPATH"]
            )

        env.update(
            {
                "PYTHONPATH": python_path,
                "CUDA_VISIBLE_DEVICES": "",
                "OMP_NUM_THREADS": "2",
                "MKL_NUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2",
                "HF_HUB_OFFLINE": "1",
            }
        )

        return env

    def build_probe_command(self):

        return [
            str(
                self.runtime_python
            ),
            str(
                self.cli_script
            ),
            "--probe",
            "--model-root",
            str(
                self.model_root
            ),
            "--codec-root",
            str(
                self.codec_root
            ),
        ]

    def build_generate_command(
        self,
        text_file,
        output_file,
        reference_audio,
        reference_text="",
        temperature=0.70,
        top_k=20,
        top_p=0.95,
        style="tu_nhien",
        denoise=True,
        max_new_frames=520,
    ):

        command = [
            str(
                self.runtime_python
            ),
            str(
                self.cli_script
            ),
            "--model-root",
            str(
                self.model_root
            ),
            "--codec-root",
            str(
                self.codec_root
            ),
            "--text-file",
            str(
                text_file
            ),
            "--output-file",
            str(
                output_file
            ),
            "--reference-audio",
            str(
                reference_audio
            ),
            "--reference-text",
            str(
                reference_text or ""
            ),
            "--temperature",
            str(
                temperature
            ),
            "--top-k",
            str(
                top_k
            ),
            "--top-p",
            str(
                top_p
            ),
            "--style",
            str(
                style or "tu_nhien"
            ),
            "--max-new-frames",
            str(
                max_new_frames
            ),
            "--threads",
            "2",
        ]

        if denoise:

            command.append(
                "--denoise"
            )

        return command

    def run(
        self,
        command,
        timeout=None,
    ):

        self.last_command = list(
            command
        )

        result = self.runner(
            command,
            cwd=str(
                self.app_root
            ),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=self.scoped_env(),
        )

        self.last_stdout = result.stdout or ""
        self.last_stderr = result.stderr or ""
        self.last_returncode = result.returncode

        return result

    def availability_probe(self):

        missing = self.missing_files()

        if missing:

            return {
                "ready": False,
                "status": "UNAVAILABLE",
                "reason": "vieneu_runtime_missing",
                "missing": missing,
                "runtime_python": str(
                    self.runtime_python
                ),
                "model_root": str(
                    self.model_root
                ),
                "codec_root": str(
                    self.codec_root
                ),
            }

        result = self.run(
            self.build_probe_command(),
            timeout=30,
        )

        status = self.parse_json(
            result.stdout
        )

        if result.returncode != 0:

            return {
                "ready": False,
                "status": "UNAVAILABLE",
                "reason": "vieneu_probe_failed",
                "exit_code": result.returncode,
                "stderr": self.last_stderr,
                "stdout": self.last_stdout,
                "runtime_python": str(
                    self.runtime_python
                ),
                "model_root": str(
                    self.model_root
                ),
                "codec_root": str(
                    self.codec_root
                ),
            }

        if status:

            status.setdefault(
                "ready",
                True,
            )

            status.setdefault(
                "status",
                "READY",
            )

            return status

        return {
            "ready": True,
            "status": "READY",
            "runtime_python": str(
                self.runtime_python
            ),
            "model_root": str(
                self.model_root
            ),
            "codec_root": str(
                self.codec_root
            ),
        }

    def validate(
        self,
        text_file,
        output_file,
        reference_audio,
        reference_text,
    ):

        status = self.availability_probe()

        if not status.get(
            "ready"
        ):

            raise RuntimeError(
                "UNAVAILABLE: VieNeu-TTS runtime chưa sẵn sàng: "
                + status.get(
                    "reason",
                    "unknown",
                )
            )

        self.validate_file(
            text_file,
            "target text",
            {
                ".txt",
                ".tts",
            },
        )

        self.validate_file(
            reference_audio,
            "reference audio",
            {
                ".wav",
                ".mp3",
                ".flac",
                ".m4a",
            },
        )

        if not str(
            reference_text
        ).strip():

            raise RuntimeError(
                "Thiếu reference text cho VieNeu-TTS."
            )

        output = Path(
            output_file
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if output.exists():

            raise RuntimeError(
                f"VieNeu-TTS không ghi đè output đã tồn tại: {output}"
            )

    def generate(
        self,
        text_file,
        output_file,
        reference_audio,
        reference_text,
        temperature=0.70,
        top_k=20,
        top_p=0.95,
        style="tu_nhien",
        denoise=True,
        max_new_frames=520,
        timeout=None,
    ):

        self.validate(
            text_file=text_file,
            output_file=output_file,
            reference_audio=reference_audio,
            reference_text=reference_text,
        )

        output = Path(
            output_file
        )

        command = self.build_generate_command(
            text_file=text_file,
            output_file=output,
            reference_audio=reference_audio,
            reference_text=reference_text,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            style=style,
            denoise=denoise,
            max_new_frames=max_new_frames,
        )

        result = self.run(
            command,
            timeout=timeout or self.DEFAULT_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "VieNeu-TTS command failed "
                f"(exit {result.returncode}).\n"
                f"STDOUT:\n{self.last_stdout}\n"
                f"STDERR:\n{self.last_stderr}"
            )

        if not output.exists():

            raise RuntimeError(
                f"VieNeu-TTS không tạo WAV: {output}"
            )

        if output.stat().st_size <= 44:

            raise RuntimeError(
                f"VieNeu-TTS tạo WAV rỗng hoặc không hợp lệ: {output}"
            )

        return output

    def validate_file(
        self,
        path,
        label,
        suffixes=None,
    ):

        if not str(
            path
        ).strip():

            raise RuntimeError(
                f"Thiếu {label}."
            )

        file = Path(
            path
        )

        if not file.exists():

            raise RuntimeError(
                f"Không tìm thấy {label}: {file}"
            )

        if suffixes and file.suffix.lower() not in suffixes:

            raise RuntimeError(
                f"{label} không đúng định dạng: {file}"
            )

        return file

    def runtime_info(self):

        return self.availability_probe()

    def parse_json(
        self,
        text,
    ):

        try:

            return json.loads(
                text
            )

        except Exception:

            return {}
