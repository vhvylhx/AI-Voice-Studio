import json
import sys
import wave
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.local_api_config import LocalApiConfig  # noqa: E402
from services.generate_runtime_validation_service import (  # noqa: E402
    GenerateRuntimeValidationService,
)
from services.local_api_service import LocalApiService  # noqa: E402


def write_wav(
    path,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(
            path
        ),
        "wb",
    ) as wav:

        wav.setnchannels(
            1
        )

        wav.setsampwidth(
            2
        )

        wav.setframerate(
            32000
        )

        wav.writeframes(
            b"\x00\x00" * 320
        )


class FakeRuntimeProfiles:

    def __init__(
        self,
        status="READY",
    ):

        self.status = status

        self.profile = SimpleNamespace(
            profile_id="runtime_default",
            runtime_path="runtime",
            python_path="runtime/python.exe",
            engine_version="v2Pro",
            is_default=True,
            to_dict=lambda: {
                "profile_id": "runtime_default",
                "runtime_path": "runtime",
                "python_path": "runtime/python.exe",
                "engine_version": "v2Pro",
                "is_default": True,
            },
        )

    def list_profiles(
        self,
    ):

        return [
            self.profile
        ]

    def validate(
        self,
        profile,
        require_generate=False,
    ):

        return {
            "doctor_status": self.status,
            "status": "ready"
            if self.status == "READY"
            else "runtime_missing",
            "checks": {
                "gpt_sovits_scripts": {
                    "inference_cli": {
                        "path": "runtime/GPT_SoVITS/inference_cli.py",
                        "exists": True,
                    }
                }
            },
        }

    def guidance(
        self,
    ):

        return {}


class FakeVoiceService:

    def __init__(
        self,
        voice,
        ready=True,
    ):

        self.voice = voice

        self.ready = ready

    def list(
        self,
    ):

        return [
            self.voice.name
        ]

    def load(
        self,
        name,
    ):

        return self.voice

    def validate_gpt_sovits(
        self,
        voice,
    ):

        missing = []

        if not self.ready:

            missing.append(
                "gpt_model"
            )

        return {
            "voice_id": voice.id,
            "voice_name": voice.name,
            "ready": self.ready,
            "missing": missing,
        }


def make_voice(
    root,
):

    gpt = root / "model.ckpt"

    sovits = root / "model.pth"

    reference = root / "reference.wav"

    gpt.write_text(
        "gpt",
        encoding="utf-8",
    )

    sovits.write_text(
        "sovits",
        encoding="utf-8",
    )

    write_wav(
        reference
    )

    return SimpleNamespace(
        id="0001",
        name="Thu Minh",
        config=SimpleNamespace(
            gpt_model=str(
                gpt
            ),
            sovits_model=str(
                sovits
            ),
            reference_audio=str(
                reference
            ),
            reference_text="Xin chào.",
            default_variant_id="default",
            variants=[
                {
                    "id": "default",
                }
            ],
            runtime_profile_id="runtime_default",
        ),
    )


def test_environment_ready_alone_does_not_unlock_generate_execution():

    root = ROOT / "cache" / "test_generate_runtime_validation_env_only"

    service = GenerateRuntimeValidationService(
        runtime_profiles=FakeRuntimeProfiles(
            status="READY"
        ),
        voice_service=None,
        smoke_root=root / "smoke",
        app_root=root,
    )

    readiness = service.readiness()

    assert readiness["environment"]["status"] == "READY"
    assert readiness["selected_assets"]["status"] == "BLOCKED"
    assert readiness["real_inference"]["status"] == "BLOCKED"
    assert readiness["capabilities"]["generate_execution"] == "BLOCKED"


def test_real_smoke_requires_matching_fingerprint_and_valid_wav():

    root = ROOT / "cache" / "test_generate_runtime_validation_pass"

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    voice = make_voice(
        root
    )

    service = GenerateRuntimeValidationService(
        runtime_profiles=FakeRuntimeProfiles(),
        voice_service=FakeVoiceService(
            voice
        ),
        smoke_root=root / "smoke",
        app_root=root,
    )

    selection = {
        "voice_id": "0001",
        "variant_id": "default",
    }

    first = service.readiness(
        selection
    )

    assert first["selected_assets"]["status"] == "READY"
    assert first["real_inference"]["status"] == "SKIPPED"
    assert first["capabilities"]["generate_execution"] == "DEGRADED"

    output = root / "output.wav"

    write_wav(
        output
    )

    service.write_smoke_report(
        first["fingerprint"],
        {
            "status": "PASS",
            "output_wav": str(
                output
            ),
        },
    )

    second = service.readiness(
        selection
    )

    assert second["real_inference"]["status"] == "PASS"
    assert second["capabilities"]["generate_execution"] == "READY"


def test_stale_smoke_does_not_unlock_generate_execution():

    root = ROOT / "cache" / "test_generate_runtime_validation_stale"

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    voice = make_voice(
        root
    )

    service = GenerateRuntimeValidationService(
        runtime_profiles=FakeRuntimeProfiles(),
        voice_service=FakeVoiceService(
            voice
        ),
        smoke_root=root / "smoke",
        app_root=root,
    )

    selection = {
        "voice_id": "0001",
        "variant_id": "default",
    }

    first = service.readiness(
        selection
    )

    service.smoke_report_path(
        first["fingerprint"]
    ).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    service.smoke_report_path(
        first["fingerprint"]
    ).write_text(
        json.dumps(
            {
                "status": "PASS",
                "fingerprint": "old",
                "output_wav": str(
                    root / "missing.wav"
                ),
            }
        ),
        encoding="utf-8",
    )

    second = service.readiness(
        selection
    )

    assert second["real_inference"]["status"] == "STALE"
    assert second["capabilities"]["generate_execution"] == "DEGRADED"


def test_local_api_readiness_uses_three_layer_validation():

    root = ROOT / "cache" / "test_generate_runtime_validation_api"

    validator = GenerateRuntimeValidationService(
        runtime_profiles=FakeRuntimeProfiles(
            status="READY"
        ),
        voice_service=None,
        smoke_root=root / "smoke",
        app_root=root,
    )

    api = LocalApiService(
        config=LocalApiConfig(
            local_api_enabled=True,
            local_api_token="secret-token",
        ),
        generate_runtime_validation_service=validator,
    )

    readiness = api.generate_readiness()

    assert readiness["capabilities"]["generate_execution"] == "BLOCKED"
    assert readiness["runtime_doctor"]["environment"]["status"] == "READY"
    assert readiness["runtime_doctor"]["selected_assets"]["status"] == "BLOCKED"
    assert readiness["runtime_doctor"]["real_inference"]["status"] == "BLOCKED"
