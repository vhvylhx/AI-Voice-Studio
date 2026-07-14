import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.runtime_profile import RuntimeProfile
from services.runtime_profile_service import RuntimeProfileService


def test_runtime_profile_serialization_and_relative_path():

    root = ROOT / "cache" / "test_runtime_profile"

    runtime = root / "runtimes" / "gpt"

    python = runtime / "python.exe"

    pretrained = root / "models" / "pretrained"

    service = RuntimeProfileService(
        config_file=root / "runtime_profiles.json",
        app_root=root,
    )

    profile = RuntimeProfile(
        profile_id="low_vram",
        display_name="GPT-SoVITS v2Pro - VRAM thap",
        engine_version="v2pro",
        runtime_path=str(
            runtime
        ),
        python_path=str(
            python
        ),
        hardware_profile="low_vram",
        minimum_vram="6GB",
        recommended_vram="8GB",
        status="unknown",
        is_default=True,
        pretrained_model_path=str(
            pretrained
        ),
        compatibility_notes="Voice model cu giu nguyen.",
    )

    data = service.serialize_profile(
        profile
    )

    assert data["runtime_path"] == str(
        Path("runtimes") / "gpt"
    )
    assert data["python_path"] == str(
        Path("runtimes") / "gpt" / "python.exe"
    )
    assert data["pretrained_model_path"] == str(
        Path("models") / "pretrained"
    )


def test_switch_default_runtime_does_not_touch_voice_model():

    root = ROOT / "cache" / "test_runtime_profile_default"

    service = RuntimeProfileService(
        config_file=root / "runtime_profiles.json",
        app_root=root,
    )

    service.add_profile(
        RuntimeProfile(
            profile_id="old",
            display_name="Old Runtime",
            is_default=True,
            compatibility_notes="voice model path: voices/0001/model",
        )
    )

    service.add_profile(
        RuntimeProfile(
            profile_id="new",
            display_name="New Runtime",
            is_default=False,
            compatibility_notes="Can validate compatibility truoc khi train/generate.",
        )
    )

    service.set_default(
        "new"
    )

    profiles = {
        item.profile_id: item
        for item in service.list_profiles()
    }

    assert profiles["new"].is_default is True
    assert profiles["old"].is_default is False
    assert "voices/0001/model" in profiles["old"].compatibility_notes


test_runtime_profile_serialization_and_relative_path()
test_switch_default_runtime_does_not_touch_voice_model()

print("RUNTIME_PROFILE_TEST_OK")
