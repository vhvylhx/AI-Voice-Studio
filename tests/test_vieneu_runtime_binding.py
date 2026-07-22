import os
import subprocess
import sys
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

from engines.vieneu_tts_adapter import VieNeuTTSAdapter
from engines.vieneu_tts_engine import VieNeuTTSEngine
from models.generate_config import GenerateRequest
from models.generate_config import GenerateResult
from models.generate_config import GenerateSelectionConfig
from models.voice_config import VoiceConfig
from services.job_handler_registry import JobHandlerRegistry
from services.job_log_service import JobLogService
from services.job_queue_service import JobQueueService
from services.job_repository import JobRepository
from services.job_runner import JobRunner
from services.generate_pipeline_service import GeneratePipelineService
from services.audio_merge_service import AudioMergeService


class FakeRunner:

    def __init__(
        self,
        returncode=0,
        stdout='{"ready": true, "status": "READY"}',
        stderr="",
        create_output=False,
        returncodes=None,
    ):

        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.create_output = create_output
        self.returncodes = list(
            returncodes or []
        )
        self.calls = []

    def __call__(
        self,
        command,
        **kwargs,
    ):

        self.calls.append(
            {
                "command": command,
                "kwargs": kwargs,
            }
        )

        if (
            self.create_output
            and "--output-file" in command
        ):

            output = Path(
                command[
                    command.index(
                        "--output-file"
                    )
                    + 1
                ]
            )
            output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            output.write_bytes(
                b"RIFF" + b"x" * 64
            )

        returncode = (
            self.returncodes.pop(
                0
            )
            if self.returncodes
            else self.returncode
        )

        return subprocess.CompletedProcess(
            command,
            returncode,
            self.stdout,
            self.stderr,
        )


class AvailableEngine:

    def is_available(
        self,
    ):

        return True


class SelectableManager:

    def __init__(
        self,
    ):

        self.selected = ""

    def get(
        self,
        engine_id,
    ):

        if engine_id == "vieneu":

            return AvailableEngine()

        return None

    def select(
        self,
        engine_id,
    ):

        self.selected = engine_id


def make_runtime_tree(
    tmp_path,
):

    runtime_python = tmp_path / "runtime" / "python.exe"
    model_root = tmp_path / "models" / "vieneu"
    codec_root = tmp_path / "codecs" / "codec"
    onnx_dir = model_root / "onnx_int8"

    runtime_python.parent.mkdir(
        parents=True
    )
    runtime_python.write_text(
        "python",
        encoding="utf-8",
    )

    onnx_dir.mkdir(
        parents=True
    )
    codec_root.mkdir(
        parents=True
    )

    for name in (
        "vieneu_prefill.onnx",
        "vieneu_decode_step.onnx",
        "vieneu_acoustic_cached.onnx",
        "vieneu_v3_heads.npz",
    ):

        (
            onnx_dir
            / name
        ).write_bytes(
            b"x"
        )

    return runtime_python, model_root, codec_root


def make_adapter(
    tmp_path,
    runner=None,
):

    runtime_python, model_root, codec_root = make_runtime_tree(
        tmp_path
    )

    cli = tmp_path / "vieneu_runtime_cli.py"
    cli.write_text(
        "print('ok')",
        encoding="utf-8",
    )

    adapter = VieNeuTTSAdapter(
        app_root=tmp_path,
        runtime_python=runtime_python,
        model_root=model_root,
        codec_root=codec_root,
        runner=runner or FakeRunner(),
    )
    adapter.cli_script = cli

    return adapter


def test_vieneu_availability_probe_ready_uses_runtime_probe(tmp_path):

    runner = FakeRunner(
        stdout='{"ready": true, "status": "READY", "backend": "CPU_ONNX"}'
    )
    adapter = make_adapter(
        tmp_path,
        runner=runner,
    )

    status = adapter.availability_probe()

    assert status["ready"] is True
    assert status["backend"] == "CPU_ONNX"
    assert runner.calls[0]["command"][0] == str(
        adapter.runtime_python
    )
    assert "--probe" in runner.calls[0]["command"]


def test_vieneu_runtime_missing_is_unavailable(tmp_path):

    adapter = VieNeuTTSAdapter(
        app_root=tmp_path,
        runtime_python=tmp_path / "missing" / "python.exe",
        model_root=tmp_path / "missing_model",
        codec_root=tmp_path / "missing_codec",
        runner=FakeRunner(),
    )

    status = adapter.availability_probe()

    assert status["ready"] is False
    assert status["status"] == "UNAVAILABLE"
    assert "runtime_python" in status["missing"]


