import json
import wave
from pathlib import Path

import pytest

from services.voice_preview_benchmark_service import VoicePreviewBenchmarkService


BENCHMARK_TRANSCRIPT = (
    "Hôm nay trời trong xanh và gió nhẹ "
    "chúng ta cùng lắng nghe một câu chuyện bình yên"
)


def create_references(tmp_path):
    references = []

    for index in range(1, 21):
        audio_path = tmp_path / f"source_{index:03d}.wav"
        transcript_path = tmp_path / f"source_{index:03d}.txt"

        audio_path.write_bytes(b"reference-audio")
        transcript_path.write_text(
            f"Nội dung tham chiếu {index}.",
            encoding="utf-8",
        )

        references.append(
            {
                "reference_id": f"reference-{index:03d}",
                "audio_path": str(audio_path),
                "transcript_path": str(transcript_path),
                "clean": True,
                "transcript_correct": True,
                "not_duplicate": True,
                "not_suspicious": True,
                "not_ai_generated": True,
                "not_clipping": True,
                "no_large_noise": True,
            }
        )

    return references


def prepare_round(tmp_path, round_id="Round01"):
    service = VoicePreviewBenchmarkService()
    result = service.prepare_round(
        output_root=tmp_path / "benchmark",
        voice_id="voice-001",
        benchmark_transcript=BENCHMARK_TRANSCRIPT,
        references=create_references(tmp_path),
        round_id=round_id,
    )
    return service, result


