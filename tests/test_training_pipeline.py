import json
import shutil
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.runtime_profile import RuntimeProfile
from models.train_config import TrainConfig
from models.train_state import TrainJobState
from services.training_service import TrainingService
from services.dataset_review_service import DatasetReviewService
from services.runtime_profile_service import RuntimeProfileService


class FakeVoice:

    def __init__(
        self,
        root,
        voice_id="0001",
        name="Thu Minh",
    ):

        self.name = name
        self.path = root / name
        self.path.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config = type(
            "Config",
            (),
            {
                "voice_id": voice_id,
                "engine": "gpt_sovits",
            },
        )()

    @property
    def id(
        self,
    ):

        return self.config.voice_id


class FakeRuntimeProfiles:

    def __init__(
        self,
        pretrained_model_path="pretrained",
        profiles=None,
    ):

        self.pretrained_model_path = pretrained_model_path
        self.profiles = profiles

    def list_profiles(
        self,
    ):

        if self.profiles is not None:

            return self.profiles

        return [
            RuntimeProfile(
                profile_id="default",
                display_name="GPT-SoVITS Test",
                engine_version="v2pro",
                runtime_path="runtime",
                python_path=sys.executable,
                pretrained_model_path=self.pretrained_model_path,
                is_default=True,
            )
        ]

    def validate(
        self,
        profile,
        smoke_test=False,
    ):

        return {
            "profile_id": profile.profile_id,
            "status": "ready",
            "causes": [],
            "detected_path": {
                "runtime_path": profile.runtime_path,
                "python_path": profile.python_path,
                "pretrained_model_path": profile.pretrained_model_path,
            },
            "checks": {
                "python": {
                    "ok": True,
                    "stdout": "3.12.0",
                    "stderr": "",
                },
                "torch": {
                    "ok": True,
                    "stdout": json.dumps(
                        {
                            "version": "2.0.0",
                            "cuda": False,
                            "device_count": 0,
                        }
                    ),
                    "stderr": "",
                },
                "gpt_sovits_scripts": {},
            },
        }

    def guidance(
        self,
    ):

        return {}


def reset_root(
    name,
):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(
            root
        )

    root.mkdir(
        parents=True,
    )

    return root


def write_wav(
    file,
    channels=1,
    sample_rate=32000,
):

    file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(
            file
        ),
        "wb",
    ) as audio:

        audio.setnchannels(
            channels
        )
        audio.setsampwidth(
            2
        )
        audio.setframerate(
            sample_rate
        )
        audio.writeframes(
            b"\x00\x00"
            * channels
            * sample_rate
        )


def write_metadata(
    root,
    wav_file=None,
    text="Xin chao.",
):

    wav_file = wav_file or root / "clips" / "000001.wav"

    if not wav_file.exists():

        write_wav(
            wav_file
        )

    metadata = root / "metadata.list"

    metadata.write_text(
        f"{wav_file}|speaker|vi|{text}\n",
        encoding="utf-8",
    )

    return metadata


def approved_review():

    return {
        "summary": {
            "train_allowed": True,
        },
        "items": [
            {
                "status": "approved",
                "code": "test_version",
            }
        ],
    }


def pending_review():

    return {
        "summary": {
            "train_allowed": False,
        },
        "items": [
            {
                "status": "pending",
                "code": "test_version",
            }
        ],
    }


def service_with_runtime():

    service = TrainingService()

    service.runtime_profiles = FakeRuntimeProfiles()

    return service


def train_config(
    metadata,
    run_id="run001",
    validation_only=True,
    smoke_test=False,
):

    return TrainConfig(
        validation_only=validation_only,
        smoke_test=smoke_test,
        run_id=run_id,
        metadata_path=str(
            metadata
        ),
    )


def test_review_not_allowed_blocks_train():

    root = reset_root(
        "test_training_review_block"
    )

    metadata = write_metadata(
        root
    )

    result = service_with_runtime().prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata
        ),
        review_report=pending_review(),
        output_root=root / "voices",
    )

    assert result["ready"] is False
    assert any(
        error["code"] == "dataset_review_not_allowed"
        for error in result["report"]["errors"]
    )


