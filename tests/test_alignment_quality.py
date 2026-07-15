import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.alignment_quality_config import AlignmentQualityConfig
from services.alignment_service import AlignmentSegment
from services.train_audio_prep_service import TrainAudioPrepService


def make_audio(
    file,
    duration=14,
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


def make_words(
    words,
    step=1.0,
):

    result = []

    cursor = 0.0

    for word in words:

        result.append(
            {
                "word": word,
                "start": cursor,
                "end": cursor + step,
            }
        )

        cursor += step

    return result


def make_service(
    matches,
):

    service = TrainAudioPrepService()

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

    service.alignment.align = lambda *args, **kwargs: matches

    return service


def make_source(
    root,
    text_content,
    duration=14,
):

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
        text_content,
        encoding="utf-8",
    )

    make_audio(
        audio,
        duration,
    )

    return source


def quality_config(
    **overrides,
):

    config = AlignmentQualityConfig(
        similarity_threshold=90,
        min_clip_duration=2.0,
        max_clip_duration=10.0,
        target_clip_duration=6.0,
        max_source_error_rate=0.35,
        min_valid_segments_per_source=3,
        allow_ratio_fallback=False,
        sample_rate=32000,
        language="vi",
    )

    for key, value in overrides.items():

        setattr(
            config,
            key,
            value,
        )

    return config


def test_long_clip_split_by_word_timestamp_and_metadata_valid_only():

    root = ROOT / "cache" / "test_alignment_quality_split"

    text = (
        "Mot hai ba bon nam sau. "
        "Bay tam chin muoi muoi mot muoi hai."
    )

    source = make_source(
        root,
        text,
        duration=14,
    )

    words = make_words(
        [
            "Mot",
            "hai",
            "ba",
            "bon",
            "nam",
            "sau.",
            "Bay",
            "tam",
            "chin",
            "muoi",
            "muoi",
            "hai.",
        ]
    )

    match = AlignmentSegment(
        text=text,
        start=0.0,
        end=12.0,
        score=99.0,
        asr_text=text,
        language="vi",
        words=words,
    )

    service = make_service(
        [
            match
        ]
    )

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
        quality_config=quality_config(
            min_valid_segments_per_source=1
        ),
    )

    assert result["report"]["quality_config"]["similarity_threshold"] == 90
    assert len(result["valid"]) == 2
    assert result["suspicious"] == []

    for clip in result["valid"]:

        assert clip["duration"] >= 2.0
        assert clip["duration"] <= 10.0
        assert clip["sample_rate"] == 32000
        assert clip["channels"] == 1
        assert clip["codec"] == "pcm_s16le"

    starts = [
        clip["start"]
        for clip in result["valid"]
    ]

    ends = [
        clip["end"]
        for clip in result["valid"]
    ]

    word_starts = {
        word["start"]
        for word in words
    }

    word_ends = {
        word["end"]
        for word in words
    }

    assert all(
        start in word_starts
        for start in starts
    )
    assert all(
        end in word_ends
        for end in ends
    )

    metadata = (
        root
        / "alignment"
        / "metadata.list"
    ).read_text(
        encoding="utf-8"
    )

    assert metadata.count(
        "|vi|"
    ) == 2


def test_bad_segment_is_skipped_and_processing_continues():

    root = ROOT / "cache" / "test_alignment_quality_continue"

    source = make_source(
        root,
        "Doan dung mot. Doan dung hai.",
        duration=8,
    )

    matches = [
        AlignmentSegment(
            text="sai",
            start=0,
            end=3,
            score=70,
            asr_text="sai",
            language="vi",
        ),
        AlignmentSegment(
            text="Doan dung hai.",
            start=3,
            end=6,
            score=95,
            asr_text="Doan dung hai.",
            language="vi",
        ),
    ]

    service = make_service(
        matches
    )

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
        quality_config=quality_config(
            max_source_error_rate=1.0,
            min_valid_segments_per_source=1,
        ),
    )

    assert len(result["valid"]) == 1
    assert result["suspicious"][0]["code"] == "similarity_too_low"
    assert "Doan dung hai." in (
        root
        / "alignment"
        / "metadata.list"
    ).read_text(
        encoding="utf-8"
    )


def test_source_is_skipped_when_error_rate_exceeded():

    root = ROOT / "cache" / "test_alignment_quality_source_skip"

    source = make_source(
        root,
        "Doan sai. Doan dung.",
        duration=8,
    )

    matches = [
        AlignmentSegment(
            text="sai",
            start=0,
            end=3,
            score=50,
            asr_text="sai",
            language="vi",
        ),
        AlignmentSegment(
            text="Doan dung.",
            start=3,
            end=6,
            score=95,
            asr_text="Doan dung.",
            language="vi",
        ),
    ]

    service = make_service(
        matches
    )

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
        quality_config=quality_config(),
    )

    source_report = result["report"]["source_reports"][0]

    assert source_report["skipped_entire_file"]
    assert source_report["skip_reason"] == "source_error_rate_exceeded"
    assert any(
        item["code"] == "source_error_rate_exceeded"
        for item in result["suspicious"]
    )


def test_weak_source_is_reported_and_not_written_to_metadata():

    root = ROOT / "cache" / "test_alignment_quality_weak"

    source = make_source(
        root,
        "Chi mot doan hop le.",
        duration=5,
    )

    service = make_service(
        [
            AlignmentSegment(
                text="Chi mot doan hop le.",
                start=0,
                end=3,
                score=95,
                asr_text="Chi mot doan hop le.",
                language="vi",
            )
        ]
    )

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
        quality_config=quality_config(
            min_valid_segments_per_source=3
        ),
    )

    assert result["report"]["source_reports"][0]["weak_source"]
    assert result["valid"][0]["metadata_enabled"] is False
    assert (
        root
        / "alignment"
        / "metadata.list"
    ).read_text(
        encoding="utf-8"
    ) == ""


def test_progress_payload_has_required_fields():

    service = TrainAudioPrepService()

    payload = service.emit_progress(
        "alignment",
        "file.mp3",
        1,
        2,
        0,
        "message",
        "info",
    )

    assert set(
        [
            "stage",
            "current_file",
            "current_item",
            "total_items",
            "percent",
            "elapsed_seconds",
            "estimated_remaining_seconds",
            "message",
            "level",
        ]
    ).issubset(
        payload.keys()
    )


test_long_clip_split_by_word_timestamp_and_metadata_valid_only()
test_bad_segment_is_skipped_and_processing_continues()
test_source_is_skipped_when_error_rate_exceeded()
test_weak_source_is_reported_and_not_written_to_metadata()
test_progress_payload_has_required_fields()

print("ALIGNMENT_QUALITY_TEST_OK")
