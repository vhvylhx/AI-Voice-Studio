from pathlib import Path
import json
import platform
import shutil
import subprocess
import sys

from core.app_context import AppContext
from models.runtime_status import RuntimeStatus


class RuntimeService:

    def __init__(self):

        self.engine = None

        self._status = None

    #
    # Engine
    #

    def current(self):

        if self.engine is None:

            self.engine = (
                AppContext.engine_manager.current()
            )

        return self.engine

    def refresh(self):

        self.engine = (
            AppContext.engine_manager.current()
        )

        self._status = None

        return self.engine

    #
    # Status
    #

    def status(self):

        self._status = self.check()

        return self._status

    def status_dict(self):

        return self.status().to_dict()

    def check(self):

        status = RuntimeStatus()

        self.check_python(
            status
        )

        self.check_ffmpeg(
            status
        )

        self.check_nvidia(
            status
        )

        self.check_cuda(
            status
        )

        self.check_gpt_sovits(
            status
        )

        self.check_engine(
            status
        )

        status.ready = (
            status.python_available
            and
            status.ffmpeg_available
            and
            status.engine_available
        )

        return status

    def check_python(
        self,
        status,
    ):

        status.python_available = True

        status.python_version = (
            platform.python_version()
        )

        status.python_executable = str(
            Path(sys.executable)
        )

    def check_ffmpeg(
        self,
        status,
    ):

        ffmpeg = shutil.which(
            "ffmpeg"
        )

        status.ffmpeg_available = (
            ffmpeg is not None
        )

        if not status.ffmpeg_available:

            status.errors.append(
                "Không tìm thấy FFmpeg."
            )

            return

        result = self.run_command([
            ffmpeg,
            "-version",
        ])

        status.ffmpeg_version = (
            result.splitlines()[0]
            if result
            else ""
        )

    def check_nvidia(
        self,
        status,
    ):

        nvidia = shutil.which(
            "nvidia-smi"
        )

        status.nvidia_available = (
            nvidia is not None
        )

        if not status.nvidia_available:

            status.errors.append(
                "Không tìm thấy NVIDIA runtime."
            )

            return

        result = self.run_command([
            nvidia,
            "--query-gpu=name,driver_version",
            "--format=csv,noheader",
        ])

        if not result:

            return

        first = result.splitlines()[0]

        parts = [
            item.strip()
            for item in first.split(",")
        ]

        if parts:

            status.gpu_name = parts[0]

        if len(parts) > 1:

            status.gpu_driver = parts[1]

        status.gpu_available = bool(
            status.gpu_name
        )

    def check_cuda(
        self,
        status,
    ):

        nvcc = shutil.which(
            "nvcc"
        )

        if nvcc is not None:

            status.cuda_available = True

            result = self.run_command([
                nvcc,
                "--version",
            ])

            for line in result.splitlines():

                if "release" in line:

                    status.cuda_version = line.strip()

                    return

            return

        nvidia = shutil.which(
            "nvidia-smi"
        )

        if nvidia is not None:

            result = self.run_command([
                nvidia,
            ])

            marker = "CUDA Version:"

            for line in result.splitlines():

                if marker in line:

                    version = (
                        line.split(marker, 1)[1]
                        .split("|", 1)[0]
                        .strip()
                    )

                    status.cuda_available = True

                    status.cuda_version = version

                    return

        status.cuda_available = False

        status.errors.append(
            "Không tìm thấy CUDA runtime."
        )

        return

    def check_gpt_sovits(
        self,
        status,
    ):

        engine = AppContext.engine_manager.get(
            "gpt_sovits"
        )

        if engine is None:

            status.errors.append(
                "Chưa đăng ký GPT-SoVITS engine."
            )

            return

        status.gpt_sovits_path = str(
            engine.root or ""
        )

        adapter = getattr(
            engine,
            "adapter",
            None,
        )

        if adapter is None:

            path = self.configured_engine_path(
                "gpt_sovits"
            )

            if path and hasattr(
                engine,
                "set_path",
            ):

                engine.set_path(
                    path
                )

                status.gpt_sovits_path = str(
                    engine.root or ""
                )

                adapter = getattr(
                    engine,
                    "adapter",
                    None,
                )

        if adapter is None:

            status.errors.append(
                "Chưa cấu hình đường dẫn GPT-SoVITS."
            )

            return

        status.gpt_sovits_python = str(
            adapter.runtime
        )

        status.gpt_sovits_webui = str(
            adapter.webui
        )

        status.gpt_sovits_cli = str(
            adapter.inference_cli
        )

        status.gpt_sovits_ready = (
            adapter.exists()
        )

        if not status.gpt_sovits_ready:

            status.errors.append(
                "GPT-SoVITS runtime chưa sẵn sàng."
            )

    def configured_engine_path(
        self,
        engine_id,
    ):

        file = Path(
            "config"
        ) / "engines.json"

        if not file.exists():

            return ""

        try:

            data = json.loads(
                file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return ""

        if isinstance(
            data,
            dict,
        ):

            data = data.get(
                "engines",
                [],
            )

        for item in data:

            if not isinstance(
                item,
                dict,
            ):

                continue

            if item.get("id") == engine_id:

                return item.get(
                    "path",
                    "",
                )

        return ""

    def check_engine(
        self,
        status,
    ):

        engine = self.current()

        if engine is None:

            status.errors.append(
                "Chưa chọn Engine."
            )

            return

        info = engine.info()

        status.engine_id = info.id

        status.engine_name = info.name

        status.engine_available = (
            engine.is_available()
        )

        status.engine_running = self.is_running()

        if not status.engine_available:

            status.errors.append(
                f"Engine '{info.id}' chưa sẵn sàng."
            )

    def run_command(
        self,
        command,
    ):

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:

                return ""

            return result.stdout.strip()

        except Exception:

            return ""

    #
    # State
    #

    def available(self):

        engine = self.current()

        if engine is None:

            return False

        return engine.is_available()

    #
    # Generate
    #

    def generate(
        self,
        text_file,
        output_file,
        voice,
    ):

        return self.current().generate(
            text_file=text_file,
            output_file=output_file,
            voice=voice,
        )

    #
    # Train
    #

    def train(
        self,
        voice,
        dataset,
    ):

        return self.current().train(
            voice,
            dataset,
        )

    #
    # Preview
    #

    def preview(
        self,
        voice,
        output_file,
    ):

        return self.current().create_preview(
            voice,
            output_file,
        )

    #
    # Runtime
    #

    def start(self):

        engine = self.current()

        if (
            engine
            and
            hasattr(
                engine,
                "start",
            )
        ):

            return engine.start()

    def stop(self):

        engine = self.current()

        if (
            engine
            and
            hasattr(
                engine,
                "stop",
            )
        ):

            return engine.stop()

    def restart(self):

        self.stop()

        self.start()

    def is_running(self):

        engine = self.current()

        if (
            engine
            and
            hasattr(
                engine,
                "is_running",
            )
        ):

            return engine.is_running()

        return False

    #
    # Dataset
    #

    def validate_dataset(
        self,
        dataset,
    ):

        return self.current().validate_dataset(
            dataset
        )

    #
    # Info
    #

    def info(self):

        return self.current().info()

    #
    # Path
    #

    def set_engine_path(
        self,
        path,
    ):

        engine = self.current()

        if hasattr(
            engine,
            "set_path",
        ):

            engine.set_path(
                Path(path)
            )

        self._status = None


## ===== KẾT THÚC FILE =====
