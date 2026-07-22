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
from services.training_preprocessing_service import TrainingPreprocessingService
from services.training_service import TrainingService


class FakeVoice:

    def __init__(
        self,
        voice_id="0001",
        name="Thu Minh",
    ):

        self.name = name
        self.display_name = name
        self.path = ROOT / "cache" / "fake_voice" / name
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
        root,
        supported_language="vi",
        missing_script="",
    ):

        self.root = Path(
            root
        )

        self.supported_language = supported_language

        self.missing_script = missing_script

    def list_profiles(
        self,
    ):

        return [
            RuntimeProfile(
                profile_id="fake_runtime",
                display_name="Fake Runtime",
                engine_version="v2Pro",
                runtime_path=str(
                    self.root
                ),
                python_path=sys.executable,
                pretrained_model_path=str(
                    self.root
                    / "GPT_SoVITS"
                    / "pretrained_models"
                ),
                is_default=True,
            )
        ]

    def resolve_path(
        self,
        value,
    ):

        return Path(
            value
        )

    def validate(
        self,
        profile,
        smoke_test=False,
    ):

        return {
            "status": "ready",
            "causes": [],
            "detected_path": {
                "runtime_path": profile.runtime_path,
                "python_path": profile.python_path,
                "pretrained_model_path": profile.pretrained_model_path,
            },
            "checks": {},
        }

    def gpt_sovits_scripts(
        self,
        runtime_path,
    ):

        root = Path(
            runtime_path
        )

        scripts = {
            "prepare_text": root / "GPT_SoVITS" / "prepare_datasets" / "1-get-text.py",
            "prepare_hubert": root / "GPT_SoVITS" / "prepare_datasets" / "2-get-hubert-wav32k.py",
            "prepare_semantic": root / "GPT_SoVITS" / "prepare_datasets" / "3-get-semantic.py",
        }

        if self.missing_script:

            scripts[
                self.missing_script
            ] = root / "missing.py"

        return {
            key: {
                "path": str(
                    path
                ),
                "exists": path.exists(),
            }
            for key, path in scripts.items()
        }

    def detect_pretrained_models(
        self,
        runtime_path,
    ):

        root = Path(
            runtime_path
        )

        paths = {
            "gpt": root / "GPT_SoVITS" / "pretrained_models" / "s1v3.ckpt",
            "sovits_g": root / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Gv2Pro.pth",
            "sovits_d": root / "GPT_SoVITS" / "pretrained_models" / "v2Pro" / "s2Dv2Pro.pth",
            "bert": root / "GPT_SoVITS" / "pretrained_models" / "chinese-roberta-wwm-ext-large",
            "hubert": root / "GPT_SoVITS" / "pretrained_models" / "chinese-hubert-base",
        }

        return {
            key: {
                "path": str(
                    path
                ),
                "exists": path.exists(),
            }
            for key, path in paths.items()
        }

    def guidance(
        self,
    ):

        return {}


class FakeLeaseManager:

    def __init__(
        self,
    ):

        self.acquired = 0
        self.released = 0

    def acquire(
        self,
        job,
        requirement,
        selected_gpu_device_id="",
        owner="",
    ):

        self.acquired += 1

        lease = type(
            "Lease",
            (),
            {
                "lease_id": "lease_test",
            },
        )()

        return lease, ""

    def release(
        self,
        lease_id,
    ):

        self.released += 1

        return True


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
            1
        )
        audio.setsampwidth(
            2
        )
        audio.setframerate(
            32000
        )
        audio.writeframes(
            b"\x00\x00"
            * 32000
        )


def write_metadata(
    root,
    name="clip_001.wav",
    language="vi",
):

    wav = root / "clips" / name

    write_wav(
        wav
    )

    metadata = root / "metadata.list"

    metadata.write_text(
        f"{wav}|speaker|{language}|Xin chao.\n",
        encoding="utf-8",
    )

    return metadata


def write_script(
    file,
    source,
):

    file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file.write_text(
        source,
        encoding="utf-8",
    )


