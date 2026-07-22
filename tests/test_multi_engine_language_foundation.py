import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from models.generate_pipeline_foundation import GenerateSettings  # noqa: E402
from models.style_profile import StyleProfile  # noqa: E402
from models.voice_config import VoiceConfig  # noqa: E402
from services.engine_capability_router import EngineCapabilityRouter  # noqa: E402
from services.generate_repository import GenerateRepository  # noqa: E402
from services.generate_session_service import GenerateSessionService  # noqa: E402
from services.language_catalog_service import LanguageCatalogService  # noqa: E402
from services.language_detection_service import LanguageDetectionService  # noqa: E402
from services.local_api_service import LocalApiService  # noqa: E402
from services.voice_catalog_service import VoiceCatalogService  # noqa: E402
from services.voice_service import VoiceService  # noqa: E402


def build_voice_service(
    tmp_path,
):

    service = VoiceService()

    service._root = tmp_path / "voices"

    service._root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return service


def test_language_catalog_and_gpt_sovits_mapping():

    catalog = LanguageCatalogService()

    assert catalog.normalize(
        "jp"
    ) == "ja"

    assert catalog.supported_codes() == [
        "vi",
        "zh",
        "en",
        "ja",
        "ko",
        "yue",
    ]

    assert catalog.gpt_sovits_mapping() == {
        "zh": "all_zh",
        "en": "en",
        "ja": "all_ja",
        "ko": "all_ko",
        "yue": "all_yue",
    }


def test_legacy_voice_migration_keeps_vi_only_and_blocks_gpt_fallback():

    config = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "display_name": "Thu Minh",
            "language": "vi",
            "engine": "gpt_sovits",
        }
    )

    assert config.enabled_languages == [
        "vi",
    ]

    assert config.engine_bindings[
        "vi"
    ][
        "engine_id"
    ] == "vietnamese_engine"


def test_enabled_language_selection_and_all_checkbox(tmp_path):

    service = build_voice_service(
        tmp_path
    )

    voice = service.create(
        "Thu Minh"
    )

    selected = service.set_enabled_languages(
        voice.id,
        [
            "vi",
            "en",
            "jp",
        ],
    )

    assert selected.config.language_selection_mode == "selected"
    assert selected.config.enabled_languages == [
        "vi",
        "en",
        "ja",
    ]

    all_enabled = service.set_enabled_languages(
        voice.id,
        [],
        allow_all=True,
    )

    assert all_enabled.config.language_selection_mode == "all"
    assert all_enabled.config.enabled_languages == [
        "vi",
        "zh",
        "en",
        "ja",
        "ko",
        "yue",
    ]


def test_language_detection_mixed_text_preserves_sentence_routes():

    detector = LanguageDetectionService()

    segments = detector.segment_text(
        "Xin chào OpenAI. Hello everyone. こんにちは。"
    )

    assert [
        item.language_code
        for item in segments
    ] == [
        "vi",
        "en",
        "ja",
    ]


def test_router_blocks_vi_without_vietnamese_engine_and_no_wrong_fallback(
    tmp_path,
):

    service = build_voice_service(
        tmp_path
    )

    voice = service.create(
        "Thu Minh"
    )

    router = EngineCapabilityRouter(
        voice_service=service
    )

    route = router.route_language(
        voice,
        "vi",
    )

    assert route.status == "BLOCKED"
    assert route.reason == "VIETNAMESE_ENGINE_UNCONFIGURED"
    assert "vietnamese_engine_unconfigured" in route.blockers

    service.update_engine_binding(
        voice.id,
        "vi",
        {
            "engine_id": "gpt_sovits",
            "runtime_profile_id": "runtime",
            "model_binding": {},
            "reference_binding": {},
        },
    )

    voice = service.find_by_id(
        voice.id
    )

    route = router.route_language(
        voice,
        "vi",
    )

    assert route.reason == "VI_REQUIRES_VIETNAMESE_ENGINE"


def test_router_blocks_language_not_enabled_and_missing_assets(tmp_path):

    service = build_voice_service(
        tmp_path
    )

    voice = service.create(
        "Thu Minh"
    )

    router = EngineCapabilityRouter(
        voice_service=service
    )

    assert router.route_language(
        voice,
        "en",
    ).reason == "LANGUAGE_NOT_ENABLED"

    service.set_enabled_languages(
        voice.id,
        [
            "en",
        ],
    )

    service.update_engine_binding(
        voice.id,
        "en",
        {
            "engine_id": "gpt_sovits",
            "runtime_profile_id": "runtime",
        },
    )

    voice = service.find_by_id(
        voice.id
    )

    route = router.route_language(
        voice,
        "en",
    )

    assert route.status == "BLOCKED"
    assert "gpt_model_missing" in route.blockers