def test_vieneu_model_missing_is_unavailable(tmp_path):

    runtime = tmp_path / "runtime" / "python.exe"
    runtime.parent.mkdir(
        parents=True
    )
    runtime.write_text(
        "python",
        encoding="utf-8",
    )
    codec = tmp_path / "codec"
    codec.mkdir()

    adapter = VieNeuTTSAdapter(
        app_root=tmp_path,
        runtime_python=runtime,
        model_root=tmp_path / "missing_model",
        codec_root=codec,
        runner=FakeRunner(),
    )

    status = adapter.availability_probe()

    assert status["ready"] is False
    assert "model_root" in status["missing"]


def test_generate_vi_resolves_to_vieneu_without_gpt_models(tmp_path):

    ref = tmp_path / "ref.wav"
    ref.write_bytes(
        b"ref"
    )
    out = tmp_path / "out"
    out.mkdir()

    voice = SimpleNamespace(
        id="voice_vi",
        config=VoiceConfig(
            voice_id="voice_vi",
            language="vi",
            engine="gpt_sovits",
            reference_audio=str(
                ref
            ),
            reference_text="Xin chao.",
        ),
        variants=[
            {
                "id": "default",
                "name": "Mac dinh",
            }
        ],
    )
    request = GenerateRequest(
        text="Xin chao",
        selection=GenerateSelectionConfig(
            selected_variant_id="default",
            output_folder=str(
                out
            ),
            output_name="hello",
        ),
    )
    manager = SelectableManager()
    service = GeneratePipelineService(
        engine_manager=manager,
    )

    errors = service.validate_request(
        request,
        voice,
    )

    assert "voice_model_missing" not in errors
    assert "vieneu_tts_unavailable" not in errors


def test_vieneu_subprocess_command_and_scoped_env(tmp_path):

    runner = FakeRunner(
        create_output=True
    )
    adapter = make_adapter(
        tmp_path,
        runner=runner,
    )
    text_file = tmp_path / "text.txt"
    ref = tmp_path / "ref.wav"
    output = tmp_path / "out.wav"
    text_file.write_text(
        "Xin chao",
        encoding="utf-8",
    )
    ref.write_bytes(
        b"ref"
    )
    before = os.environ.copy()

    adapter.generate(
        text_file=text_file,
        output_file=output,
        reference_audio=ref,
        reference_text="Xin chao.",
    )

    generate_call = runner.calls[-1]
    command = generate_call["command"]
    env = generate_call["kwargs"]["env"]

    assert command[0] == str(
        adapter.runtime_python
    )
    assert str(
        adapter.cli_script
    ) in command
    assert "--reference-audio" in command
    assert "--output-file" in command
    assert env["CUDA_VISIBLE_DEVICES"] == ""
    assert env["HF_HUB_OFFLINE"] == "1"
    assert os.environ == before


def test_vieneu_non_zero_exit_fails(tmp_path):

    adapter = make_adapter(
        tmp_path,
        runner=FakeRunner(
            returncodes=[
                0,
                7,
            ],
            stderr="boom",
        ),
    )
    text_file = tmp_path / "text.txt"
    ref = tmp_path / "ref.wav"
    text_file.write_text(
        "Xin chao",
        encoding="utf-8",
    )
    ref.write_bytes(
        b"ref"
    )

    try:

        adapter.generate(
            text_file=text_file,
            output_file=tmp_path / "out.wav",
            reference_audio=ref,
            reference_text="Xin chao.",
        )

        assert False

    except RuntimeError as exc:

        assert "exit 7" in str(
            exc
        )


def test_vieneu_output_missing_fails(tmp_path):

    adapter = make_adapter(
        tmp_path,
        runner=FakeRunner(),
    )
    text_file = tmp_path / "text.txt"
    ref = tmp_path / "ref.wav"
    text_file.write_text(
        "Xin chao",
        encoding="utf-8",
    )
    ref.write_bytes(
        b"ref"
    )

    try:

        adapter.generate(
            text_file=text_file,
            output_file=tmp_path / "out.wav",
            reference_audio=ref,
            reference_text="Xin chao.",
        )

        assert False

    except RuntimeError as exc:

        assert "không tạo WAV" in str(
            exc
        )


