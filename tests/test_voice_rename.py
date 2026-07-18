import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.voice_service import VoiceService  # noqa: E402


def test_voice_rename_keeps_id_reference_and_variants(tmp_path):

    service = VoiceService()
    service._root = tmp_path / "voices"
    service._root.mkdir()

    voice = service.create(
        "Thu Minh"
    )

    voice.config.reference_audio = "ref.wav"
    voice.config.reference_text = "Xin chao"
    service.save(
        voice
    )

    renamed = service.rename(
        "Thu Minh",
        "  Thu Minh Mới  ",
    )

    loaded = service.load(
        "Thu Minh Mới"
    )

    assert renamed.id == voice.id
    assert loaded.id == voice.id
    assert loaded.config.reference_audio == "ref.wav"
    assert loaded.config.reference_text == "Xin chao"
    assert loaded.variants[0]["id"] == "default"


def test_voice_rename_rejects_invalid_and_duplicate(tmp_path):

    service = VoiceService()
    service._root = tmp_path / "voices"
    service._root.mkdir()

    service.create(
        "A"
    )
    service.create(
        "B"
    )

    try:

        service.rename(
            "A",
            "",
        )

        assert False

    except ValueError as exc:

        assert "voice_name_required" in str(
            exc
        )

    try:

        service.rename(
            "A",
            "B",
        )

        assert False

    except ValueError as exc:

        assert "voice_name_duplicate" in str(
            exc
        )
