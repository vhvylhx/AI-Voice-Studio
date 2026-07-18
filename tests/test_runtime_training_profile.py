import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.project_config import ProjectConfig
from models.project_model import ProjectModel
from models.runtime_profile import RuntimeProfile
from models.runtime_training_profile import HardwareInfo
from models.runtime_training_profile import RuntimeTrainingProfile
from services.project_service import ProjectService
from services.runtime_training_profile_service import RuntimeTrainingProfileService


class FakeRuntimeProfiles:

    def __init__(
        self,
        profiles=None,
        validation=None,
    ):

        self.profiles = profiles or [
            RuntimeProfile(
                profile_id="gpt_sovits_v2pro_default",
                display_name="GPT-SoVITS v2Pro",
                engine_version="v2Pro",
                runtime_path="runtime",
                python_path=sys.executable,
                pretrained_model_path="pretrained",
                is_default=True,
            )
        ]

        self.validation = validation or {
            "status": "ready",
            "checks": {
                "python": {
                    "stdout": "3.9.13",
                },
                "torch": {
                    "stdout": json.dumps(
                        {
                            "version": "2.0.0+cu118",
                            "cuda": True,
                            "device_count": 1,
                        }
                    ),
                },
            },
        }

    def list_profiles(
        self,
    ):

        return self.profiles

    def validate(
        self,
        profile,
        smoke_test=False,
    ):

        return self.validation


def reset_root(
    name,
):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(
            root
        )

    root.mkdir(
        parents=True,
    )

    return root


class MockProfileService(RuntimeTrainingProfileService):

    def __init__(
        self,
        hardware,
        runtime_profiles=None,
        app_root=None,
    ):

        super().__init__(
            runtime_profiles=runtime_profiles
            or FakeRuntimeProfiles(),
            app_root=app_root,
        )

        self.mock_hardware = hardware

    def detect_gpu(
        self,
    ):

        return {
            "name": self.mock_hardware.gpu,
            "vram_mb": self.mock_hardware.vram_mb,
        }

    def detect_ram_mb(
        self,
    ):

        return self.mock_hardware.ram_mb


def test_auto_detect_quadro_p1000_selects_compatibility():

    hardware = HardwareInfo(
        gpu="Quadro P1000",
        vram_mb=4096,
        cuda_available=True,
        cpu_threads=8,
        ram_mb=16384,
    )

    service = MockProfileService(
        hardware
    )

    detected = service.detect_hardware()

    profile = service.recommend(
        "auto",
        hardware=detected,
    )

    assert profile.runtime_profile_id == "gpt_sovits_v2pro_default"
    assert profile.compatibility_mode == "compatibility"
    assert profile.compute_mode == "cuda"
    assert profile.batch_size == 1
    assert profile.num_workers == 0
    assert profile.gpt_epochs == 20
    assert profile.sovits_epochs == 50


def test_performance_uses_higher_config_for_stronger_mock():

    hardware = HardwareInfo(
        gpu="RTX 4090",
        vram_mb=24576,
        cuda_available=True,
        cpu_threads=24,
        ram_mb=65536,
        runtime_profile_id="gpt_sovits_v2pro_default",
        runtime_status="ready",
    )

    service = RuntimeTrainingProfileService(
        runtime_profiles=FakeRuntimeProfiles()
    )

    profile = service.performance_profile(
        hardware
    )

    assert profile.batch_size > 1
    assert profile.num_workers > 0
    assert profile.compatibility_mode == "performance"


def test_custom_config_roundtrip_and_project_memory():

    root = reset_root(
        "test_runtime_training_project_memory"
    )

    project = ProjectModel(
        name="Test",
        path=root,
        input_dir=root / "text",
        output_dir=root / "audio",
        cache_dir=root / "cache",
        log_dir=root / "logs",
        config=ProjectConfig(),
    )

    profile = RuntimeTrainingProfile(
        mode="custom",
        auto_detect_hardware=False,
        runtime_profile_id="custom-runtime",
        compute_mode="cpu",
        batch_size=3,
        num_workers=2,
        gpt_epochs=11,
        sovits_epochs=22,
        save_interval=2,
        hardware={
            "fingerprint": "abc",
        },
    )

    service = ProjectService()

    service.save_runtime_training_profile(
        project,
        profile,
    )

    loaded = ProjectConfig.from_dict(
        project.config.to_dict()
    )

    assert loaded.training_profile_mode == "custom"
    assert loaded.auto_detect_hardware is False
    assert loaded.training_runtime_profile_id == "custom-runtime"
    assert loaded.training_batch_size == 3
    assert loaded.training_num_workers == 2
    assert loaded.training_custom_config["batch_size"] == 3
    assert loaded.training_hardware_fingerprint == "abc"


def test_app_managed_runtime_copy_changes_only_workers():

    root = reset_root(
        "test_runtime_training_copy"
    )

    runtime = root / "runtime"

    configs = runtime / "GPT_SoVITS" / "configs"

    configs.mkdir(
        parents=True,
    )

    (configs / "s1longer.yaml").write_text(
        "train:\n"
        "  epochs: 20\n"
        "  batch_size: 8\n"
        "  save_every_n_epoch: 1\n"
        "data:\n"
        "  num_workers: 4\n",
        encoding="utf-8",
    )

    (configs / "s2v2Pro.json").write_text(
        json.dumps(
            {
                "train": {
                    "epochs": 100,
                    "batch_size": 32,
                    "learning_rate": 0.0001,
                }
            }
        ),
        encoding="utf-8",
    )

    script = runtime / "GPT_SoVITS" / "s2_train.py"

    script.write_text(
        "def build():\n"
        "    return dict(num_workers=5)\n",
        encoding="utf-8",
    )

    original = script.read_text(
        encoding="utf-8"
    )

    profile = RuntimeTrainingProfile(
        batch_size=1,
        num_workers=0,
        gpt_epochs=20,
        sovits_epochs=50,
        save_interval=1,
    )

    service = RuntimeTrainingProfileService(
        runtime_profiles=FakeRuntimeProfiles(),
        app_root=root,
    )

    report = service.create_app_managed_runtime_copy(
        runtime,
        root / "voices" / "0001" / "model" / "run001",
        profile,
    )

    assert script.read_text(
        encoding="utf-8"
    ) == original

    copied_script = Path(
        report["sovits_script"]
    ).read_text(
        encoding="utf-8"
    )

    assert "num_workers=0" in copied_script
    assert "num_workers=5" not in copied_script
    assert report["compile"]["ok"] is True

    gpt_config = Path(
        report["gpt_config"]
    ).read_text(
        encoding="utf-8"
    )

    assert "batch_size: 1" in gpt_config
    assert "num_workers: 0" in gpt_config

    sovits_config = json.loads(
        Path(
            report["sovits_config"]
        ).read_text(
            encoding="utf-8"
        )
    )

    assert sovits_config["train"]["batch_size"] == 1
    assert sovits_config["train"]["epochs"] == 50


test_auto_detect_quadro_p1000_selects_compatibility()
test_performance_uses_higher_config_for_stronger_mock()
test_custom_config_roundtrip_and_project_memory()
test_app_managed_runtime_copy_changes_only_workers()

print("RUNTIME_TRAINING_PROFILE_TEST_OK")