def test_metadata_missing_and_empty():

    root = reset_root(
        "test_training_metadata_missing"
    )

    missing = service_with_runtime().prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            root / "missing.list"
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "metadata_missing"
        for error in missing["report"]["errors"]
    )

    empty_file = root / "empty_metadata.list"

    empty_file.write_text(
        "",
        encoding="utf-8",
    )

    empty = service_with_runtime().prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            empty_file,
            run_id="run002",
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "metadata_empty"
        for error in empty["report"]["errors"]
    )


def test_wav_wrong_format_is_rejected():

    root = reset_root(
        "test_training_wav_format"
    )

    wav_file = root / "clips" / "bad.wav"

    write_wav(
        wav_file,
        channels=2,
        sample_rate=44100,
    )

    metadata = write_metadata(
        root,
        wav_file=wav_file,
    )

    result = service_with_runtime().prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "metadata_audio_invalid_format"
        for error in result["report"]["errors"]
    )


def test_runtime_and_pretrained_missing():

    root = reset_root(
        "test_training_runtime_missing"
    )

    metadata = write_metadata(
        root
    )

    service = TrainingService()

    service.runtime_profiles = FakeRuntimeProfiles(
        profiles=[]
    )

    runtime_missing = service.prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "runtime_profile_missing"
        for error in runtime_missing["report"]["errors"]
    )

    service = TrainingService()

    service.runtime_profiles = FakeRuntimeProfiles(
        pretrained_model_path=""
    )

    pretrained_missing = service.prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata,
            run_id="run002",
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "pretrained_model_missing"
        for error in pretrained_missing["report"]["errors"]
    )


def test_validation_only_report_progress_and_run_id():

    root = reset_root(
        "test_training_validation_only"
    )

    metadata = write_metadata(
        root
    )

    result = service_with_runtime().prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert result["ready"] is True
    assert result["status"] == "validation_ready"
    assert result["run_id"] == "run001"
    assert Path(
        result["report_path"]
    ).exists()
    assert result["report"]["clip_count"] == 1
    assert result["report"]["total_duration"] > 0
    assert result["progress"]
    assert (
        "0001"
        + str(
            Path("model")
        )
        + "run001"
    ).replace(
        "\\",
        "",
    ) in result["model_output"].replace(
        "\\",
        "",
    )


def test_smoke_test_mock_and_no_overwrite():

    root = reset_root(
        "test_training_smoke"
    )

    metadata = write_metadata(
        root
    )

    service = service_with_runtime()

    service.train_executor = lambda context: {
        "ok": True,
        "checkpoint": "mock.ckpt",
    }

    result = service.prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata,
            validation_only=False,
            smoke_test=True,
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert result["status"] == "smoke_test_ok"
    assert Path(
        result["state"]["model_output"]
    ).exists()
    assert (
        Path(
            result["state"]["report_path"]
        ).parent
        / "train_state.json"
    ).exists()

    blocked = service.prepare_train(
        FakeVoice(
            root
        ),
        train_config(
            metadata,
            validation_only=False,
            smoke_test=True,
        ),
        review_report=approved_review(),
        output_root=root / "voices",
    )

    assert any(
        error["code"] == "model_output_exists"
        for error in blocked["report"]["errors"]
    )


def test_resume_state_serialization():

    state = TrainJobState(
        run_id="abc",
        voice_id="0001",
        status="paused",
        checkpoint="checkpoint.ckpt",
        model_output="voices/0001/model/abc",
        resume_allowed=True,
    )

    loaded = TrainJobState.from_dict(
        state.to_dict()
    )

    assert loaded.run_id == "abc"
    assert loaded.resume_allowed is True
    assert loaded.resume_confirmed is False