def test_vieneu_reference_missing_fails(tmp_path):

    adapter = make_adapter(
        tmp_path,
        runner=FakeRunner(),
    )
    text_file = tmp_path / "text.txt"
    text_file.write_text(
        "Xin chao",
        encoding="utf-8",
    )

    try:

        adapter.generate(
            text_file=text_file,
            output_file=tmp_path / "out.wav",
            reference_audio=tmp_path / "missing.wav",
            reference_text="Xin chao.",
        )

        assert False

    except RuntimeError as exc:

        assert "reference audio" in str(
            exc
        )


def test_vieneu_engine_does_not_fallback_to_gpt_sovits(tmp_path):

    class MissingAdapter:

        runtime_python = tmp_path / "runtime" / "python.exe"
        model_root = tmp_path / "model"

        def availability_probe(
            self,
        ):

            return {
                "ready": False,
                "status": "UNAVAILABLE",
                "reason": "vieneu_runtime_missing",
            }

    engine = VieNeuTTSEngine(
        adapter=MissingAdapter()
    )

    assert engine.is_available() is False

    try:

        engine.generate(
            text_file=tmp_path / "text.txt",
            output_file=tmp_path / "out.wav",
            voice=SimpleNamespace(
                config=VoiceConfig(
                    reference_audio="",
                    reference_text="",
                )
            ),
        )

        assert False

    except RuntimeError as exc:

        assert "VieNeu-TTS runtime" in str(
            exc
        )
        assert "GPT-SoVITS" not in str(
            exc
        )


def test_job_runner_generate_execute_calls_generate_pipeline(tmp_path):

    class FakePipeline:

        def __init__(
            self,
        ):

            self.calls = []

        def run(
            self,
            request,
            voice,
        ):

            self.calls.append(
                {
                    "request": request,
                    "voice": voice,
                }
            )

            return GenerateResult(
                ok=True,
                output_file=str(
                    tmp_path / "out.wav"
                ),
            )

    pipeline = FakePipeline()
    app_context = SimpleNamespace(
        generate_pipeline_service=pipeline
    )

    repository = JobRepository(
        tmp_path / "jobs"
    )
    queue = JobQueueService(
        repository
    )
    runner = JobRunner(
        repository=repository,
        queue_service=queue,
        handler_registry=JobHandlerRegistry(),
        log_service=JobLogService(
            repository
        ),
        app_context=app_context,
    )

    request = GenerateRequest(
        text="Xin chao",
        selection=GenerateSelectionConfig(
            selected_variant_id="default",
            output_folder=str(
                tmp_path
            ),
            output_name="out",
        ),
    )
    voice_config = VoiceConfig(
        voice_id="voice_vi",
        language="vi",
        engine="vieneu",
        reference_audio=str(
            tmp_path / "ref.wav"
        ),
        reference_text="Xin chao.",
    )

    job = queue.enqueue_new(
        "generate_execute",
        payload={
            "request": {
                "text": request.text,
                "selection": {
                    **request.selection.__dict__,
                    "speed": request.selection.speed.__dict__,
                },
                "audio_profile": request.audio_profile.__dict__,
            },
            "voice": {
                "id": "voice_vi",
                "config": voice_config.to_dict(),
            },
        },
    )

    result = runner.run_next()

    assert result.job_id == job.job_id
    assert result.state == "completed"
    assert result.result["ok"] is True
    assert pipeline.calls[0]["request"].text == "Xin chao"
    assert pipeline.calls[0]["voice"].config.engine == "vieneu"


def test_audio_merge_concat_uses_absolute_chunk_paths(tmp_path):

    class CaptureMerge(AudioMergeService):

        def __init__(
            self,
        ):

            super().__init__(
                ffmpeg="ffmpeg"
            )
            self.commands = []

        def run(
            self,
            command,
        ):

            self.commands.append(
                command
            )
            Path(
                command[-1]
            ).write_bytes(
                b"RIFF" + b"x" * 64
            )

    chunk = tmp_path / "temp" / "generate" / "job" / "chunks" / "chunk.wav"
    chunk.parent.mkdir(
        parents=True
    )
    chunk.write_bytes(
        b"RIFF" + b"x" * 64
    )
    work = tmp_path / "temp" / "generate" / "job" / "merge"
    output = tmp_path / "out.wav"
    service = CaptureMerge()

    service.merge(
        chunk_files=[
            chunk,
        ],
        output_file=output,
        work_dir=work,
    )

    concat_text = (
        work
        / "concat.txt"
    ).read_text(
        encoding="utf-8"
    )

    assert chunk.resolve().as_posix() in concat_text
