import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.suspicious_recovery_service import SuspiciousRecoveryService


def make_audio(
    file,
    duration=8,
):

    file.parent.mkdir(
        parents=True,
        exist_ok=True,
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
            str(duration),
            str(file),
        ],
        check=True,
    )


def write_json(
    file,
    data,
):

    file.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )


def make_alignment_root():

    root = ROOT / "cache" / "test_suspicious_recovery"

    if root.exists():

        shutil.rmtree(
            root
        )

    alignment = root / "alignment"

    alignment.mkdir(
        parents=True,
    )

    source_audio = root / "source" / "001.mp3"

    make_audio(
        source_audio,
        duration=8,
    )

    valid_audio = alignment / "existing.wav"

    make_audio(
        valid_audio,
        duration=3,
    )

    valid = [
        {
            "id": "existing",
            "status": "valid",
            "audio": str(
                valid_audio
            ),
            "transcript": str(
                alignment / "existing.txt"
            ),
            "source_audio": str(
                source_audio
            ),
            "source_text": "001.txt",
            "speaker": "source",
            "language": "vi",
            "content": "Doan co san.",
            "asr_text": "Doan co san.",
            "match_score": 95.0,
            "start": 0,
            "end": 3,
            "duration": 3,
            "sample_rate": 32000,
            "channels": 1,
            "codec": "pcm_s16le",
            "metadata_enabled": True,
        }
    ]

    suspicious = [
        {
            "status": "suspicious",
            "code": "no_alignment_match",
            "source_audio": str(
                source_audio
            ),
            "source_text": "001.txt",
            "start": 0,
            "end": 0,
            "duration": 0,
            "similarity": 0,
            "original_text": "Mot hai ba bon.",
            "asr_text": "",
        },
        {
            "status": "suspicious",
            "code": "similarity_too_low",
            "source_audio": str(
                source_audio
            ),
            "source_text": "001.txt",
            "start": 4,
            "end": 6,
            "duration": 2,
            "similarity": 50,
            "original_text": "Khong khop.",
            "asr_text": "Sai noi dung.",
        },
    ]

    report = {
        "quality_config": {
            "similarity_threshold": 90,
            "min_clip_duration": 2.0,
            "max_clip_duration": 10.0,
            "target_clip_duration": 6.0,
            "max_source_error_rate": 0.35,
            "min_valid_segments_per_source": 3,
            "allow_ratio_fallback": False,
            "sample_rate": 32000,
            "language": "vi",
            "alignment_model": "small",
            "alignment_device": "auto",
            "alignment_compute_type": "int8",
        },
        "alignment_runtime": {
            "python_executable": sys.executable,
            "model_path": "mock",
            "device": "cpu",
            "compute_type": "int8",
        },
    }

    state = {
        "valid": valid,
        "suspicious": suspicious,
        "errors": [],
        "source_reports": [],
        "completed_sources": [],
    }

    write_json(
        alignment / "alignment_report.json",
        report,
    )

    write_json(
        alignment / "alignment_state.json",
        state,
    )

    return root, alignment, source_audio


def test_recovery_groups_asr_segments_and_keeps_metadata_valid_only():

    root, alignment, source_audio = make_alignment_root()

    service = SuspiciousRecoveryService()

    service.alignment.transcribe = lambda *args, **kwargs: [
        {
            "text": "Mot hai",
            "start": 0.0,
            "end": 2.1,
            "language": "vi",
            "words": [
                {
                    "word": "Mot",
                    "start": 0.0,
                    "end": 1.0,
                },
                {
                    "word": "hai",
                    "start": 1.0,
                    "end": 2.1,
                },
            ],
        },
        {
            "text": "ba bon.",
            "start": 2.1,
            "end": 4.3,
            "language": "vi",
            "words": [
                {
                    "word": "ba",
                    "start": 2.1,
                    "end": 3.0,
                },
                {
                    "word": "bon.",
                    "start": 3.0,
                    "end": 4.3,
                },
            ],
        },
    ]

    report = service.recover(
        alignment,
        root / "recovery",
    )

    assert report["summary"]["valid_before"] == 1
    assert report["summary"]["recovered_valid"] == 1
    assert report["summary"]["valid_after"] == 2
    assert report["quality_config"]["similarity_threshold"] == 90
    assert report["metadata_validation"]["ok"] is True

    metadata = Path(
        report["metadata_path"]
    ).read_text(
        encoding="utf-8"
    )

    assert metadata.count(
        "|vi|"
    ) == 2


def test_recovery_does_not_reuse_asr_segment_or_approve_low_similarity():

    root, alignment, source_audio = make_alignment_root()

    service = SuspiciousRecoveryService()

    service.alignment.transcribe = lambda *args, **kwargs: [
        {
            "text": "Mot hai ba bon.",
            "start": 0.0,
            "end": 4.0,
            "language": "vi",
            "words": [],
        }
    ]

    report = service.recover(
        alignment,
        root / "recovery",
    )

    assert report["summary"]["recovered_valid"] == 1
    assert report["summary"]["still_suspicious"] == 1
    assert (
        report["still_suspicious"][0]["old_reason"]
        == "similarity_too_low"
    )
    assert report["still_suspicious"][0]["old_similarity"] == 50
