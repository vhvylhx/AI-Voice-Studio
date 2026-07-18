import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from services.bootstrap_service import BootstrapService
from services.feature_readiness_service import FeatureReadinessService
from services.runtime_environment_manager import RuntimeEnvironmentManager


class FakeEnvironment(RuntimeEnvironmentManager):

    def __init__(
        self,
        pyside=True,
        pytest=True,
        docx=True,
        whisper=True,
        runtime_ready=True,
    ):

        self.pyside = pyside
        self.pytest = pytest
        self.docx = docx
        self.whisper = whisper
        self.runtime_ready = runtime_ready

    def full_status(
        self,
    ):

        return {
            "app": {
                "python_executable": sys.executable,
                "python_version": sys.version.split()[0],
                "packages": {
                    "PySide6": self.pyside,
                    "pytest": self.pytest,
                    "docx": self.docx,
                    "faster_whisper": self.whisper,
                },
                "ready_for_ui": self.pyside,
                "ready_for_tests": self.pytest,
            },
            "voice_runtime": {
                "ready": self.runtime_ready,
                "status": "ready"
                if self.runtime_ready
                else "runtime_missing",
            },
            "alignment": {
                "faster_whisper": self.whisper,
                "ready": self.whisper,
            },
            "ffmpeg": {
                "available": True,
            },
            "ffprobe": {
                "available": True,
            },
            "nvidia": {
                "available": True,
            },
        }


def test_bootstrap_setup_required_when_app_shell_missing():

    env = FakeEnvironment(
        pyside=False
    )

    readiness = FeatureReadinessService(
        env
    )

    service = BootstrapService(
        environment=env,
        readiness=readiness,
    )

    target = service.startup_target()

    assert target["target"] == "first_run_setup"
    assert target["status"]["can_start_main_app"] is False


def test_optional_dependency_degrades_not_crashes():

    env = FakeEnvironment(
        pyside=True,
        docx=False,
        whisper=False,
    )

    summary = FeatureReadinessService(
        env
    ).summary()

    assert "app_shell" not in summary["blocking_features"]
    assert summary["limited_mode"] is True


def test_feature_readiness_has_required_features():

    env = FakeEnvironment()

    items = FeatureReadinessService(
        env
    ).summary()["items"]

    ids = {
        item["feature_id"]
        for item in items
    }

    for feature_id in [
        "app_shell",
        "project_management",
        "import_txt",
        "import_docx",
        "dataset_scan",
        "dataset_health",
        "dataset_repair",
        "dataset_review",
        "alignment",
        "training",
        "generation",
        "local_api",
        "testing",
        "runtime_validation",
    ]:

        assert feature_id in ids


test_bootstrap_setup_required_when_app_shell_missing()
test_optional_dependency_degrades_not_crashes()
test_feature_readiness_has_required_features()

print("BOOTSTRAP_FEATURE_READINESS_TEST_OK")
