import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.generate_config import (  # noqa: E402
    GENERATE_MODE_AI_STYLE,
    GENERATE_MODE_STANDARD,
    GenerateAudioProfile,
    GenerateRequest,
    GenerateSelectionConfig,
    SpeedProfile,
)
from models.voice_config import VoiceConfig  # noqa: E402
from services.generate_pipeline_service import (  # noqa: E402
    GeneratePipelineService,
)


class MockMergeService:

    def output_suffix(
        self,
        output_format,
    ):

        return f".{output_format}"

    def merge(
        self,
        chunk_files,
        output_file,
        work_dir,
        profile=None,
    ):

        output = Path(
            output_file
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(
            b"merged"
        )

        return output


class MockEngineManager:

    def __init__(self):

        self.calls = []

    def generate(
        self,
        **kwargs,
    ):

        output = Path(
            kwargs["output_file"]
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_bytes(
            b"chunk"
        )

        self.calls.append(
            kwargs
        )

        return output


def clean_cache(name):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(
            root
        )

    root.mkdir(
        parents=True,
    )

    return root


def make_voice(root):

    gpt = root / "model.ckpt"

    sovits = root / "model.pth"

    ref = root / "ref.wav"

    for file in [
        gpt,
        sovits,
        ref,
    ]:

        file.write_bytes(
            b"x"
        )

    config = VoiceConfig(
        voice_id="0001",
        gpt_model=str(
            gpt
        ),
        sovits_model=str(
            sovits
        ),
        reference_audio=str(
            ref
        ),
        reference_text="Xin chào.",
        default_style_id="natural",
    )

    return SimpleNamespace(
        id="0001",
        name="Voice",
        config=config,
        variants=config.variants,
    )


def make_request(
    root,
    mode=GENERATE_MODE_STANDARD,
    output_format="wav",
):

    selection = GenerateSelectionConfig(
        mode=mode,
        voice_id="0001",
        selected_variant_id="default",
        allow_all_variants=True,
        allow_all_styles=True,
        output_folder=str(
            root / "output"
        ),
        output_name="demo",
        output_format=output_format,
        mp3_bitrate_kbps=192,
        speed=SpeedProfile(
            speed=1.0,
        ),
    )

    return GenerateRequest(
        text="Xin chào. Đây là câu thứ hai.",
        selection=selection,
        project_id="project1",
        audio_profile=GenerateAudioProfile(
            output_format=output_format,
            mp3_bitrate_kbps=192,
        ),
    )


def test_voice_model_missing_blocks_generate():

    root = clean_cache(
        "test_generate_missing_model"
    )

    voice = make_voice(
        root
    )

    voice.config.language = "en"
    voice.config.engine = "gpt_sovits"
    voice.config.gpt_model = ""

    request = make_request(
        root
    )

    (root / "output").mkdir()

    service = GeneratePipelineService(
        engine_manager=MockEngineManager(),
        merge_service=MockMergeService(),
    )

    result = service.run(
        request,
        voice,
    )

    assert not result.ok
    assert "voice_model_missing" in result.errors
    assert not (
        root / "output" / "demo.wav"
    ).exists()


def test_standard_mode_generates_wav_report_and_progress():

    root = clean_cache(
        "test_generate_standard"
    )

    voice = make_voice(
        root
    )

    request = make_request(
        root,
        mode=GENERATE_MODE_STANDARD,
    )

    (root / "output").mkdir()

    engine = MockEngineManager()

    service = GeneratePipelineService(
        engine_manager=engine,
        merge_service=MockMergeService(),
    )

    result = service.run(
        request,
        voice,
    )

    assert result.ok
    assert Path(
        result.output_file
    ).suffix == ".wav"
    assert Path(
        result.output_file
    ).exists()
    assert result.report["chunk_count"] >= 1
    assert service.progress_events
    assert engine.calls[0]["variant"] == "default"


def test_ai_style_stays_in_scope_and_mp3_output():

    root = clean_cache(
        "test_generate_ai_style"
    )

    voice = make_voice(
        root
    )

    request = make_request(
        root,
        mode=GENERATE_MODE_AI_STYLE,
        output_format="mp3",
    )

    request.selection.allowed_variant_ids = [
        "story",
    ]

    request.selection.allow_all_variants = False

    request.selection.allowed_style_ids = [
        "dramatic",
    ]

    request.selection.allow_all_styles = False

    (root / "output").mkdir()

    engine = MockEngineManager()

    service = GeneratePipelineService(
        engine_manager=engine,
        merge_service=MockMergeService(),
    )

    result = service.run(
        request,
        voice,
    )

    assert result.ok
    assert Path(
        result.output_file
    ).suffix == ".mp3"
    assert engine.calls[0]["variant"] == "story"
    assert engine.calls[0]["style"] == "dramatic"


def test_resume_does_not_generate_existing_chunk_again():

    root = clean_cache(
        "test_generate_resume"
    )

    voice = make_voice(
        root
    )

    request = make_request(
        root
    )

    request.job_id = "resume_job"

    (root / "output").mkdir()

    temp_chunk = (
        Path("temp")
        / "generate"
        / "resume_job"
        / "chunks"
        / "chunk_0001.wav"
    )

    if temp_chunk.exists():

        temp_chunk.unlink()

    temp_chunk.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_chunk.write_bytes(
        b"done"
    )

    engine = MockEngineManager()

    service = GeneratePipelineService(
        engine_manager=engine,
        merge_service=MockMergeService(),
    )

    result = service.run(
        request,
        voice,
    )

    assert result.ok
    assert engine.calls == []


def test_retry_limit_stops_job_without_final_output():

    root = clean_cache(
        "test_generate_retry_failed"
    )

    voice = make_voice(
        root
    )

    request = make_request(
        root
    )

    (root / "output").mkdir()

    def failing_adapter(
        chunk,
        text_file,
        output,
    ):

        raise RuntimeError(
            "boom"
        )

    service = GeneratePipelineService(
        engine_manager=MockEngineManager(),
        merge_service=MockMergeService(),
    )

    result = service.run(
        request,
        voice,
        adapter=failing_adapter,
    )

    assert not result.ok
    assert "chunk_failed" in result.errors[0]
    assert not (
        root / "output" / "demo.wav"
    ).exists()