def test_prepare_round_creates_twenty_pair_contracts(tmp_path):
    service, result = prepare_round(tmp_path)

    assert result["status"] == "PREPARED"
    assert result["pair_count"] == 20

    round_dir = Path(result["round_dir"])
    round_manifest = json.loads(
        (round_dir / "benchmark_manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert round_manifest["pair_count"] == 20
    assert [pair["pair_id"] for pair in round_manifest["pairs"]] == [
        f"pair_{index:03d}"
        for index in range(1, 21)
    ]

    for index in range(1, 21):
        pair_dir = round_dir / f"pair_{index:03d}"
        pair_manifest = service.load_pair_manifest(
            pair_dir / "pair_manifest.json"
        )

        assert (pair_dir / "reference.wav").is_file()
        assert (
            pair_dir / "reference_transcript.txt"
        ).read_text(encoding="utf-8")
        assert (
            pair_dir / "new_transcript.txt"
        ).read_text(encoding="utf-8") == BENCHMARK_TRANSCRIPT
        assert pair_manifest["approval_state"] == "UNKNOWN"
        assert (
            pair_manifest["previews"]["same_preview"]["file"]
            == "same_preview_v1.wav"
        )
        assert (
            pair_manifest["previews"]["new_preview"]["file"]
            == "new_preview_v1.wav"
        )
        assert (
            pair_manifest["previews"]["same_preview"]["status"]
            == "UNAVAILABLE"
        )
        assert (
            pair_manifest["previews"]["new_preview"]["status"]
            == "UNAVAILABLE"
        )


def test_round_versioning_uses_new_preview_names_without_overwrite(tmp_path):
    service, round_one = prepare_round(tmp_path, "Round01")

    round_two = service.prepare_round(
        output_root=tmp_path / "benchmark",
        voice_id="voice-001",
        benchmark_transcript=BENCHMARK_TRANSCRIPT,
        references=create_references(tmp_path),
        round_id="Round02",
    )

    pair_one_round_two = service.load_pair_manifest(
        Path(round_two["round_dir"])
        / "pair_001"
        / "pair_manifest.json"
    )

    assert (
        pair_one_round_two["previews"]["same_preview"]["file"]
        == "same_preview_v2.wav"
    )
    assert (
        pair_one_round_two["previews"]["new_preview"]["file"]
        == "new_preview_v2.wav"
    )

    with pytest.raises(FileExistsError):
        service.prepare_round(
            output_root=tmp_path / "benchmark",
            voice_id="voice-001",
            benchmark_transcript=BENCHMARK_TRANSCRIPT,
            references=create_references(tmp_path),
            round_id="Round01",
        )

    assert Path(round_one["round_dir"]).is_dir()


@pytest.mark.parametrize(
    "approval_state",
    ("UNKNOWN", "KEEP", "MAYBE", "REJECT", "APPROVED"),
)
def test_pair_approval_states_are_supported(tmp_path, approval_state):
    service, result = prepare_round(tmp_path)

    pair_manifest_path = (
        Path(result["round_dir"])
        / "pair_001"
        / "pair_manifest.json"
    )
    updated = service.update_approval(
        pair_manifest_path,
        approval_state,
    )

    assert updated["approval_state"] == approval_state
    assert service.load_pair_manifest(
        pair_manifest_path
    )["approval_state"] == approval_state


def test_manifest_validation_rejects_generated_preview_status(tmp_path):
    service, result = prepare_round(tmp_path)
    pair_manifest_path = (
        Path(result["round_dir"])
        / "pair_001"
        / "pair_manifest.json"
    )
    manifest = json.loads(
        pair_manifest_path.read_text(encoding="utf-8")
    )
    manifest["previews"]["same_preview"]["status"] = "READY"
    pair_manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Foundation"):
        service.load_pair_manifest(pair_manifest_path)


def test_training_lock_requires_an_approved_pair(tmp_path):
    service, result = prepare_round(tmp_path)
    manifest_path = result["manifest_path"]

    blocked = service.training_status(manifest_path)

    assert blocked["training_allowed"] is False
    assert blocked["status"] == "PENDING_APPROVAL"
    assert blocked["approved_pair_count"] == 0

    service.update_approval(
        Path(result["round_dir"])
        / "pair_010"
        / "pair_manifest.json",
        "APPROVED",
    )

    allowed = service.training_status(manifest_path)

    assert allowed["training_allowed"] is True
    assert allowed["status"] == "READY"
    assert allowed["approved_pair_count"] == 1


def test_generate_previews_creates_and_records_all_preview_evidence(tmp_path):
    service, prepared = prepare_round(tmp_path)
    requests = []

    def generate_fixture_wav(request):
        requests.append(request)
        with wave.open(request["output_path"], "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48000)
            output.writeframes(
                (1200).to_bytes(
                    2,
                    byteorder="little",
                    signed=True,
                )
                * 480
            )

    profile = {
        "app_root": str(tmp_path),
        "runtime_python": str(tmp_path / "runtime.exe"),
        "model_root": str(tmp_path / "model"),
        "codec_root": str(tmp_path / "codec"),
        "backend": "CPU_ONNX",
        "sample_rate": 48000,
    }
    result = service.generate_previews(
        prepared["manifest_path"],
        profile,
        generation_runner=generate_fixture_wav,
    )

    assert result["status"] == "READY"
    assert result["pair_count"] == 20
    assert len(requests) == 40
    assert {
        request["preview_name"]
        for request in requests
    } == {"same_preview", "new_preview"}

    round_dir = Path(prepared["round_dir"])
    round_manifest = json.loads(
        Path(prepared["manifest_path"]).read_text(
            encoding="utf-8"
        )
    )
    assert round_manifest["generation_status"] == "READY"
    assert round_manifest["runtime_profile"] == profile

    for index in range(1, 21):
        pair_dir = round_dir / f"pair_{index:03d}"
        pair_manifest = service.load_pair_manifest(
            pair_dir / "pair_manifest.json",
            allow_generated=True,
        )
        for name in ("same_preview", "new_preview"):
            preview = pair_manifest["previews"][name]
            assert preview["status"] == "READY"
            assert preview["checksum"]
            assert preview["duration"] > 0
            assert preview["generation_timestamp"]
            assert preview["runtime_profile"] == profile
            assert preview["validation"]["status"] == "PASS"
            assert preview["validation"]["sample_rate"] == 48000
            assert preview["validation"]["channels"] == 1
            assert preview["validation"]["nonsilent"] is True
            assert (pair_dir / preview["file"]).is_file()


def test_generate_previews_rejects_existing_output_without_overwrite(tmp_path):
    service, prepared = prepare_round(tmp_path)

    def generate_fixture_wav(request):
        with wave.open(request["output_path"], "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48000)
            output.writeframes(
                (1).to_bytes(
                    2,
                    byteorder="little",
                    signed=True,
                )
            )

    profile = {
        "app_root": str(tmp_path),
        "runtime_python": str(tmp_path / "runtime.exe"),
        "model_root": str(tmp_path / "model"),
        "codec_root": str(tmp_path / "codec"),
    }
    service.generate_previews(
        prepared["manifest_path"],
        profile,
        generation_runner=generate_fixture_wav,
    )
    output_path = (
        Path(prepared["round_dir"])
        / "pair_001"
        / "same_preview_v1.wav"
    )
    original = output_path.read_bytes()

    with pytest.raises(FileExistsError, match="ghi de"):
        service.generate_previews(
            prepared["manifest_path"],
            profile,
            generation_runner=generate_fixture_wav,
        )

    assert output_path.read_bytes() == original


def create_frozen_top20_manifest(tmp_path):
    top20 = []
    for index in range(1, 21):
        audio_path = tmp_path / f"top20_{index:03d}.wav"
        with wave.open(str(audio_path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(32000)
            output.writeframes(
                (index).to_bytes(
                    2,
                    byteorder="little",
                    signed=True,
                )
                * (32000 * 6)
            )
        top20.append(
            {
                "clip_id": f"ref-{index:03d}",
                "audio_path": str(audio_path),
                "audio_sha256": service_sha256(audio_path),
                "speaker": "Thu Minh",
                "language": "vi",
                "transcript": (
                    "Day la transcript preview hop le cho mot cap "
                    f"doi chieu so {index}"
                ),
                "source_id": f"workspace/Thu Minh/{index}.mp3",
                "chapter_id": str(index),
                "freeze_rank": index,
                "freeze_status": "frozen",
                "exclude_from_future_training": True,
                "evidence": {
                    "id": f"clip-{index:03d}",
                },
            }
        )
    manifest_path = tmp_path / "reference_selection_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifact_type": "REFERENCE_SELECTION",
                "top20": top20,
                "top50": list(top20),
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


def service_sha256(path):
    return VoicePreviewBenchmarkService().sha256(path)


def test_avs016_sprint6_generates_ai_and_benchmark_report(tmp_path):
    service = VoicePreviewBenchmarkService()
    frozen_manifest = create_frozen_top20_manifest(tmp_path)
    prepared = service.prepare_avs016_sprint6_round(
        output_root=tmp_path / "preview_generation",
        voice_id="0001",
        frozen_top20_manifest_path=frozen_manifest,
        round_id="Round01",
    )
    requests = []

    def generate_fixture_wav(request):
        requests.append(request)
        sample = (
            1600
            if request["preview_name"] == "ai_preview"
            else 900
        )
        with wave.open(request["output_path"], "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48000)
            output.writeframes(
                sample.to_bytes(
                    2,
                    byteorder="little",
                    signed=True,
                )
                * 480
            )

    profile = {
        "app_root": str(tmp_path),
        "runtime_python": str(tmp_path / "runtime.exe"),
        "model_root": str(tmp_path / "model"),
        "codec_root": str(tmp_path / "codec"),
        "backend": "CPU_ONNX",
        "sample_rate": 48000,
    }
    result = service.generate_avs016_sprint6_previews(
        prepared["manifest_path"],
        profile,
        generation_runner=generate_fixture_wav,
    )

    assert result["status"] == "READY"
    assert result["pair_count"] == 20
    assert result["preview_count"] == 40
    assert len(requests) == 40
    assert {
        request["preview_name"]
        for request in requests
    } == {"ai_preview", "benchmark_preview"}

    report = json.loads(
        Path(result["report_path"]).read_text(encoding="utf-8")
    )
    assert report["artifact_type"] == "AVS016_PREVIEW_REPORT"
    assert report["status"] == "READY"
    assert report["ai_preview_count"] == 20
    assert report["benchmark_preview_count"] == 20
    assert report["transcript_identity"]["status"] == "PASS"

    round_dir = Path(prepared["round_dir"])
    for index in range(1, 21):
        pair_manifest = service.load_avs016_pair_manifest(
            round_dir
            / f"pair_{index:03d}"
            / "pair_manifest.json",
            allow_generated=True,
        )
        assert pair_manifest["preview_id"] == f"preview_{index:03d}"
        assert pair_manifest["reference"]["reference_id"]
        assert pair_manifest["transcript"]["file"] == "transcript.txt"
        assert pair_manifest["ai_preview"]["status"] == "READY"
        assert pair_manifest["benchmark_preview"]["status"] == "READY"
        assert (
            pair_manifest["ai_preview"]["transcript_sha256"]
            == pair_manifest["benchmark_preview"]["transcript_sha256"]
        )
        assert (
            round_dir
            / f"pair_{index:03d}"
            / pair_manifest["ai_preview"]["file"]
        ).is_file()
        assert (
            round_dir
            / f"pair_{index:03d}"
            / pair_manifest["benchmark_preview"]["file"]
        ).is_file()


def test_avs016_preflight_blocks_transcript_duration_outlier(tmp_path):
    service = VoicePreviewBenchmarkService()
    audio_path = tmp_path / "reference.wav"
    with wave.open(str(audio_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(32000)
        output.writeframes(
            (100).to_bytes(
                2,
                byteorder="little",
                signed=True,
            )
            * (32000 * 6)
        )

    preflight = service.reference_preflight_integrity(
        reference_id="000070_005_002",
        transcript=" ".join(["ratdai"] * 60),
        audio_path=audio_path,
    )

    assert preflight["status"] == "BLOCK"
    assert "reference_chars_per_second_too_high" in preflight["blockers"]


def test_avs016_transcript_normalization_preserves_source_text():
    service = VoicePreviewBenchmarkService()

    result = service.normalize_preview_transcript('  " "Noi dung can doc.')

    assert result["normalized_text"] == "Noi dung can doc."
    assert result["source_text"] == '  " "Noi dung can doc.'
    assert result["normalization"]["source_preserved"] is True
    assert result["normalization"]["status"] == "NORMALIZED"


def test_avs016_sprint8_replaces_blocked_pair_from_top50(tmp_path):
    service = VoicePreviewBenchmarkService()
    source_manifest_path = create_frozen_top20_manifest(tmp_path)
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    blocked = manifest["top20"][1]
    blocked["transcript"] = " ".join(["ratdai"] * 60)
    blocked["evidence"]["id"] = "000070_005_002"

    replacement_audio = tmp_path / "replacement.wav"
    with wave.open(str(replacement_audio), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(32000)
        output.writeframes(
            (111).to_bytes(
                2,
                byteorder="little",
                signed=True,
            )
            * (32000 * 6)
        )
    replacement = dict(manifest["top20"][0])
    replacement.update(
        {
            "clip_id": "ref-replacement",
            "audio": str(replacement_audio),
            "audio_path": str(replacement_audio),
            "audio_sha256": service.sha256(replacement_audio),
            "transcript": "Day la transcript thay the hop le cho Round02.",
            "source_id": "workspace/source/replacement.mp3",
            "chapter_id": "replacement",
            "freeze_rank": None,
            "evidence": {"id": "000015_022_001"},
        }
    )
    manifest["top50"].append(replacement)
    source_manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    result = service.create_avs016_sprint8_reference_manifest(
        source_manifest_path,
        tmp_path / "sprint8",
        {"000070_005_002"},
        review_evidence_paths=["review_inputs/avs016_round01/x.csv"],
    )

    adjusted = json.loads(
        Path(result["manifest_path"]).read_text(encoding="utf-8")
    )
    top20_ids = [
        item["evidence"]["id"]
        for item in adjusted["top20"]
    ]
    assert "000070_005_002" not in top20_ids
    assert top20_ids[1] == "000015_022_001"
    assert adjusted["top20"][1]["freeze_rank"] == 2
    assert adjusted["sprint8_review_integration"]["training_approval"] is False


def test_avs016_pair_manifest_contains_preflight_and_audit(tmp_path):
    service = VoicePreviewBenchmarkService()
    frozen_manifest = create_frozen_top20_manifest(tmp_path)
    prepared = service.prepare_avs016_sprint6_round(
        output_root=tmp_path / "preview_generation",
        voice_id="0001",
        frozen_top20_manifest_path=frozen_manifest,
        round_id="Round02",
    )

    pair_manifest = service.load_avs016_pair_manifest(
        Path(prepared["round_dir"])
        / "pair_001"
        / "pair_manifest.json",
    )

    assert pair_manifest["reference"]["conditioning_reference_id"]
    assert pair_manifest["reference"]["conditioning_reference_checksum"]
    assert pair_manifest["reference"]["preflight_integrity"]["status"] in (
        "PASS",
        "REVIEW",
    )
    assert pair_manifest["transcript"]["source_sha256"]
    assert pair_manifest["transcript"]["normalization"]["source_preserved"]
    assert pair_manifest["ai_preview"]["benchmark_voice_profile"]
    assert "temperature" in pair_manifest["ai_preview"]["inference_parameters"]
    assert "comparison_reason" in pair_manifest["benchmark_preview"]


@pytest.mark.parametrize(
    "channels,sample_rate,sample_width,frames,error",
    (
        (1, 48000, 2, 0, "duration"),
        (2, 48000, 2, 1, "mono"),
        (1, 32000, 2, 1, "sample rate"),
        (1, 48000, 1, 1, "PCM16"),
        (1, 48000, 2, 1, "im lang"),
    ),
)
def test_preview_wav_validation_rejects_invalid_audio(
    tmp_path,
    channels,
    sample_rate,
    sample_width,
    frames,
    error,
):
    path = tmp_path / "invalid.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(sample_width)
        output.setframerate(sample_rate)
        output.writeframes(
            b"\x00" * channels * sample_width * frames
        )

    with pytest.raises(ValueError, match=error):
        VoicePreviewBenchmarkService().validate_preview_wav(path)


def test_preview_wav_validation_rejects_corrupt_audio(tmp_path):
    path = tmp_path / "corrupt.wav"
    path.write_bytes(b"not-a-valid-wav")

    with pytest.raises(ValueError, match="corrupt"):
        VoicePreviewBenchmarkService().validate_preview_wav(path)


def test_reference_selection_requires_eligible_references(tmp_path):
    service = VoicePreviewBenchmarkService()
    references = create_references(tmp_path)
    references[0]["not_ai_generated"] = False

    with pytest.raises(ValueError, match="20 reference"):
        service.select_references(references)


@pytest.mark.parametrize(
    "transcript",
    (
        "Câu này có số 123 trong nội dung để kiểm tra.",
        "Câu này có dấu chấm.",
        "Hello đây là câu kiểm tra không hợp lệ",
    ),
)
def test_benchmark_transcript_rejects_forbidden_content(transcript):
    with pytest.raises(ValueError):
        VoicePreviewBenchmarkService().validate_benchmark_transcript(
            transcript
        )
