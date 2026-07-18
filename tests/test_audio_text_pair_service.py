import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.audio_text_pair_service import AudioTextPairService  # noqa: E402


def test_pair_mp3_wav_txt_and_missing_duplicate(tmp_path):

    (tmp_path / "001.mp3").write_bytes(
        b"a"
    )
    (tmp_path / "001.txt").write_text(
        "text",
        encoding="utf-8",
    )
    (tmp_path / "002.wav").write_bytes(
        b"a"
    )
    (tmp_path / "003.txt").write_text(
        "text",
        encoding="utf-8",
    )
    (tmp_path / "dup.mp3").write_bytes(
        b"a"
    )
    (tmp_path / "dup.wav").write_bytes(
        b"a"
    )

    result = AudioTextPairService().match_folder(
        tmp_path
    )

    assert result["summary"]["matched"] == 1

    codes = {
        item["code"]
        for item in result["errors"]
    }

    assert "missing_text" in codes
    assert "missing_audio" in codes
    assert "duplicate_stem" in codes


def test_pair_order_is_stable(tmp_path):

    for name in [
        "b.mp3",
        "a.mp3",
        "b.txt",
        "a.txt",
    ]:

        (tmp_path / name).write_text(
            "x",
            encoding="utf-8",
        )

    result = AudioTextPairService().match_folder(
        tmp_path
    )

    assert [
        item["stem"]
        for item in result["pairs"]
    ] == [
        "a",
        "b",
    ]
