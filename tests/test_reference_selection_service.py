import json
import math
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.reference_selection_service import ReferenceSelectionService


def write_sine_wav(
    path,
    *,
    duration=2.0,
    sample_rate=2000,
    frequency=160.0,
    amplitude=0.25,
    leading_silence=0.0,
    dc_offset=0.0,
):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(duration * sample_rate)
    samples = []

    for index in range(frames):
        time = index / sample_rate
        value = (
            0.0
            if time < leading_silence
            else amplitude * math.sin(2 * math.pi * frequency * time)
        )
        value += dc_offset
        value = max(-0.999, min(0.999, value))
        samples.append(int(value * 32767))

    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(
            b"".join(
                sample.to_bytes(
                    2,
                    byteorder="little",
                    signed=True,
                )
                for sample in samples
            )
        )


def write_metadata(root, rows):
    metadata = root / "metadata.list"
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        "\n".join(
            f"{audio}|speaker-0001|vi|{transcript}"
            for audio, transcript in rows
        )
        + "\n",
        encoding="utf-8",
    )
    return metadata


def evidence_item(audio, **overrides):
    parts = Path(audio).parts
    chapter = parts[0] if parts else Path(audio).stem
    item = {
        "audio": audio,
        "id": f"evidence-{Path(audio).stem}",
        "source_audio": f"workspace/source/{chapter}.mp3",
        "source_text": f"workspace/source/{chapter}.txt",
        "match_score": 92.0,
    }
    item.update(overrides)
    return item


