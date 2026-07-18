import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.training_reference_config import (  # noqa: E402
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_NONE,
    SPEAKER_REFERENCE_SELECTED_FILE,
    TrainingReferenceConfig,
)


def test_old_config_loads_with_safe_defaults():

    config = TrainingReferenceConfig.from_dict({})

    assert config.reference_mode == REFERENCE_MODE_NONE
    assert config.speaker_reference_audio == ""
    assert config.selected_training_segment_ids == []


def test_serialize_deserialize_and_mode_validation():

    config = TrainingReferenceConfig.from_dict(
        {
            "reference_mode": REFERENCE_MODE_APP_STYLE_PROFILE,
            "style_profile_id": "style_000001",
            "speaker_reference_mode": SPEAKER_REFERENCE_SELECTED_FILE,
            "speaker_reference_audio": "a.wav",
            "selected_training_segment_ids": [
                1,
                "2",
            ],
        }
    )

    data = config.to_dict()
    loaded = TrainingReferenceConfig.from_dict(
        data
    )

    assert loaded.reference_mode == REFERENCE_MODE_APP_STYLE_PROFILE
    assert loaded.style_profile_id == "style_000001"
    assert loaded.selected_training_segment_ids == [
        "1",
        "2",
    ]

    invalid = TrainingReferenceConfig.from_dict(
        {
            "reference_mode": "bad",
            "speaker_reference_mode": "bad",
        }
    )

    assert invalid.reference_mode == REFERENCE_MODE_NONE
    assert invalid.speaker_reference_mode == "none"
