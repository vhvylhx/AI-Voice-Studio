import platform
import shutil
import subprocess
from pathlib import Path


class SystemService:

    #
    # Python
    #

    def python_version(self):

        return platform.python_version()

    def python_executable(self):

        import sys

        return Path(
            sys.executable
        )

    #
    # Git
    #

    def has_git(self):

        return (
            shutil.which("git")
            is not None
        )

    #
    # Pip
    #

    def has_pip(self):

        return (
            shutil.which("pip")
            is not None
        )

    #
    # CUDA
    #

    def has_cuda(self):

        return (
            shutil.which("nvcc")
            is not None
        )

    #
    # Nvidia
    #

    def has_nvidia(self):

        return (
            shutil.which(
                "nvidia-smi"
            )
            is not None
        )

    def gpu_name(self):

        try:

            result = subprocess.run(

                [

                    "nvidia-smi",

                    "--query-gpu=name",

                    "--format=csv,noheader",

                ],

                capture_output=True,

                text=True,

            )

            return result.stdout.strip()

        except Exception:

            return ""

    #
    # RAM
    #

    def total_ram_gb(self):

        try:

            import psutil

            return round(

                psutil.virtual_memory().total
                / 1024
                / 1024
                / 1024,

                1,

            )

        except Exception:

            return 0

    #
    # Disk
    #

    def free_disk_gb(
        self,
        folder=".",
    ):

        usage = shutil.disk_usage(
            folder
        )

        return round(

            usage.free
            / 1024
            / 1024
            / 1024,

            1,

        )

    #
    # Summary
    #

    def summary(self):

        return {

            "python": self.python_version(),

            "git": self.has_git(),

            "pip": self.has_pip(),

            "cuda": self.has_cuda(),

            "nvidia": self.has_nvidia(),

            "gpu": self.gpu_name(),

            "ram": self.total_ram_gb(),

            "disk": self.free_disk_gb(),

        }