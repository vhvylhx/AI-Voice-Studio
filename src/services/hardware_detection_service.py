import ctypes
import os
import platform
import shutil
import subprocess

from models.resource_model import (
    GPUDeviceInfo,
    HardwareProfile,
)


class HardwareDetectionService:

    def detect(
        self,
    ):

        gpu_devices = self.detect_gpus()

        return HardwareProfile(
            os_name=platform.platform(),
            cpu_name=platform.processor()
            or platform.machine(),
            cpu_threads=os.cpu_count()
            or 0,
            ram_total_mb=self.detect_ram_total_mb(),
            gpu_devices=gpu_devices,
            ffmpeg_available=shutil.which(
                "ffmpeg"
            )
            is not None,
            ffprobe_available=shutil.which(
                "ffprobe"
            )
            is not None,
            nvidia_smi_available=shutil.which(
                "nvidia-smi"
            )
            is not None,
        )

    def detect_gpus(
        self,
    ):

        if shutil.which(
            "nvidia-smi"
        ) is None:

            return []

        command = [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu,temperature.gpu",
            "--format=csv,noheader,nounits",
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )

        except Exception:

            return []

        if result.returncode != 0:

            return []

        devices = []

        for line in result.stdout.splitlines():

            parts = [
                item.strip()
                for item in line.split(
                    ","
                )
            ]

            if len(
                parts
            ) < 7:

                continue

            devices.append(
                GPUDeviceInfo(
                    device_id=parts[0],
                    name=parts[1],
                    vram_total_mb=self.safe_int(
                        parts[2]
                    ),
                    vram_free_mb=self.safe_int(
                        parts[3]
                    ),
                    vram_used_mb=self.safe_int(
                        parts[4]
                    ),
                    utilization_percent=self.safe_float(
                        parts[5]
                    ),
                    temperature_c=self.safe_float(
                        parts[6]
                    ),
                    cuda_available=True,
                    status="available",
                )
            )

        return devices

    def detect_ram_total_mb(
        self,
    ):

        try:

            import psutil

            return int(
                psutil.virtual_memory().total
                / 1024
                / 1024
            )

        except Exception:

            pass

        if platform.system().lower() == "windows":

            class MemoryStatus(ctypes.Structure):

                _fields_ = [
                    (
                        "dwLength",
                        ctypes.c_ulong,
                    ),
                    (
                        "dwMemoryLoad",
                        ctypes.c_ulong,
                    ),
                    (
                        "ullTotalPhys",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailPhys",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullTotalPageFile",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailPageFile",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullTotalVirtual",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "ullAvailVirtual",
                        ctypes.c_ulonglong,
                    ),
                    (
                        "sullAvailExtendedVirtual",
                        ctypes.c_ulonglong,
                    ),
                ]

            status = MemoryStatus()

            status.dwLength = ctypes.sizeof(
                MemoryStatus
            )

            if ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(
                    status
                )
            ):

                return int(
                    status.ullTotalPhys
                    / 1024
                    / 1024
                )

        return 0

    def safe_int(
        self,
        value,
    ):

        try:

            return int(
                float(
                    value
                )
            )

        except Exception:

            return 0

    def safe_float(
        self,
        value,
    ):

        try:

            return float(
                value
            )

        except Exception:

            return 0.0
