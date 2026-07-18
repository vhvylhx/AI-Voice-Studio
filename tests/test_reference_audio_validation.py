import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.reference_audio_validation_service import (  # noqa: E402
    ReferenceAudioValidationService,
)


def test_reference_audio_file_validation(tmp_path):

    service = ReferenceAudioValidationService()

    wav = tmp_path / "ref.wav"
    wav.write_bytes(
        b"RIFF"
    )

    assert service.validate_file(
        wav
    )["ok"]

    missing = service.validate_file(
        tmp_path / "missing.wav"
    )

    assert missing["ok"] is False
    assert missing["messages"][0]["code"] == "audio_missing"

    bad = tmp_path / "ref.txt"
    bad.write_text(
        "x",
        encoding="utf-8",
    )

    assert service.validate_file(
        bad
    )["messages"][0]["code"] == "audio_extension_unsupported"


def test_reference_audio_folder_validation(tmp_path):

    service = ReferenceAudioValidationService()

    empty = service.validate_folder(
        tmp_path
    )

    assert empty["ok"] is False
    assert empty["messages"][0]["code"] == "folder_empty"

    (tmp_path / "a.mp3").write_bytes(
        b"a"
    )

    assert service.validate_folder(
        tmp_path
    )["ok"]


def test_reference_text_required(tmp_path):

    wav = tmp_path / "ref.wav"
    wav.write_bytes(
        b"RIFF"
    )

    result = ReferenceAudioValidationService().validate_file(
        wav,
        transcript_required=True,
    )

    assert any(
        item["code"] == "reference_text_required"
        for item in result["messages"]
    )
