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


def test_runtime_profile_missing_is_not_ready_for_generate():

    root = ROOT / "cache" / "test_runtime_profile_missing"

    service = RuntimeProfileService(
        config_file=root / "runtime_profiles.json",
        app_root=root,
    )

    report = service.validate(
        RuntimeProfile(
            profile_id="missing",
            display_name="Missing Runtime",
        ),
        require_generate=True,
    )

    assert report["doctor_status"] == "UNAVAILABLE"
    assert any(
        item["code"] == "runtime_missing"
        for item in report["causes"]
    )


def test_runtime_profile_generate_doctor_detects_scripts_and_pretrained():

    root = ROOT / "cache" / "test_runtime_profile_doctor"

    runtime = root / "runtime_root"

    paths = [
        runtime / "webui.py",
        runtime / "GPT_SoVITS" / "inference_cli.py",
        runtime / "GPT_SoVITS" / "inference_webui.py",
        runtime / "tools" / "slice_audio.py",
        runtime / "tools" / "asr" / "fasterwhisper_asr.py",
        runtime / "GPT_SoVITS" / "prepare_datasets" / "1-get-text.py",
        runtime / "GPT_SoVITS" / "prepare_datasets" / "2-get-hubert-wav32k.py",
        runtime / "GPT_SoVITS" / "prepare_datasets" / "2-get-sv.py",
        runtime / "GPT_SoVITS" / "prepare_datasets" / "3-get-semantic.py",
        runtime / "GPT_SoVITS" / "s1_train.py",
        runtime / "GPT_SoVITS" / "s2_train.py",
        runtime / "GPT_SoVITS" / "pretrained_models" / "s1v3.ckpt",
        runtime / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Gv2Pro.pth",
        runtime / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Dv2Pro.pth",
        runtime / "GPT_SoVITS" / "pretrained_models" / "chinese-roberta-wwm-ext-large" / "marker.txt",
        runtime / "GPT_SoVITS" / "pretrained_models" / "chinese-hubert-base" / "marker.txt",
        runtime / "GPT_SoVITS" / "configs" / "s2v2Pro.json",
    ]

    for path in paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            "mock",
            encoding="utf-8",
        )

    service = RuntimeProfileService(
        config_file=root / "runtime_profiles.json",
        app_root=root,
    )

    profile = RuntimeProfile(
        profile_id="doctor",
        display_name="Doctor",
        runtime_path=str(
            runtime
        ),
        python_path=sys.executable,
        pretrained_model_path=str(
            runtime / "GPT_SoVITS" / "pretrained_models"
        ),
    )

    report = service.validate(
        profile,
        require_generate=True,
    )

    assert report["checks"]["gpt_sovits_scripts"]["inference_cli"]["exists"]
    assert report["checks"]["pretrained_models"]["gpt"]["exists"]
    assert report["doctor_status"] in {
        "READY",
        "MISCONFIGURED",
    }
    assert "ffmpeg" in report["checks"]


test_runtime_profile_serialization_and_relative_path()
test_switch_default_runtime_does_not_touch_voice_model()
test_runtime_profile_missing_is_not_ready_for_generate()
test_runtime_profile_generate_doctor_detects_scripts_and_pretrained()

print("RUNTIME_PROFILE_TEST_OK")