def test_review_decisions_ignore_or_reject_error_files():

    report = {
        "items": [
            {
                "code": "test_version",
                "status": "pending",
                "reason": "test",
            },
            {
                "code": "broken_file",
                "status": "pending",
                "reason": "broken",
            },
            {
                "code": "empty_file",
                "status": "pending",
                "reason": "empty",
            },
        ],
        "summary": {
            "blocking_errors": 3,
        },
    }

    service = DatasetReviewService()

    final = service.apply_decisions(
        report,
        {
            "test_version": "ignored",
            "broken_file": "rejected",
            "empty_file": "rejected",
        },
    )

    assert final["summary"]["pending"] == 0
    assert final["summary"]["ignored"] == 1
    assert final["summary"]["rejected"] == 2
    assert final["summary"]["train_allowed"] is True


def test_runtime_profile_default_and_detection():

    root = reset_root(
        "test_training_runtime_profile_detect"
    )

    runtime_root = root / "runtime"

    (runtime_root / "runtime").mkdir(
        parents=True,
    )

    (runtime_root / "runtime" / "python.exe").write_text(
        "",
        encoding="utf-8",
    )

    paths = [
        runtime_root / "webui.py",
        runtime_root / "GPT_SoVITS" / "inference_webui.py",
        runtime_root / "tools" / "slice_audio.py",
        runtime_root / "tools" / "asr" / "fasterwhisper_asr.py",
        runtime_root / "GPT_SoVITS" / "prepare_datasets" / "1-get-text.py",
        runtime_root / "GPT_SoVITS" / "prepare_datasets" / "2-get-hubert-wav32k.py",
        runtime_root / "GPT_SoVITS" / "prepare_datasets" / "3-get-semantic.py",
        runtime_root / "GPT_SoVITS" / "s1_train.py",
        runtime_root / "GPT_SoVITS" / "s2_train.py",
        runtime_root / "GPT_SoVITS" / "configs" / "s2v2Pro.json",
        runtime_root / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Gv2Pro.pth",
        runtime_root / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Dv2Pro.pth",
        runtime_root / "GPT_SoVITS" / "pretrained_models" / "s1v3.ckpt",
        runtime_root / "GPT_SoVITS" / "pretrained_models" / "chinese-roberta-wwm-ext-large" / "config.json",
        runtime_root / "GPT_SoVITS" / "pretrained_models" / "chinese-hubert-base" / "config.json",
    ]

    for path in paths:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            "",
            encoding="utf-8",
        )

    service = RuntimeProfileService(
        config_file=root / "runtime_profiles.json",
        app_root=root,
    )

    result = service.create_gpt_sovits_profile(
        runtime_root,
    )

    profiles = service.list_profiles()

    assert result["detected"]["engine_version"] == "v2Pro"
    assert result["detected"]["ready"] is True
    assert profiles[0].is_default is True
    assert profiles[0].engine_version == "v2Pro"


def test_smoke_command_construction_and_subprocess_failure():

    root = reset_root(
        "test_training_smoke_command"
    )

    metadata = write_metadata(
        root
    )

    model_output = root / "voices" / "0001" / "model" / "run001"

    model_output.mkdir(
        parents=True,
    )

    service = TrainingService()

    runtime = {
        "profile": {
            "python_path": sys.executable,
            "runtime_path": str(
                root
            ),
        },
        "validation": {
            "detected_path": {
                "python_path": sys.executable,
                "runtime_path": str(
                    root
                ),
            }
        },
    }

    command = service.build_smoke_command(
        runtime,
        {
            "path": str(
                metadata
            )
        },
        model_output,
    )

    assert command
    assert command[0] == sys.executable
    assert Path(
        command[1]
    ).is_absolute()

    bad_script = root / "bad_smoke.py"

    bad_script.write_text(
        "import sys\n"
        "sys.stderr.write('CUDA out of memory')\n"
        "sys.exit(1)\n",
        encoding="utf-8",
    )

    bad = service.run_smoke_command(
        [
            sys.executable,
            str(
                bad_script
            ),
            str(
                root
            ),
            str(
                metadata
            ),
            str(
                model_output / "out.json"
            ),
            str(
                model_output / "ckpt.mock"
            ),
        ],
        runtime,
        model_output,
    )

    assert bad["ok"] is False
    assert bad["out_of_memory"] is True
    assert bad["exit_code"] == 1
