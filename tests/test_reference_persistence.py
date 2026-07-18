import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.training_reference_config import (  # noqa: E402
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_VOICE_DEFAULT,
    TrainingReferenceConfig,
)
from models.voice_config import VoiceConfig  # noqa: E402
from models.voice_model import VoiceModel  # noqa: E402
from services.project_service import ProjectService  # noqa: E402
from services.reference_vault_service import ReferenceVaultService  # noqa: E402
from services.training_reference_resolver import TrainingReferenceResolver  # noqa: E402


def test_speaker_reference_resolves_by_asset_id_when_legacy_missing(tmp_path):

    source = tmp_path / "ref.wav"
    source.write_bytes(
        b"audio"
    )

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    asset = vault.import_file(
        source,
        "speaker_reference_audio",
    )[
        "asset"
    ]

    source.unlink()

    config = TrainingReferenceConfig(
        reference_mode=REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
        speaker_reference_mode=SPEAKER_REFERENCE_SELECTED_FILE,
        speaker_reference_asset_id=asset.asset_id,
        speaker_reference_audio=str(
            source
        ),
    )

    resolved = TrainingReferenceResolver(
        vault_service=vault
    ).resolve(
        config
    )

    assert resolved["state"] == "valid"
    assert resolved["speaker_reference"]["audio_asset_id"] == asset.asset_id
    assert Path(
        resolved["speaker_reference"]["audio"]
    ).exists()


def test_legacy_voice_reference_still_loads():

    config = VoiceConfig.from_dict(
        {
            "reference_audio": "legacy.wav",
            "reference_text": "Xin chao",
        }
    )

    assert config.speaker_reference["audio_path"] == "legacy.wav"
    assert config.speaker_reference["text"] == "Xin chao"


def test_voice_default_reference_uses_asset_id_after_rename(tmp_path):

    source = tmp_path / "ref.wav"
    source.write_bytes(
        b"audio"
    )

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    asset = vault.import_file(
        source,
        "speaker_reference_audio",
    )[
        "asset"
    ]

    voice_config = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "reference_audio": str(
                source
            ),
            "speaker_reference": {
                "audio_asset_id": asset.asset_id,
            },
        }
    )

    voice = VoiceModel(
        name="New Name",
        path=tmp_path / "voice",
        avatar=tmp_path / "voice" / "avatar.png",
        preview=tmp_path / "voice" / "preview.wav",
        config=voice_config,
    )

    resolved = TrainingReferenceResolver(
        vault_service=vault
    ).resolve(
        TrainingReferenceConfig(
            reference_mode=REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            speaker_reference_mode=SPEAKER_REFERENCE_VOICE_DEFAULT,
        ),
        voice=voice,
    )

    assert Path(
        resolved["speaker_reference"]["audio"]
    ).exists()


def test_project_rename_duplicate_archive_do_not_remove_reference(tmp_path):

    service = ProjectService()
    service.root = tmp_path / "projects"
    service.root.mkdir()

    project = service.create(
        "Ref Project"
    )

    source = tmp_path / "ref.txt"
    source.write_text(
        "text",
        encoding="utf-8",
    )

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )
    asset = vault.import_file(
        source,
        "training_reference_text",
        source_project_id=project.id,
    )[
        "asset"
    ]

    renamed = service.rename(
        project.id,
        "Ref Project Renamed",
    )
    duplicate = service.duplicate(
        renamed.id,
        "Ref Project Copy",
    )
    service.archive(
        renamed.id
    )
    service.restore_archive(
        renamed.id
    )

    assert renamed.id == project.id
    assert duplicate.id != project.id
    assert vault.resolve_asset_path(
        asset.asset_id
    ).exists()