def test_selection_scans_metadata_authority_filters_ranks_diversifies_and_freezes(
    tmp_path,
):
    dataset_root = tmp_path / "dataset"
    rows = []

    for index in range(24):
        chapter = f"chapter-{index % 4}"
        source = f"{chapter}/source-{index % 6}"
        relative_audio = f"{source}/clip-{index:02d}.wav"
        write_sine_wav(
            dataset_root / relative_audio,
            frequency=145.0 + index,
            duration=2.0 + (index % 3) * 0.3,
        )
        rows.append(
            (
                relative_audio,
                "Đây là câu kể chuyện trung tính có đầy đủ nội dung.",
            )
        )

    duplicate_audio = "chapter-0/source-0/duplicate.wav"
    duplicate_path = dataset_root / duplicate_audio
    duplicate_path.parent.mkdir(parents=True, exist_ok=True)
    duplicate_path.write_bytes(
        (dataset_root / rows[0][0]).read_bytes()
    )
    rows.append(
        (
            duplicate_audio,
            "Đây là transcript của clip bị trùng lặp.",
        )
    )

    clipped_audio = "chapter-1/source-1/clipped.wav"
    write_sine_wav(
        dataset_root / clipped_audio,
        amplitude=0.999,
    )
    rows.append(
        (
            clipped_audio,
            "Đây là transcript của clip clipping.",
        )
    )

    empty_transcript_audio = "chapter-2/source-2/empty.wav"
    write_sine_wav(dataset_root / empty_transcript_audio)
    rows.append((empty_transcript_audio, ""))

    suspicious_audio = "chapter-3/source-3/suspicious.wav"
    write_sine_wav(dataset_root / suspicious_audio)
    rows.append(
        (
            suspicious_audio,
            "Đây là transcript của clip suspicious.",
        )
    )

    metadata = write_metadata(dataset_root, rows)
    health = tmp_path / "dataset_health.json"
    evidence_items = [
        evidence_item(audio)
        for audio, _transcript in rows
    ]
    for item in evidence_items:
        if item["audio"] == suspicious_audio:
            item["suspicious"] = True
    health.write_text(
        json.dumps(
            {
                "items": evidence_items
            }
        ),
        encoding="utf-8",
    )

    result = ReferenceSelectionService().select(
        metadata,
        tmp_path / "selection",
        dataset_health_file=health,
        top_limit=50,
        freeze_limit=20,
    )

    assert result["status"] == "READY"
    assert result["dataset_scanned"] == 28
    assert result["filter_summary"]["accepted"] == 24
    assert result["filter_summary"]["rejected"] == 4
    rejection_reasons = result["filter_summary"]["rejection_reasons"]
    assert rejection_reasons["clipping"] == 1
    assert rejection_reasons["duplicate"] >= 1
    assert rejection_reasons["suspicious"] == 1
    assert rejection_reasons["transcript_empty"] == 1

    ranking = result["ranking_manifest"]
    assert ranking["authority"]["metadata_list"] == str(metadata)
    assert ranking["authority"]["candidate_cache_used_as_authority"] is False
    assert ranking["calibration_evidence"]["applied"] is True
    assert len(result["top50"]) == 24
    assert len(result["top20"]) == 20
    assert all(
        candidate["score"]["total"] >= 0
        for candidate in result["top50"]
    )
    assert all(
        candidate["freeze_status"] == "frozen"
        and candidate["exclude_from_future_training"] is True
        for candidate in result["top20"]
    )
    assert len(
        {
            candidate["source_id"]
            for candidate in result["top20"]
        }
    ) >= 4
    assert len(
        {
            candidate["chapter_id"]
            for candidate in result["top20"]
        }
    ) == 4

    holdout_path = tmp_path / "selection" / "evaluation_holdout_manifest.json"
    ranking_path = tmp_path / "selection" / "reference_selection_manifest.json"
    report_path = tmp_path / "selection" / "selection_report.json"
    assert ranking_path.is_file()
    assert holdout_path.is_file()
    assert report_path.is_file()

    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    assert holdout["artifact_type"] == "EVALUATION_HOLDOUT"
    assert holdout["exclude_from_future_training"] is True
    assert holdout["holdout_count"] == 20
    assert [item["freeze_rank"] for item in holdout["items"]] == list(
        range(1, 21)
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["artifact_type"] == "REFERENCE_SELECTION_REPORT"
    assert report["accepted_clips"] == 24
    assert report["rejected_clips"] == 4
    assert report["top50_count"] == 24
    assert report["frozen_top20_count"] == 20
    assert report["all_frozen_excluded_from_future_training"] is True
    assert report["all_holdout_excluded_from_future_training"] is True
    assert report["evidence_coverage"]["required"]["alignment_similarity"] == {
        "present": 28,
        "missing": 0,
    }
    assert report["evidence_coverage"]["optional_warning_candidates"] == 28


def test_selection_uses_alignment_evidence_to_reject_invalid_clip(tmp_path):
    dataset_root = tmp_path / "dataset"
    audio = "chapter-a/source-a/clip.wav"
    write_sine_wav(dataset_root / audio)
    metadata = write_metadata(
        dataset_root,
        [(audio, "Transcript hợp lệ cho clip có alignment evidence.")],
    )
    alignment_manifest = tmp_path / "alignment_manifest.json"
    alignment_manifest.write_text(
        json.dumps(
            {
                "suspicious_clips": [
                    evidence_item(
                        audio,
                        status="suspicious",
                        code="similarity_too_low",
                    )
                ]
            }
        ),
        encoding="utf-8",
    )

    result = ReferenceSelectionService().select(
        metadata,
        tmp_path / "selection",
        alignment_manifest_file=alignment_manifest,
        top_limit=50,
        freeze_limit=1,
    )

    assert result["filter_summary"]["accepted"] == 0
    assert result["filter_summary"]["rejection_reasons"]["suspicious"] == 1
    assert result["top50"] == []
    assert result["top20"] == []


def test_selection_resolves_production_cache_relative_paths(tmp_path, monkeypatch):
    app_root = tmp_path / "app"
    metadata_root = app_root / "cache" / "run" / "alignment"
    audio = "cache/run/alignment/clips/clip.wav"
    write_sine_wav(app_root / audio)
    metadata = write_metadata(
        metadata_root,
        [(audio, "Transcript hop le cho duong dan cache production.")],
    )
    alignment_manifest = tmp_path / "alignment_manifest.json"
    alignment_manifest.write_text(
        json.dumps(
            {
                "valid_clips": [
                    {
                        "audio": audio,
                        "id": "clip-cache-production",
                        "source_audio": "workspace/Thu Minh/5137.mp3",
                        "source_text": "workspace/Thu Minh/5137.txt",
                        "match_score": 88.5,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(app_root)
    result = ReferenceSelectionService().select(
        metadata,
        tmp_path / "selection",
        alignment_manifest_file=alignment_manifest,
        top_limit=1,
        freeze_limit=1,
    )

    assert result["filter_summary"]["accepted"] == 1
    assert result["filter_summary"]["rejected"] == 0
    assert result["top20"][0]["audio"] == audio
    assert result["top20"][0]["source_id"] == "workspace/Thu Minh/5137.mp3"
    assert result["top20"][0]["chapter_id"] == "5137"
    assert result["top20"][0]["exclude_from_future_training"] is True
    assert (
        result["top20"][0]["evidence"]["alignment_similarity"] == 88.5
    )


def test_selection_rejects_missing_required_evidence_and_warns_optional(tmp_path):
    dataset_root = tmp_path / "dataset"
    accepted_audio = "chapter-a/source-a/accepted.wav"
    missing_audio = "chapter-b/source-b/missing_source_text.wav"
    write_sine_wav(dataset_root / accepted_audio)
    write_sine_wav(dataset_root / missing_audio)
    metadata = write_metadata(
        dataset_root,
        [
            (accepted_audio, "Transcript hop le cho evidence integrity."),
            (missing_audio, "Transcript hop le nhung thieu required evidence."),
        ],
    )
    evidence = tmp_path / "evidence.json"
    evidence.write_text(
        json.dumps(
            {
                "items": [
                    evidence_item(accepted_audio),
                    {
                        "audio": missing_audio,
                        "id": "missing-source-text",
                        "source_audio": "workspace/source/missing.mp3",
                        "match_score": 91.0,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = ReferenceSelectionService().select(
        metadata,
        tmp_path / "selection",
        alignment_manifest_file=evidence,
        top_limit=1,
        freeze_limit=1,
    )

    reasons = result["filter_summary"]["rejection_reasons"]
    report = result["selection_report"]
    assert result["filter_summary"]["accepted"] == 1
    assert result["filter_summary"]["rejected"] == 1
    assert reasons["required_evidence_missing_source_text"] == 1
    assert report["evidence_coverage"]["required"]["source_text"] == {
        "present": 1,
        "missing": 1,
    }
    assert report["evidence_coverage"]["optional_warning_candidates"] == 2


def test_selection_rejects_audit_cases_for_reference_selection(tmp_path, monkeypatch):
    dataset_root = tmp_path / "dataset"
    rows = []
    audio_files = [
        "chapter-a/source-a/clean.wav",
        "chapter-a/source-a/duplicate.wav",
        "chapter-b/source-b/suspicious.wav",
        "chapter-c/source-c/invalid.wav",
        "chapter-d/source-d/clipped.wav",
        "chapter-e/source-e/empty_transcript.wav",
        "chapter-f/source-f/ai_generated.wav",
        "chapter-g/source-g/multi_speaker.wav",
        "chapter-h/source-h/noise_high.wav",
    ]

    for index, audio in enumerate(audio_files):
        write_sine_wav(
            dataset_root / audio,
            frequency=130.0 + index * 11.0,
        )

    (dataset_root / "chapter-a/source-a/duplicate.wav").write_bytes(
        (dataset_root / "chapter-a/source-a/clean.wav").read_bytes()
    )
    write_sine_wav(
        dataset_root / "chapter-d/source-d/clipped.wav",
        amplitude=0.999,
        frequency=173.0,
    )

    for audio in audio_files:
        transcript = (
            ""
            if audio.endswith("empty_transcript.wav")
            else "Transcript hop le cho fixture audit reference selection."
        )
        rows.append((audio, transcript))

    metadata = write_metadata(dataset_root, rows)
    evidence = tmp_path / "evidence.json"
    evidence_items = []
    evidence_flags = {
        "chapter-b/source-b/suspicious.wav": {"suspicious": True},
        "chapter-c/source-c/invalid.wav": {"invalid": True},
        "chapter-f/source-f/ai_generated.wav": {"ai_generated": True},
        "chapter-g/source-g/multi_speaker.wav": {"multiple_speakers": True},
    }
    for audio in audio_files:
        evidence_items.append(evidence_item(audio, **evidence_flags.get(audio, {})))
    evidence.write_text(
        json.dumps(
            {
                "items": evidence_items
            }
        ),
        encoding="utf-8",
    )

    service = ReferenceSelectionService()
    original_audio_metrics = service.audio_metrics

    def audio_metrics_with_noise_case(audio_path):
        metrics = original_audio_metrics(audio_path)
        if audio_path.name == "noise_high.wav":
            metrics["harmonic_noise_indicator"] = 0.01
        return metrics

    monkeypatch.setattr(service, "audio_metrics", audio_metrics_with_noise_case)

    result = service.select(
        metadata,
        tmp_path / "selection",
        alignment_manifest_file=evidence,
        top_limit=1,
        freeze_limit=1,
    )

    reasons = result["filter_summary"]["rejection_reasons"]
    assert result["dataset_scanned"] == 9
    assert result["filter_summary"]["accepted"] == 1
    assert result["filter_summary"]["rejected"] == 8
    assert reasons["duplicate"] == 1
    assert reasons["suspicious"] == 1
    assert reasons["invalid"] == 1
    assert reasons["clipping"] == 1
    assert reasons["transcript_empty"] == 1
    assert reasons["ai_generated"] == 1
    assert reasons["multiple_speakers"] == 1
    assert reasons["noise_high"] == 1


def test_selection_flags_and_penalizes_boundary_fragments(tmp_path):
    dataset_root = tmp_path / "dataset"
    complete_audio = "chapter-a/source-a/complete.wav"
    fragment_audio = "chapter-b/source-b/fragment.wav"
    write_sine_wav(dataset_root / complete_audio)
    write_sine_wav(
        dataset_root / fragment_audio,
        frequency=190.0,
    )
    metadata = write_metadata(
        dataset_root,
        [
            (
                complete_audio,
                "Transcript hop le co cau day du ket thuc ro rang.",
            ),
            (
                fragment_audio,
                "Transcript dang do va ket thuc bang dau ba cham...",
            ),
        ],
    )
    evidence = tmp_path / "evidence.json"
    evidence.write_text(
        json.dumps(
            {
                "items": [
                    evidence_item(complete_audio),
                    evidence_item(fragment_audio),
                ]
            }
        ),
        encoding="utf-8",
    )

    result = ReferenceSelectionService().select(
        metadata,
        tmp_path / "selection",
        alignment_manifest_file=evidence,
        top_limit=2,
        freeze_limit=2,
    )

    by_audio = {
        item["audio"]: item
        for item in result["top50"]
    }
    fragment = by_audio[fragment_audio]
    complete = by_audio[complete_audio]
    assert fragment["text_quality_flags"]["ends_with_ellipsis"] is True
    assert fragment["text_quality_flags"]["boundary_fragment"] is True
    assert (
        fragment["score"]["components"]["transcript_quality"]
        < complete["score"]["components"]["transcript_quality"]
    )


if __name__ == "__main__":
    test_selection_scans_metadata_authority_filters_ranks_diversifies_and_freezes(
        Path("cache/test_reference_selection_service")
    )
    print("REFERENCE_SELECTION_SERVICE_TEST_OK")
