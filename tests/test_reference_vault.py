import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.reference_vault_service import ReferenceVaultService  # noqa: E402


def test_import_mp3_wav_txt_and_deduplicate(tmp_path):

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    mp3 = tmp_path / "ref.mp3"
    wav = tmp_path / "ref.wav"
    txt = tmp_path / "ref.txt"

    mp3.write_bytes(
        b"mp3-data"
    )
    wav.write_bytes(
        b"wav-data"
    )
    txt.write_text(
        "Xin chao",
        encoding="utf-8",
    )

    mp3_asset = vault.import_file(
        mp3,
        "speaker_reference_audio",
    )[
        "asset"
    ]

    wav_asset = vault.import_file(
        wav,
        "training_reference_audio",
    )[
        "asset"
    ]

    txt_asset = vault.import_file(
        txt,
        "speaker_reference_text",
    )[
        "asset"
    ]

    assert not Path(
        mp3_asset.managed_relative_path
    ).is_absolute()
    assert not Path(
        wav_asset.managed_relative_path
    ).is_absolute()
    assert not Path(
        txt_asset.managed_relative_path
    ).is_absolute()
    assert mp3_asset.checksum
    assert wav_asset.checksum
    assert txt_asset.checksum

    again = vault.import_file(
        mp3,
        "speaker_reference_audio",
    )

    assert again["deduplicated"]
    assert again["asset"].asset_id == mp3_asset.asset_id


def test_same_name_different_content_creates_different_asset(tmp_path):

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    one = tmp_path / "a" / "ref.mp3"
    two = tmp_path / "b" / "ref.mp3"

    one.parent.mkdir()
    two.parent.mkdir()

    one.write_bytes(
        b"one"
    )
    two.write_bytes(
        b"two"
    )

    asset_one = vault.import_file(
        one,
        "speaker_reference_audio",
    )[
        "asset"
    ]
    asset_two = vault.import_file(
        two,
        "speaker_reference_audio",
    )[
        "asset"
    ]

    assert asset_one.asset_id != asset_two.asset_id


def test_missing_source_does_not_break_managed_asset(tmp_path):

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    source = tmp_path / "ref.txt"
    source.write_text(
        "Van ban tham chieu",
        encoding="utf-8",
    )

    asset = vault.import_file(
        source,
        "training_reference_text",
    )[
        "asset"
    ]

    source.unlink()

    resolved = vault.resolve_asset_path(
        asset.asset_id
    )

    assert resolved.exists()
    assert vault.verify_asset(
        asset.asset_id
    )[
        "ok"
    ]


def test_relink_checksum_mismatch_warns(tmp_path):

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    source = tmp_path / "ref.txt"
    source.write_text(
        "A",
        encoding="utf-8",
    )

    asset = vault.import_file(
        source,
        "training_reference_text",
    )[
        "asset"
    ]

    replacement = tmp_path / "replacement.txt"
    replacement.write_text(
        "B",
        encoding="utf-8",
    )

    result = vault.relink_external(
        asset.asset_id,
        replacement,
    )

    assert not result["ok"]
    assert result["warning"] == "checksum_mismatch"
