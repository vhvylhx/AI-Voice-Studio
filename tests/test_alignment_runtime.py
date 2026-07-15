import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.alignment_service import AlignmentSegment
from services.alignment_service import AlignmentService
from services.train_audio_prep_service import TrainAudioPrepService


class FakeAlignmentService(AlignmentService):

    def check_package(self, python_executable=None):

        return {
            "available": True,
            "version": "test",
            "error": "",
        }

    def resolve_model_path(
        self,
        model="small",
        model_path="",
        model_cache="",
    ):

        return str(
            Path("cache")
            / "test_alignment_runtime"
            / "fake_model"
        )


def test_package_missing():

    service = AlignmentService()

    result = service.validate_runtime(
        python_executable="__missing_python__.exe",
    )

    assert result["status"] == "package_missing"


def test_model_missing():

    class Service(FakeAlignmentService):

        def resolve_model_path(self, **kwargs):

            return ""

    result = Service().validate_runtime(
        model="small",
        cuda_available=False,
        device="auto",
        compute_type=None,
    )

    assert result["status"] == "model_missing"


def test_model_load_failure():

    class Service(FakeAlignmentService):

        def check_model_load(self, runtime):

            return {
                "ready": False,
                "message": "load failed",
            }

    result = Service().validate_runtime(
        check_load=True,
    )

    assert result["status"] == "model_load_failed"


def test_cpu_fallback():

    result = FakeAlignmentService().validate_runtime(
        cuda_available=False,
        device="auto",
        compute_type=None,
    )

    assert result["ready"]
    assert result["device"] == "cpu"
    assert result["compute_type"] == "int8"


def test_metadata_language_and_mock_alignment():

    root = (
        ROOT
        / "cache"
        / "test_alignment_runtime"
    )

    if root.exists():

        shutil.rmtree(
            root
        )

    source = root / "source"

    source.mkdir(
        parents=True,
    )

    audio = source / "001.mp3"

    text = source / "001.txt"

    text.write_text(
        "Xin chào, đây là đoạn kiểm tra tiếng Việt.",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=32000:cl=mono",
            "-t",
            "3",
            str(audio),
        ],
        check=True,
    )

    service = TrainAudioPrepService()

    language_seen = {}

    service.alignment.validate_runtime = lambda **kwargs: {
        "ready": True,
        "status": "ready",
        "message": "OK",
        "python_executable": sys.executable,
        "model": "small",
        "model_path": "mock",
        "device": "cpu",
        "compute_type": "int8",
        "package": {
            "available": True,
            "version": "mock",
        },
    }

    def align_mock(
        audio_file,
        original_text,
        **kwargs,
    ):

        language_seen["language"] = kwargs.get(
            "language"
        )

        return [
            AlignmentSegment(
                text="Xin chào, đây là đoạn kiểm tra tiếng Việt.",
                start=0.0,
                end=2.5,
                score=95.0,
                asr_text="Xin chào, đây là đoạn kiểm tra tiếng Việt.",
                language="vi",
            )
        ]

    service.alignment.align = align_mock

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
        engine_path="",
        limit=1,
        allow_fallback=False,
        quality_config={
            "similarity_threshold": 90,
            "min_clip_duration": 2.0,
            "max_clip_duration": 10.0,
            "target_clip_duration": 6.0,
            "max_source_error_rate": 0.35,
            "min_valid_segments_per_source": 1,
            "allow_ratio_fallback": False,
            "sample_rate": 32000,
            "language": "vi",
            "alignment_model": "small",
            "alignment_device": "auto",
            "alignment_compute_type": None,
        },
    )

    metadata = (
        root
        / "alignment"
        / "metadata.list"
    ).read_text(
        encoding="utf-8"
    )

    assert result["report"]["summary"]["valid_clips"] == 1
    assert language_seen["language"] == "vi"
    assert "|vi|" in metadata
    assert "|VI|" not in metadata


test_package_missing()
test_model_missing()
test_model_load_failure()
test_cpu_fallback()
test_metadata_language_and_mock_alignment()

print("ALIGNMENT_RUNTIME_TEST_OK")
