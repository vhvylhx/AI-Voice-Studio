from pathlib import Path
import os
import shutil
import subprocess
import tempfile


class GPTSoVITSAdapter:

    def __init__(
        self,
        root,
    ):

        self.root = Path(root)

        self._help_text = None

        self.last_command = []

        self.last_stdout = ""

        self.last_stderr = ""

    #
    # Runtime
    #

    @property
    def runtime(self):

        return (
            self.root
            / "runtime"
            / "python.exe"
        )

    #
    # CLI
    #

    @property
    def inference_cli(self):

        return (
            self.root
            / "GPT_SoVITS"
            / "inference_cli.py"
        )

    #
    # WebUI
    #

    @property
    def webui(self):

        return (
            self.root
            / "webui.py"
        )

    #
    # Version marker
    #

    @property
    def version_marker(self):

        return (
            self.root
            / "GPT_SoVITS"
        )

    #
    # Train
    #

    @property
    def train_dir(self):

        return (
            self.root
            / "GPT_SoVITS"
        )

    #
    # Exists
    #

    def exists(self):

        return (

            self.root.exists()

            and

            self.runtime.exists()

            and

            self.inference_cli.exists()

            and

            self.webui.exists()

        )

    def missing_files(self):

        files = {
            "root": self.root,
            "python": self.runtime,
            "inference_cli": self.inference_cli,
            "webui": self.webui,
        }

        return [
            name
            for name, path in files.items()
            if not path.exists()
        ]

    #
    # Python
    #

    def python(self):

        if self.runtime.exists():

            return self.runtime

        raise RuntimeError(
            "Không tìm thấy runtime/python.exe"
        )

    #
    # Detect
    #

    def detect_version(self):

        if self.version_marker.exists():

            return "GPT-SoVITS v2 Pro"

        return "Unknown"

    def help_text(self):

        if self._help_text is not None:

            return self._help_text

        if not self.exists():

            self._help_text = ""

            return self._help_text

        result = self.run(
            [
                str(
                    self.inference_cli
                ),
                "--help",
            ],
            check=False,
            timeout=20,
        )

        self._help_text = (
            result.stdout
            or
            result.stderr
            or
            ""
        )

        return self._help_text

    def supports_arg(
        self,
        name,
    ):

        return name in self.help_text()

    #
    # Run
    #

    def run(
        self,
        args,
        cwd=None,
        check=True,
        timeout=None,
    ):

        command = self.build_command(
            args
        )

        self.last_command = command

        env = os.environ.copy()

        python_path = str(
            self.root
        )

        if env.get(
            "PYTHONPATH"
        ):

            python_path = (
                python_path
                + os.pathsep
                + env["PYTHONPATH"]
            )

        env["PYTHONPATH"] = python_path

        result = subprocess.run(
            command,
            cwd=cwd or self.root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        self.last_stdout = result.stdout or ""

        self.last_stderr = result.stderr or ""

        if check and result.returncode != 0:

            raise RuntimeError(
                "GPT-SoVITS command failed "
                f"(exit {result.returncode}).\n"
                f"STDOUT:\n{self.last_stdout}\n"
                f"STDERR:\n{self.last_stderr}"
            )

        return result

    def build_command(
        self,
        args,
    ):

        python = str(
            self.python()
        )

        if (
            args
            and
            str(args[0]).lower().endswith(
                ".py"
            )
        ):

            code = (
                "import runpy, sys; "
                f"sys.path.insert(0, {str(self.root)!r}); "
                f"sys.path.insert(0, {str(self.root / 'GPT_SoVITS')!r}); "
                "script = sys.argv[1]; "
                "sys.argv = [script] + sys.argv[2:]; "
                "runpy.run_path(script, run_name='__main__')"
            )

            return [
                python,
                "-c",
                code,
                *args,
            ]

        return [
            python,
            *args,
        ]

    #
    # Validate
    #

    def validate_runtime(self):

        if self.exists():

            return

        missing = ", ".join(
            self.missing_files()
        )

        raise RuntimeError(
            f"GPT-SoVITS runtime chưa sẵn sàng: {missing}"
        )

    def validate_file(
        self,
        path,
        label,
        suffixes=None,
    ):

        file = Path(path)

        if not str(path).strip():

            raise RuntimeError(
                f"Thiếu {label}."
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

    def validate_generate(
        self,
        gpt_model,
        sovits_model,
        reference_audio,
        reference_text,
        target_text,
        output_dir,
    ):

        self.validate_runtime()

        self.validate_file(
            gpt_model,
            "model GPT",
            {
                ".ckpt",
            },
        )

        self.validate_file(
            sovits_model,
            "model SoVITS",
            {
                ".pth",
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

        self.validate_file(
            target_text,
            "target text",
            {
                ".txt",
                ".tts",
            },
        )

        if not str(reference_text).strip():

            raise RuntimeError(
                "Thiếu reference text."
            )

        output = Path(output_dir)

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not output.exists():

            raise RuntimeError(
                f"Không tạo được output folder: {output}"
            )

    #
    # Generate
    #

    def generate(
        self,
        gpt_model,
        sovits_model,
        reference_audio,
        reference_text,
        prompt_language,
        target_text,
        text_language,
        output_dir,
        output_file=None,
        speed=1.0,
        emotion="",
        style="",
        similarity=1.0,
        voice_id="",
        variant="original",
        timeout=3600,
    ):

        self.validate_generate(
            gpt_model=gpt_model,
            sovits_model=sovits_model,
            reference_audio=reference_audio,
            reference_text=reference_text,
            target_text=target_text,
            output_dir=output_dir,
        )

        target_text = Path(
            target_text
        ).resolve()

        output_dir = Path(
            output_dir
        ).resolve()

        output_file = (
            Path(output_file).resolve()
            if output_file
            else output_dir / "output.wav"
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            ref_text_file = self.prepare_reference_text(
                reference_text,
                temp_dir,
            )

            args = [
                str(
                    self.inference_cli
                ),
                "--gpt_model",
                str(gpt_model),
                "--sovits_model",
                str(sovits_model),
                "--ref_audio",
                str(reference_audio),
                "--ref_text",
                str(ref_text_file),
                "--ref_language",
                self.cli_language(
                    prompt_language
                ),
                "--target_text",
                str(target_text),
                "--target_language",
                self.cli_language(
                    text_language
                ),
                "--output_path",
                str(output_dir),
            ]

            self.extend_optional_args(
                args=args,
                speed=speed,
                emotion=emotion,
                style=style,
                similarity=similarity,
                voice_id=voice_id,
                variant=variant,
            )

            self.run(
                args,
                timeout=timeout,
            )

        generated = output_dir / "output.wav"

        if not generated.exists():

            raise RuntimeError(
                f"GPT-SoVITS không tạo output.wav trong {output_dir}"
            )

        if generated != output_file:

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.move(
                str(generated),
                str(output_file),
            )

        return output_file

    def prepare_reference_text(
        self,
        reference_text,
        temp_dir,
    ):

        ref = Path(str(reference_text))

        if ref.exists():

            return ref.resolve()

        file = (
            Path(temp_dir)
            / "reference.txt"
        )

        file.write_text(
            str(reference_text),
            encoding="utf-8",
        )

        return file

    def cli_language(
        self,
        language,
    ):

        mapping = {
            "zh": "中文",
            "cn": "中文",
            "中文": "中文",
            "en": "英文",
            "英文": "英文",
            "ja": "日文",
            "jp": "日文",
            "日文": "日文",
            "vi": "多语种混合",
            "multi": "多语种混合",
            "多语种混合": "多语种混合",
        }

        return mapping.get(
            str(language).lower(),
            language,
        )

    def extend_optional_args(
        self,
        args,
        speed,
        emotion,
        style,
        similarity,
        voice_id,
        variant,
    ):

        optional = [
            ("--speed", speed, speed != 1.0),
            ("--emotion", emotion, bool(emotion)),
            ("--style", style, bool(style)),
            ("--similarity", similarity, similarity != 1.0),
            ("--voice_id", voice_id, False),
            ("--variant", variant, variant not in ["", "original"]),
        ]

        unsupported = []

        for flag, value, required in optional:

            if not required:

                continue

            if self.supports_arg(
                flag
            ):

                args.extend([
                    flag,
                    str(value),
                ])

            else:

                unsupported.append(
                    flag
                )

        if unsupported:

            raise RuntimeError(
                "GPT-SoVITS CLI chưa hỗ trợ tham số generate: "
                + ", ".join(unsupported)
            )

    #
    # Train
    #

    def train(
        self,
        dataset,
        output_dir,
    ):

        raise NotImplementedError(
            "Sprint sau sẽ gọi train CLI của GPT-SoVITS."
        )

    #
    # Detect model
    #

    def find_models(
        self,
        folder,
    ):

        folder = Path(folder)

        result = {
            "gpt": [],
            "sovits": [],
        }

        if not folder.exists():

            return result

        for file in folder.rglob("*"):

            if not file.is_file():

                continue

            suffix = file.suffix.lower()

            if suffix not in [
                ".ckpt",
                ".pth",
            ]:

                continue

            if suffix == ".ckpt":

                result["gpt"].append(
                    file
                )

            if suffix == ".pth":

                result["sovits"].append(
                    file
                )

        return result

    #
    # Runtime info
    #

    def runtime_info(self):

        return {
            "root": str(
                self.root
            ),
            "python": str(
                self.runtime
            ),
            "webui": str(
                self.webui
            ),
            "cli": str(
                self.inference_cli
            ),
            "ready": self.exists(),
            "missing": self.missing_files(),
            "version": self.detect_version(),
        }


## ===== KẾT THÚC FILE =====
