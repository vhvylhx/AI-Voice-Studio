from pathlib import Path
import json
import subprocess

from models.runtime_profile import RuntimeProfile


class RuntimeProfileService:

    def __init__(
        self,
        config_file=None,
        app_root=None,
    ):

        self.app_root = Path(
            app_root or Path.cwd()
        ).resolve()

        self.config_file = Path(
            config_file
            or self.app_root
            / "config"
            / "runtime_profiles.json"
        )

    def load(
        self,
    ):

        if not self.config_file.exists():

            return {
                "schema_version": 1,
                "profiles": [],
            }

        data = json.loads(
            self.config_file.read_text(
                encoding="utf-8"
            )
        )

        data.setdefault(
            "schema_version",
            1,
        )

        data.setdefault(
            "profiles",
            [],
        )

        return data

    def save(
        self,
        data,
    ):

        self.config_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.config_file.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def list_profiles(
        self,
    ):

        return [
            RuntimeProfile.from_dict(
                item
            )
            for item in self.load().get(
                "profiles",
                [],
            )
        ]

    def add_profile(
        self,
        profile,
    ):

        profile = RuntimeProfile.from_dict(
            profile
        )

        data = self.load()

        profiles = [
            item
            for item in data.get(
                "profiles",
                [],
            )
            if item.get(
                "profile_id"
            )
            != profile.profile_id
        ]

        profiles.append(
            self.serialize_profile(
                profile
            )
        )

        data["profiles"] = profiles

        self.save(
            data
        )

        return profile

    def set_default(
        self,
        profile_id,
    ):

        data = self.load()

        found = False

        for item in data.get(
            "profiles",
            [],
        ):

            is_default = (
                item.get(
                    "profile_id"
                )
                == profile_id
            )

            item["is_default"] = is_default

            found = found or is_default

        if not found:

            raise ValueError(
                f"Runtime profile khong ton tai: {profile_id}"
            )

        self.save(
            data
        )

    def serialize_profile(
        self,
        profile,
    ):

        profile = RuntimeProfile.from_dict(
            profile
        )

        data = profile.to_dict()

        for key in (
            "runtime_path",
            "python_path",
            "pretrained_model_path",
        ):

            data[key] = self.to_portable_path(
                data.get(
                    key,
                    "",
                )
            )

        return data

    def to_portable_path(
        self,
        value,
    ):

        if not value:

            return ""

        path = Path(
            value
        )

        try:

            resolved = path.resolve()

            return str(
                resolved.relative_to(
                    self.app_root
                )
            )

        except Exception:

            return str(
                path
            )

    def resolve_path(
        self,
        value,
    ):

        if not value:

            return Path()

        path = Path(
            value
        )

        if path.is_absolute():

            return path

        return (
            self.app_root
            / path
        )

    def validate(
        self,
        profile,
        smoke_test=False,
    ):

        profile = RuntimeProfile.from_dict(
            profile
        )

        runtime_path = self.resolve_path(
            profile.runtime_path
        )

        python_path = self.resolve_path(
            profile.python_path
        )

        pretrained_path = self.resolve_path(
            profile.pretrained_model_path
        )

        result = {
            "profile_id": profile.profile_id,
            "status": "ready",
            "causes": [],
            "required_version": "",
            "detected_path": {
                "runtime_path": str(
                    runtime_path
                ),
                "python_path": str(
                    python_path
                ),
                "pretrained_model_path": str(
                    pretrained_path
                ),
            },
            "commands": [],
            "links": [],
            "restart_required": False,
            "checks": {},
            "compatibility_notes": profile.compatibility_notes,
        }

        if profile.runtime_path and not runtime_path.exists():

            self.add_issue(
                result,
                "runtime_missing",
                "Khong tim thay thu muc runtime.",
            )

        if not python_path.exists():

            self.add_issue(
                result,
                "python_missing",
                "Khong tim thay Python runtime.",
            )

            result["commands"].extend([
                "winget install --id Python.Python.3.12 -e",
                "python --version",
                "where python",
            ])

            result["links"].append(
                "https://www.python.org/downloads/"
            )

        else:

            result["checks"]["python"] = self.run_python(
                python_path,
                "import sys; print(sys.version.split()[0])",
            )

            result["checks"]["torch"] = self.run_python(
                python_path,
                (
                    "import json, torch; "
                    "print(json.dumps({"
                    "'version': getattr(torch, '__version__', ''), "
                    "'cuda': bool(torch.cuda.is_available()), "
                    "'device_count': torch.cuda.device_count()"
                    "}))"
                ),
            )

            result["checks"]["faster_whisper"] = self.run_python(
                python_path,
                (
                    "import json, faster_whisper; "
                    "print(json.dumps({"
                    "'version': getattr(faster_whisper, '__version__', '')"
                    "}))"
                ),
            )

            if not result["checks"]["faster_whisper"]["ok"]:

                self.add_issue(
                    result,
                    "package_missing",
                    "Chua co faster-whisper trong Python runtime.",
                )

        if profile.pretrained_model_path and not pretrained_path.exists():

            self.add_issue(
                result,
                "pretrained_model_missing",
                "Khong tim thay pretrained model path.",
            )

        scripts = self.gpt_sovits_scripts(
            runtime_path
        )

        result["checks"]["gpt_sovits_scripts"] = scripts

        if profile.runtime_path and not all(
            item["exists"]
            for item in scripts.values()
        ):

            self.add_issue(
                result,
                "gpt_sovits_scripts_missing",
                "Thieu script GPT-SoVITS can thiet.",
            )

        if smoke_test and result["status"] == "ready":

            result["checks"]["smoke_test"] = self.run_python(
                python_path,
                "import torch, faster_whisper; print('OK')",
            )

            if not result["checks"]["smoke_test"]["ok"]:

                self.add_issue(
                    result,
                    "smoke_test_failed",
                    "Smoke test runtime that bai.",
                )

        return result

    def add_issue(
        self,
        result,
        code,
        message,
    ):

        result["status"] = code

        result["causes"].append(
            {
                "code": code,
                "message": message,
            }
        )

    def gpt_sovits_scripts(
        self,
        runtime_path,
    ):

        scripts = {
            "webui": runtime_path / "webui.py",
            "inference_cli": runtime_path / "GPT_SoVITS" / "inference_webui.py",
            "slice_audio": runtime_path / "tools" / "slice_audio.py",
            "asr_fasterwhisper": runtime_path / "tools" / "asr" / "fasterwhisper_asr.py",
        }

        return {
            key: {
                "path": str(
                    path
                ),
                "exists": path.exists(),
            }
            for key, path in scripts.items()
        }

    def run_python(
        self,
        python_path,
        code,
    ):

        try:

            result = subprocess.run(
                [
                    str(
                        python_path
                    ),
                    "-c",
                    code,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

        except Exception as e:

            return {
                "ok": False,
                "stdout": "",
                "stderr": str(
                    e
                ),
            }

        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def guidance(
        self,
    ):

        return {
            "python_missing": {
                "commands": [
                    "winget install --id Python.Python.3.12 -e",
                    "python --version",
                    "where python",
                ],
                "links": [
                    "https://www.python.org/downloads/",
                ],
                "restart_required": True,
            },
            "ffmpeg_missing": {
                "commands": [
                    "winget install --id Gyan.FFmpeg -e",
                    "ffmpeg -version",
                    "ffprobe -version",
                    "where ffmpeg",
                    "where ffprobe",
                ],
                "links": [
                    "https://ffmpeg.org/download.html",
                ],
                "restart_required": True,
            },
            "nvidia": {
                "commands": [
                    "nvidia-smi",
                ],
                "links": [
                    "https://www.nvidia.com/Download/index.aspx",
                ],
                "restart_required": True,
                "note": "Chi phat hien GPU/driver, khong tu cai driver.",
            },
            "faster_whisper_model_missing": {
                "preferred_path": "models/asr/<model_name>/",
                "links": [
                    "https://huggingface.co/Systran",
                ],
                "restart_required": False,
                "note": "Khong tai model am tham. Chi tai khi nguoi dung xac nhan.",
            },
        }