def create_fake_runtime(
    root,
    supported_language="vi",
):

    runtime = root / "runtime"

    prepare = runtime / "GPT_SoVITS" / "prepare_datasets"

    pretrained = runtime / "GPT_SoVITS" / "pretrained_models"

    for path in [
        pretrained / "s1v3.ckpt",
        pretrained / "v2Pro" / "s2Gv2Pro.pth",
        pretrained / "v2Pro" / "s2Dv2Pro.pth",
        pretrained / "chinese-roberta-wwm-ext-large" / "config.json",
        pretrained / "chinese-hubert-base" / "config.json",
        pretrained / "sv" / "pretrained_eres2netv2w24s4ep4.ckpt",
        runtime / "GPT_SoVITS" / "configs" / "s2v2Pro.json",
    ]:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            "mock",
            encoding="utf-8",
        )

    write_script(
        prepare / "1-get-text.py",
        (
            "import os\n"
            f"language_v1_to_language_v2 = {{'{supported_language}': '{supported_language}'}}\n"
            "opt=os.environ['opt_dir']\n"
            "os.makedirs(opt + '/3-bert', exist_ok=True)\n"
            "open(opt + '/3-bert/clip_001.wav.pt', 'w', encoding='utf-8').write('bert')\n"
            "open(opt + '/2-name2text-0.txt', 'w', encoding='utf-8').write('clip_001.wav\\tph\\t[1]\\tXin chao.\\n')\n"
        ),
    )

    write_script(
        prepare / "2-get-hubert-wav32k.py",
        (
            "import os\n"
            "opt=os.environ['opt_dir']\n"
            "os.makedirs(opt + '/4-cnhubert', exist_ok=True)\n"
            "os.makedirs(opt + '/5-wav32k', exist_ok=True)\n"
            "open(opt + '/4-cnhubert/clip_001.wav.pt', 'w', encoding='utf-8').write('hubert')\n"
            "open(opt + '/5-wav32k/clip_001.wav', 'wb').write(b'RIFFmock')\n"
        ),
    )

    write_script(
        prepare / "2-get-sv.py",
        (
            "import os\n"
            "opt=os.environ['opt_dir']\n"
            "os.makedirs(opt + '/7-sv_cn', exist_ok=True)\n"
            "open(opt + '/7-sv_cn/clip_001.wav.pt', 'w', encoding='utf-8').write('sv')\n"
        ),
    )

    write_script(
        prepare / "3-get-semantic.py",
        (
            "import os\n"
            "opt=os.environ['opt_dir']\n"
            "open(opt + '/6-name2semantic-0.tsv', 'w', encoding='utf-8').write('clip_001.wav\\t1 2 3\\n')\n"
        ),
    )

    cleaner = runtime / "GPT_SoVITS" / "text" / "cleaner.py"

    cleaner.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaner.write_text(
        f"language_module_map = {{'{supported_language}': 'mock'}}\n",
        encoding="utf-8",
    )

    return runtime


def test_plan_uses_voice_id_and_run_owned_output():

    root = reset_root(
        "test_preprocess_plan"
    )

    metadata = write_metadata(
        root
    )

    runtime = create_fake_runtime(
        root
    )

    service = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime
        ),
    )

    result = service.build_plan(
        FakeVoice(),
        metadata,
        preprocessing_run_id="avs01419a_voice_0001_test",
        output_root=root / "preprocess",
    )

    assert result["ok"] is True
    assert result["plan"]["voice_id"] == "0001"
    assert "Thu Minh" in result["plan"]["display_name_snapshot"]
    assert Path(
        result["plan"]["output_root"]
    ).resolve().is_relative_to(
        root.resolve()
    )
    assert result["plan"]["metadata_sha256"]
    assert isinstance(
        result["plan"]["stages"][0]["command"],
        list,
    )


def test_unsupported_vietnamese_runtime_blocks_before_execution():

    root = reset_root(
        "test_preprocess_language_block"
    )

    metadata = write_metadata(
        root
    )

    runtime = create_fake_runtime(
        root,
        supported_language="en",
    )

    result = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime,
            supported_language="en",
        ),
    ).build_plan(
        FakeVoice(),
        metadata,
        preprocessing_run_id="run_lang",
        output_root=root / "preprocess",
    )

    assert result["ok"] is False
    assert any(
        item["code"] == "PREPROCESS_CONFIG_INVALID"
        for item in result["blockers"]
    )


def test_dataset_traversal_and_duplicate_blocked():

    root = reset_root(
        "test_preprocess_dataset_block"
    )

    wav = root / "clips" / "clip_001.wav"

    write_wav(
        wav
    )

    metadata = root / "metadata.list"

    metadata.write_text(
        f"{wav}|speaker|vi|Xin chao.\n{wav}|speaker|vi|Xin chao lan 2.\n",
        encoding="utf-8",
    )

    service = TrainingPreprocessingService(
        app_root=ROOT
    )

    report = service.validate_dataset(
        metadata
    )

    assert report["ok"] is False
    assert any(
        item["reason"] == "metadata.list co duplicate audio path."
        for item in report["errors"]
    )


