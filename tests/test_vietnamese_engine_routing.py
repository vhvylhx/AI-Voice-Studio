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

from engines.gpt_sovits_engine import GPTSoVITSEngine
from engines.vieneu_tts_engine import VieNeuTTSEngine
from models.generate_config import GenerateRequest
from models.generate_config import GenerateSelectionConfig
from models.voice_config import VoiceConfig
from services.engine_language_router import EngineLanguageRouter
from services.generate_pipeline_service import GeneratePipelineService
from services.voice_service import VoiceService


class UnavailableVieNeuEngine:

    def is_available(
        self,
    ):

        return False


class FakeEngineManager:

    def __init__(
        self,
    ):

        self.engines = {
            "gpt_sovits": GPTSoVITSEngine(),
            "vieneu": UnavailableVieNeuEngine(),
        }
        self.selected = ""

    def get(
        self,
        engine_id,
    ):

        return self.engines.get(
            engine_id
        )

    def select(
        self,
        engine_id,
    ):

        self.selected = engine_id


def make_voice(
    tmp_path,
    language="vi",
    engine="gpt_sovits",
):

    gpt = tmp_path / "model.ckpt"
    sovits = tmp_path / "model.pth"
    ref = tmp_path / "ref.wav"

    for file in (
        gpt,
        sovits,
        ref,
    ):

        file.write_bytes(
            b"x"
        )

    config = VoiceConfig(
        voice_id="voice_1",
        language=language,
        engine=engine,
        gpt_model=str(
            gpt
        ),
        sovits_model=str(
            sovits
        ),
        reference_audio=str(
            ref
        ),
        reference_text="Xin chao.",
    )

    return SimpleNamespace(
        id="voice_1",
        config=config,
        variants=[
            {
                "id": "default",
                "name": "Mac dinh",
            }
        ],
    )


def test_vietnamese_language_routes_only_to_vieneu():

    router = EngineLanguageRouter()

    assert router.resolve_engine(
        "vi",
        "gpt_sovits",
    ) == "vieneu"
    assert router.validate_binding(
        "vi",
        "gpt_sovits",
    ) == [
        "vietnamese_requires_vieneu_tts"
    ]


def test_gpt_sovits_metadata_does_not_advertise_vi():

    info = GPTSoVITSEngine().info()

    assert "vi" not in info.supported_languages


def test_voice_default_engine_is_vieneu():

    config = VoiceConfig()

    assert config.language == "vi"
    assert config.engine == "vieneu"


def test_voice_service_rejects_gpt_sovits_binding_for_vi(tmp_path):

    voice = make_voice(
        tmp_path,
        language="vi",
        engine="vieneu",
    )

    try:

        VoiceService.__new__(
            VoiceService
        ).link_engine(
            voice,
            "gpt_sovits",
        )

        assert False

    except RuntimeError as exc:

        assert "vietnamese_requires_vieneu_tts" in str(
            exc
        )


def test_generate_validation_reports_vieneu_unavailable_not_gpt_fallback(tmp_path):

    voice = make_voice(
        tmp_path,
        language="vi",
        engine="gpt_sovits",
    )
    out = tmp_path / "out"
    out.mkdir()
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
    manager = FakeEngineManager()
    service = GeneratePipelineService(
        engine_manager=manager,
    )

    errors = service.validate_request(
        request,
        voice,
    )

    assert "vieneu_tts_unavailable" in errors
    assert "vietnamese_requires_vieneu_tts" not in errors
    assert manager.selected == ""
