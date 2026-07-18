import importlib.util
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from services.runtime_profile_service import RuntimeProfileService


class RuntimeEnvironmentManager:

    def __init__(
        self,
        app_root=None,
        runtime_profiles=None,
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

    def app_environment(
        self,
    ):

        packages = {
            name: self.package_available(
                name
            )
            for name in (
                "PySide6",
                "docx",
                "faster_whisper",
                "pytest",
            )
        }

        return {
            "kind": "app",
            "python_executable": str(
                Path(
                    sys.executable
                )
            ),
            "python_version": platform.python_version(),
            "packages": packages,
            "ready_for_ui": packages.get(
                "PySide6",
                False,
            ),
            "ready_for_tests": packages.get(
                "pytest",
                False,
            ),
        }

    def voice_runtime_environment(
        self,
        runtime_profile_id="",
    ):

        profile = self.select_runtime_profile(
            runtime_profile_id
        )

        if profile is None:

            return {
                "kind": "voice_runtime",
                "ready": False,
                "status": "runtime_profile_missing",
                "profile": {},
                "validation": {},
            }

        validation = self.runtime_profiles.validate(
            profile,
            smoke_test=False,
        )

        return {
            "kind": "voice_runtime",
            "ready": validation.get(
                "status"
            )
            == "ready",
            "status": validation.get(
                "status",
                "unknown",
            ),
            "profile": profile.to_dict(),
            "validation": validation,
        }

    def alignment_environment(
        self,
    ):

        app = self.app_environment()

        return {
            "kind": "alignment",
            "python_executable": app[
                "python_executable"
            ],
            "faster_whisper": app[
                "packages"
            ].get(
                "faster_whisper",
                False,
            ),
            "ready": app[
                "packages"
            ].get(
                "faster_whisper",
                False,
            ),
        }

    def full_status(
        self,
    ):

        return {
            "app": self.app_environment(),
            "voice_runtime": self.voice_runtime_environment(),
            "alignment": self.alignment_environment(),
            "ffmpeg": self.command_status(
                "ffmpeg",
                [
                    "ffmpeg",
                    "-version",
                ],
            ),
            "ffprobe": self.command_status(
                "ffprobe",
                [
                    "ffprobe",
                    "-version",
                ],
            ),
            "nvidia": self.command_status(
                "nvidia-smi",
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader",
                ],
            ),
        }

    def command_status(
        self,
        executable,
        command,
    ):

        path = shutil.which(
            executable
        )

        if not path:

            return {
                "available": False,
                "path": "",
                "stdout": "",
                "stderr": "",
            }

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )

        except Exception as e:

            return {
                "available": False,
                "path": path,
                "stdout": "",
                "stderr": str(
                    e
                ),
            }

        return {
            "available": result.returncode == 0,
            "path": path,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def package_available(
        self,
        name,
    ):

        return importlib.util.find_spec(
            name
        ) is not None

    def select_runtime_profile(
        self,
        runtime_profile_id="",
    ):

        profiles = self.runtime_profiles.list_profiles()

        if runtime_profile_id:

            for profile in profiles:

                if profile.profile_id == runtime_profile_id:

                    return profile

            return None

        for profile in profiles:

            if profile.is_default:

                return profile

        return profiles[0] if profiles else None