def test_language_fingerprint_is_language_scoped_and_display_name_safe(
    tmp_path,
):

    service = build_voice_service(
        tmp_path
    )

    voice = service.create(
        "Thu Minh"
    )

    model = voice.path / "model"
    dataset = voice.path / "dataset"

    gpt = model / "gpt.ckpt"
    sovits = model / "sovits.pth"
    ref = dataset / "ref.wav"

    for path in [
        gpt,
        sovits,
        ref,
    ]:

        path.write_text(
            "mock",
            encoding="utf-8",
        )

    for code in [
        "en",
        "ja",
    ]:

        service.update_engine_binding(
            voice.id,
            code,
            {
                "engine_id": "gpt_sovits",
                "runtime_profile_id": "runtime",
                "model_binding": {
                    "gpt_model": str(
                        gpt
                    ),
                    "sovits_model": str(
                        sovits
                    ),
                },
                "reference_binding": {
                    "reference_audio": str(
                        ref
                    ),
                    "reference_text": "Hello.",
                },
                "inference_verified": True,
            },
        )

    service.set_enabled_languages(
        voice.id,
        [
            "en",
            "ja",
        ],
    )

    voice = service.find_by_id(
        voice.id
    )

    router = EngineCapabilityRouter(
        voice_service=service
    )

    en = router.route_language(
        voice,
        "en",
    ).fingerprint

    ja = router.route_language(
        voice,
        "ja",
    ).fingerprint

    service.rename_display_name(
        voice.id,
        "Thu Minh New",
    )

    renamed = service.find_by_id(
        voice.id
    )

    assert en != ja
    assert router.route_language(
        renamed,
        "en",
    ).fingerprint == en


def test_style_profile_language_compatibility_migration():

    profile = StyleProfile.from_dict(
        {
            "style_profile_id": "style_story",
            "display_name": "Kể chuyện",
        }
    )

    assert "supported_languages" in profile.compatibility
    assert "vi" in profile.compatibility[
        "supported_languages"
    ]


def test_local_api_language_endpoints(tmp_path):

    service = build_voice_service(
        tmp_path
    )

    voice = service.create(
        "Thu Minh"
    )

    api = LocalApiService(
        config={
            "local_api_enabled": True,
            "local_api_token": "token",
        },
        voice_catalog=VoiceCatalogService(
            voice_service=service
        ),
    )

    languages = api.route(
        "GET",
        "/api/v1/languages",
        {},
    )

    assert languages[
        "body"
    ][
        "primary_language"
    ] == "vi"

    updated = api.route(
        "PATCH",
        f"/api/v1/voices/{voice.id}/enabled-languages",
        {
            "language_codes": [
                "vi",
                "en",
            ]
        },
    )

    assert updated[
        "body"
    ][
        "enabled_languages"
    ] == [
        "vi",
        "en",
    ]

    planned = api.route(
        "POST",
        "/api/v1/generate/language-plan",
        {
            "voice_id": voice.id,
            "text": "Hello everyone.",
        },
    )

    assert planned[
        "body"
    ][
        "segments"
    ][
        0
    ][
        "route"
    ][
        "reason"
    ] in {
        "GPT_MODEL_MISSING",
        "LANGUAGE_ENGINE_UNCONFIGURED",
    }


def test_generate_plan_freezes_language_route(tmp_path):

    voice_service = build_voice_service(
        tmp_path
    )

    voice = voice_service.create(
        "Thu Minh"
    )

    router = EngineCapabilityRouter(
        voice_service=voice_service
    )

    service = GenerateSessionService(
        repository=GenerateRepository(
            root=tmp_path / "generate"
        ),
        settings=GenerateSettings(
            max_unit_characters=80
        ),
        language_router=router,
    )

    result = service.create_session(
        {
            "project_id": "project_demo",
            "voice_id": voice.id,
            "text": "Xin chào. Hello everyone.",
            "selection": {
                "voice_id": voice.id,
            },
            "output": {
                "output_folder": str(
                    tmp_path / "out"
                ),
                "output_name": "demo",
            },
        }
    )

    plan = result[
        "plan"
    ]

    assert plan[
        "units"
    ][
        0
    ][
        "language_code"
    ]

    assert "route_status" in plan[
        "units"
    ][
        0
    ]