def test_full_mock_preprocessing_writes_manifest_and_artifacts():

    root = reset_root(
        "test_preprocess_run"
    )

    metadata = write_metadata(
        root
    )

    runtime = create_fake_runtime(
        root
    )

    leases = FakeLeaseManager()

    service = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime
        ),
        lease_manager=leases,
    )

    result = service.run(
        FakeVoice(),
        metadata,
        preprocessing_run_id="avs01419a_voice_0001_mock",
        output_root=root / "preprocess",
    )

    manifest = json.loads(
        Path(
            result["run"]["manifest_path"]
        ).read_text(
            encoding="utf-8"
        )
    )

    assert result["ok"] is True
    assert manifest["run_id"] == "avs01419a_voice_0001_mock"
    assert manifest["status"] == "success"
    assert manifest["runtime"]["supported_languages"] == [
        "vi"
    ]
    assert manifest["training_ready"] is True
    assert manifest["counts"]["input_clips"] == 1
    assert manifest["artifacts"]["name2text"]["count"] == 1
    assert manifest["artifacts"]["semantic"]["count"] == 1
    assert leases.acquired == leases.released


def test_training_preflight_reads_preprocessing_manifest_and_stale_state():

    root = reset_root(
        "test_preprocess_training_gate"
    )

    metadata = write_metadata(
        root
    )

    runtime = create_fake_runtime(
        root
    )

    service = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime
        ),
    )

    preprocess = service.run(
        FakeVoice(),
        metadata,
        preprocessing_run_id="avs01419a_voice_0001_gate",
        output_root=root / "preprocess",
    )

    training = TrainingService()
    training.runtime_profiles = FakeRuntimeProfiles(
        runtime
    )

    config = TrainConfig(
        validation_only=True,
        run_id="train_gate",
        metadata_path=str(
            metadata
        ),
        preprocessing_manifest_path=preprocess["run"]["manifest_path"],
    )

    ready = training.prepare_train(
        FakeVoice(),
        config,
        review_report={
            "summary": {
                "train_allowed": True,
            },
            "items": [],
        },
        output_root=root / "voices",
    )

    assert ready["ready"] is True
    assert ready["report"]["preprocessing"]["status"] == "READY"

    manifest = Path(
        preprocess["run"]["manifest_path"]
    )

    data = json.loads(
        manifest.read_text(
            encoding="utf-8"
        )
    )

    data[
        "dataset_fingerprint"
    ] = "stale"

    manifest.write_text(
        json.dumps(
            data,
            indent=4,
        ),
        encoding="utf-8",
    )

    stale = training.prepare_train(
        FakeVoice(),
        TrainConfig(
            validation_only=True,
            run_id="train_gate_stale",
            metadata_path=str(
                metadata
            ),
            preprocessing_manifest_path=str(
                manifest
            ),
        ),
        review_report={
            "summary": {
                "train_allowed": True,
            },
            "items": [],
        },
        output_root=root / "voices",
    )

    assert stale["ready"] is False
    assert stale["report"]["preprocessing"]["status"] == "STALE"


def test_missing_script_and_process_failure_have_stable_codes():

    root = reset_root(
        "test_preprocess_failures"
    )

    metadata = write_metadata(
        root
    )

    runtime = create_fake_runtime(
        root
    )

    result = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime,
            missing_script="prepare_semantic",
        ),
    ).build_plan(
        FakeVoice(),
        metadata,
        preprocessing_run_id="run_missing_script",
        output_root=root / "preprocess_missing",
    )

    assert any(
        item["code"] == "PREPROCESS_SCRIPT_MISSING"
        for item in result["blockers"]
    )

    broken_script = (
        runtime
        / "GPT_SoVITS"
        / "prepare_datasets"
        / "3-get-semantic.py"
    )

    broken_script.write_text(
        "import sys\nsys.stderr.write('CUDA out of memory')\nsys.exit(1)\n",
        encoding="utf-8",
    )

    run = TrainingPreprocessingService(
        app_root=ROOT,
        runtime_profiles=FakeRuntimeProfiles(
            runtime
        ),
    ).run(
        FakeVoice(),
        metadata,
        preprocessing_run_id="run_process_fail",
        output_root=root / "preprocess_fail",
    )

    assert run["ok"] is False
    assert run["run"]["blockers"][-1]["code"] == "PREPROCESS_CUDA_OOM"
