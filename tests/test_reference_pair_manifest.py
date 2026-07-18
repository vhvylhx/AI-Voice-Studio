import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.audio_text_pair_service import AudioTextPairService  # noqa: E402
from services.reference_vault_service import ReferenceVaultService  # noqa: E402


def test_audio_text_pair_persistent_manifest_survives_source_move(tmp_path):

    source = tmp_path / "source"
    source.mkdir()

    audio = source / "001.mp3"
    text = source / "001.txt"

    audio.write_bytes(
        b"audio"
    )
    text.write_text(
        "Xin chao",
        encoding="utf-8",
    )

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    result = AudioTextPairService(
        vault_service=vault
    ).match_folder(
        source,
        persist_manifest=True,
        manifest_dir=tmp_path / "manifests",
        source_project_id="project_000001",
    )

    manifest = result["manifest"]

    assert manifest["manifest_id"].startswith(
        "pair_manifest_"
    )
    assert manifest["pairs"][0]["audio_asset_id"]
    assert manifest["pairs"][0]["text_asset_id"]
    assert Path(
        manifest["manifest_path"]
    ).exists()

    audio.unlink()
    text.unlink()

    audio_path = vault.resolve_asset_path(
        manifest["pairs"][0]["audio_asset_id"]
    )
    text_path = vault.resolve_asset_path(
        manifest["pairs"][0]["text_asset_id"]
    )

    assert audio_path.exists()
    assert text_path.exists()
