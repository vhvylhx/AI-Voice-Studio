import ctypes
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

from models.runtime_training_profile import HardwareInfo
from models.runtime_training_profile import RuntimeTrainingProfile
from services.runtime_profile_service import RuntimeProfileService


class RuntimeTrainingProfileService:

    def __init__(
        self,
        runtime_profiles=None,
        app_root=None,
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

    def detect_hardware(
        self,
        runtime_profile_id="",
    ):

        profile = self.select_runtime_profile(
            runtime_profile_id
        )

        validation = (
            self.runtime_profiles.validate(
                profile,
                smoke_test=False,
            )
            if profile
            else {}
        )

        torch_info = self.parse_json(
            validation.get(
                "checks",
                {},
            )
            .get(
                "torch",
                {},
            )
            .get(
                "stdout",
                "{}",
            )
        )

        gpu = self.detect_gpu()

        info = HardwareInfo(
            gpu=gpu.get(
                "name",
                "",
            ),
            vram_mb=int(
                gpu.get(
                    "vram_mb",
                    0,
                )
                or 0
            ),
            cuda_available=bool(
                torch_info.get(
                    "cuda",
                    False,
                )
            ),
            cpu=platform.processor()
            or platform.machine(),
            cpu_threads=os.cpu_count()
            or 0,
            ram_mb=self.detect_ram_mb(),
            python=validation.get(
                "checks",
                {},
            )
            .get(
                "python",
                {},
            )
            .get(
                "stdout",
                "",
            ),
            runtime_profile_id=(
                profile.profile_id
                if profile
                else ""
            ),
            runtime_status=validation.get(
                "status",
                "missing",
            ),
        )

        info.fingerprint = self.hardware_fingerprint(
            info
        )

        return {
            "hardware": info.to_dict(),
            "runtime_profile": (
                profile.to_dict()
                if profile
                else {}
            ),
            "runtime_validation": validation,
        }

    def recommend(
        self,
        mode="auto",
        custom_config=None,
        hardware=None,
    ):

        mode = (
            mode or "auto"
        ).lower()

        custom = RuntimeTrainingProfile.from_dict(
            custom_config
        )

        detected = hardware or self.detect_hardware(
            custom.runtime_profile_id
        )

        info = HardwareInfo.from_dict(
            detected.get(
                "hardware",
                {},
            )
        )

        if mode == "custom":

            custom.mode = "custom"

            custom.hardware = info.to_dict()

            custom.reason = (
                "Nguoi dung tu chinh cau hinh train."
            )

            return custom

        if mode == "performance":

            return self.performance_profile(
                info,
            )

        if mode == "compatibility":

            return self.compatibility_profile(
                info,
                reason=(
                    "Compatibility uu tien on dinh va it VRAM."
                ),
            )

        if (
            info.vram_mb
            and info.vram_mb >= 8192
            and info.runtime_status == "ready"
        ):

            return self.performance_profile(
                info,
                auto=True,
            )

        return self.compatibility_profile(
            info,
            reason=(
                "Auto phat hien VRAM thap hoac runtime can cau hinh an toan."
            ),
        )

    def compatibility_profile(
        self,
        hardware,
        reason="",
    ):

        return RuntimeTrainingProfile(
            mode="compatibility",
            auto_detect_hardware=True,
            runtime_profile_id=hardware.runtime_profile_id,
            compute_mode=(
                "cuda"
                if hardware.cuda_available
                else "cpu"
            ),
            batch_size=1,
            num_workers=0,
            vram_profile="low_vram",
            gpt_config="s1longer.yaml",
            gpt_epochs=20,
            sovits_config="s2v2Pro.json",
            sovits_epochs=50,
            save_interval=1,
            pretrained_model_version="v2Pro",
            resume_policy="manual",
            checkpoint_policy="save_every_epoch",
            compatibility_mode="compatibility",
            reason=reason,
            hardware=hardware.to_dict(),
        )

    def performance_profile(
        self,
        hardware,
        auto=False,
    ):

        if hardware.vram_mb >= 12288:

            batch_size = 4

            workers = min(
                4,
                max(
                    1,
                    hardware.cpu_threads // 4,
                ),
            )

        elif hardware.vram_mb >= 8192:

            batch_size = 2

            workers = min(
                2,
                max(
                    1,
                    hardware.cpu_threads // 6,
                ),
            )

        else:

            return self.compatibility_profile(
                hardware,
                reason=(
                    "Performance khong du VRAM, ha ve Compatibility."
                ),
            )

        return RuntimeTrainingProfile(
            mode="auto" if auto else "performance",
            auto_detect_hardware=True,
            runtime_profile_id=hardware.runtime_profile_id,
            compute_mode=(
                "cuda"
                if hardware.cuda_available
                else "cpu"
            ),
            batch_size=batch_size,
            num_workers=workers,
            vram_profile="performance",
            gpt_config="s1longer.yaml",
            gpt_epochs=20,
            sovits_config="s2v2Pro.json",
            sovits_epochs=50,
            save_interval=1,
            pretrained_model_version="v2Pro",
            resume_policy="manual",
            checkpoint_policy="save_every_epoch",
            compatibility_mode="performance",
            reason=(
                "Auto chon Performance dua tren VRAM/CPU va runtime ready."
                if auto
                else "Performance profile cho may co VRAM cao hon."
            ),
            hardware=hardware.to_dict(),
        )

    def create_app_managed_runtime_copy(
        self,
        runtime_root,
        run_dir,
        profile,
    ):

        profile = RuntimeTrainingProfile.from_dict(
            profile
        )

        runtime_root = Path(
            runtime_root
        )

        run_dir = Path(
            run_dir
        )

        runtime_copy = run_dir / "runtime_copy"

        config_dir = runtime_copy / "configs"

        script_dir = runtime_copy / "scripts"

        config_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        script_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        gpt_source = (
            runtime_root
            / "GPT_SoVITS"
            / "configs"
            / profile.gpt_config
        )

        sovits_config_source = (
            runtime_root
            / "GPT_SoVITS"
            / "configs"
            / profile.sovits_config
        )

        sovits_script_source = (
            runtime_root
            / "GPT_SoVITS"
            / "s2_train.py"
        )

        gpt_target = config_dir / profile.gpt_config

        sovits_config_target = (
            config_dir / profile.sovits_config
        )

        sovits_script_target = (
            script_dir / "s2_train.py"
        )

        self.copy_gpt_config(
            gpt_source,
            gpt_target,
            profile,
        )

        self.copy_sovits_config(
            sovits_config_source,
            sovits_config_target,
            profile,
        )

        diff = self.copy_sovits_script(
            sovits_script_source,
            sovits_script_target,
            profile,
        )

        compile_result = subprocess.run(
            [
                "python",
                "-m",
                "py_compile",
                str(
                    sovits_script_target
                ),
            ],
            capture_output=True,
            text=True,
        )

        report = {
            "runtime_copy": str(
                runtime_copy
            ),
            "gpt_config": str(
                gpt_target
            ),
            "sovits_config": str(
                sovits_config_target
            ),
            "sovits_script": str(
                sovits_script_target
            ),
            "source_checksums": {
                "gpt_config": self.sha256(
                    gpt_source
                ),
                "sovits_config": self.sha256(
                    sovits_config_source
                ),
                "sovits_script": self.sha256(
                    sovits_script_source
                ),
            },
            "copy_checksums": {
                "gpt_config": self.sha256(
                    gpt_target
                ),
                "sovits_config": self.sha256(
                    sovits_config_target
                ),
                "sovits_script": self.sha256(
                    sovits_script_target
                ),
            },
            "diff_summary": diff,
            "compile": {
                "ok": compile_result.returncode == 0,
                "stdout": compile_result.stdout.strip(),
                "stderr": compile_result.stderr.strip(),
            },
        }

        (
            runtime_copy / "runtime_copy_report.json"
        ).write_text(
            json.dumps(
                report,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return report

    def copy_gpt_config(
        self,
        source,
        target,
        profile,
    ):

        text = Path(
            source
        ).read_text(
            encoding="utf-8"
        )

        text = self.replace_yaml_value(
            text,
            "epochs",
            profile.gpt_epochs,
        )

        text = self.replace_yaml_value(
            text,
            "batch_size",
            profile.batch_size,
        )

        text = self.replace_yaml_value(
            text,
            "save_every_n_epoch",
            profile.save_interval,
        )

        text = self.replace_yaml_value(
            text,
            "num_workers",
            profile.num_workers,
        )

        Path(
            target
        ).write_text(
            text,
            encoding="utf-8",
        )

    def copy_sovits_config(
        self,
        source,
        target,
        profile,
    ):

        data = json.loads(
            Path(
                source
            ).read_text(
                encoding="utf-8"
            )
        )

        train = data.setdefault(
            "train",
            {},
        )

        train["epochs"] = int(
            profile.sovits_epochs
        )

        train["batch_size"] = int(
            profile.batch_size
        )

        train["save_every_epoch"] = int(
            profile.save_interval
        )

        train.setdefault(
            "if_save_latest",
            True,
        )

        train.setdefault(
            "if_save_every_weights",
            True,
        )

        train.setdefault(
            "gpu_numbers",
            "0",
        )

        train.setdefault(
            "pretrained_s2G",
            "",
        )

        train.setdefault(
            "pretrained_s2D",
            "",
        )

        Path(
            target
        ).write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def copy_sovits_script(
        self,
        source,
        target,
        profile,
    ):

        original = Path(
            source
        ).read_text(
            encoding="utf-8"
        )

        old = "num_workers=5"

        new = f"num_workers={int(profile.num_workers)}"

        changed = original.replace(
            old,
            new,
            1,
        )

        Path(
            target
        ).write_text(
            changed,
            encoding="utf-8",
        )

        return {
            "s2_train.py": {
                "changed": old in original,
                "from": old,
                "to": new,
                "occurrences_changed": (
                    1
                    if old in original
                    else 0
                ),
            }
        }

    def replace_yaml_value(
        self,
        text,
        key,
        value,
    ):

        pattern = re.compile(
            rf"^(\s*{re.escape(key)}:\s*)(.+)$",
            re.MULTILINE,
        )

        return pattern.sub(
            rf"\g<1>{value}",
            text,
            count=1,
        )

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
                "vram_mb": 0,
            }

        if result.returncode != 0:

            return {
                "name": "",
                "vram_mb": 0,
            }

        line = result.stdout.splitlines()[0]

        parts = [
            item.strip()
            for item in line.split(
                ","
            )
        ]

        return {
            "name": parts[0] if parts else "",
            "vram_mb": self.parse_memory_mb(
                parts[1] if len(
                    parts
                )
                > 1
                else ""
            ),
        }

    def detect_ram_mb(
        self,
    ):

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

    def parse_memory_mb(
        self,
        text,
    ):

        match = re.search(
            r"(\d+)",
            text or "",
        )

        return int(
            match.group(1)
        ) if match else 0

    def hardware_fingerprint(
        self,
        info,
    ):

        text = "|".join(
            [
                info.gpu,
                str(
                    info.vram_mb
                ),
                str(
                    info.cuda_available
                ),
                info.cpu,
                str(
                    info.cpu_threads
                ),
                str(
                    info.ram_mb
                ),
                info.runtime_profile_id,
                info.runtime_status,
            ]
        )

        return hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()

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

    def sha256(
        self,
        file,
    ):

        file = Path(
            file
        )

        if not file.exists():

            return ""

        return hashlib.sha256(
            file.read_bytes()
        ).hexdigest()

