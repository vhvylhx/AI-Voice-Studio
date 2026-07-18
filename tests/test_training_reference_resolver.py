import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.training_reference_config import (  # noqa: E402
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_TRAINING_DATASET,
    SPEAKER_REFERENCE_VOICE_DEFAULT,
    TrainingReferenceConfig,
)
from services.training_reference_resolver import TrainingReferenceResolver  # noqa: E402


class Voice:

    class Config:

        reference_audio = "voice.wav"
        reference_text = "Xin chao"

    config = Config()


def test_app_style_profile_mode_ignores_speaker_fields():

    config = TrainingReferenceConfig(
        reference_mode=REFERENCE_MODE_APP_STYLE_PROFILE,
        style_profile_id="style_000001",
        speaker_reference_audio="manual.wav",
    )

    result = TrainingReferenceResolver().resolve(
        config,
        voice=Voice(),
    )

    assert result["style_profile_id"] == "style_000001"
    assert result["speaker_reference"] == {}


def test_manual_dataset_and_voice_default_precedence():

    resolver = TrainingReferenceResolver()

    manual = resolver.resolve(
        TrainingReferenceConfig(
            reference_mode=REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            speaker_reference_mode=SPEAKER_REFERENCE_SELECTED_FILE,
            speaker_reference_audio="manual.wav",
        ),
        voice=Voice(),
    )

    assert manual["speaker_reference"]["origin"] == "manual"

    dataset = resolver.resolve(
        TrainingReferenceConfig(
            reference_mode=REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            speaker_reference_mode=SPEAKER_REFERENCE_TRAINING_DATASET,
        ),
        voice=Voice(),
        dataset_reference={
            "clip": "dataset.wav",
        },
    )

    assert dataset["speaker_reference"]["origin"] == "training_dataset"

    voice_default = resolver.resolve(
        TrainingReferenceConfig(
            reference_mode=REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            speaker_reference_mode=SPEAKER_REFERENCE_VOICE_DEFAULT,
        ),
        voice=Voice(),
    )

    assert voice_default["speaker_reference"]["audio"] == "voice.wav"
