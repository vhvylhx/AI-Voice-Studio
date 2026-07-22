import os
import sys
from pathlib import Path


os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from PySide6.QtWidgets import QApplication  # noqa: E402

from models.voice_config import VoiceConfig  # noqa: E402
from services.engine_capability_router import EngineCapabilityRouter  # noqa: E402
from services.language_detection_service import LanguageDetectionService  # noqa: E402
from services.local_api_service import LocalApiService  # noqa: E402
from services.vietnamese_engine_evaluation_service import (  # noqa: E402
    VietnameseEngineEvaluationService,
)
from services.voice_catalog_service import VoiceCatalogService  # noqa: E402
from services.voice_service import VoiceService  # noqa: E402
from widgets.generate_options_panel import GenerateOptionsPanel  # noqa: E402
from widgets.voice_detail import VoiceDetail  # noqa: E402


def app():

    return QApplication.instance() or QApplication(
        []
    )


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


def test_all_checkbox_ticks_all_six_languages(tmp_path):

    app()
    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    widget = VoiceDetail()
    widget.load(
        voice
    )

    captured = []
    widget.language_selection_changed.connect(
        lambda codes, allow_all: captured.append(
            (
                codes,
                allow_all,
            )
        )
    )

    widget.all_languages_checkbox.setChecked(
        True
    )

    assert captured[-1] == (
        [
            "vi",
            "zh",
            "en",
            "ja",
            "ko",
            "yue",
        ],
        True,
    )


def test_unchecking_one_language_makes_all_false(tmp_path):

    app()
    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    voice = service.set_enabled_languages(
        voice.id,
        [],
        allow_all=True,
    )

    widget = VoiceDetail()
    widget.load(
        voice
    )

    widget.language_checkboxes[
        "en"
    ].setChecked(
        False
    )

    assert not widget.all_languages_checkbox.isChecked()
    assert "en" not in widget.checked_language_codes()


def test_service_does_not_save_empty_language_list(tmp_path):

    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )

    try:

        service.set_enabled_languages(
            voice.id,
            [],
        )

    except ValueError as exc:

        assert str(
            exc
        ) == "enabled_languages_required"

    else:

        raise AssertionError(
            "empty language list must fail"
        )


def test_legacy_voice_defaults_to_vietnamese_only():

    config = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "display_name": "Legacy",
        }
    )

    assert config.enabled_languages == [
        "vi",
    ]


def test_voice_detail_status_and_tooltip(tmp_path):

    app()
    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    router = EngineCapabilityRouter(
        voice_service=service
    )
    widget = VoiceDetail()
    widget.load(
        voice,
        router.voice_language_capabilities(
            voice.id
        ),
    )

    assert widget.language_status_labels[
        "vi"
    ].text() == "Chưa cấu hình"
    assert "không tự dịch" in widget.all_languages_checkbox.toolTip()


def test_generate_fixed_language_uses_only_enabled_language(tmp_path):

    app()
    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    service.set_enabled_languages(
        voice.id,
        [
            "vi",
            "en",
        ],
    )
    voice = service.find_by_id(
        voice.id
    )
    router = EngineCapabilityRouter(
        voice_service=service
    )
    panel = GenerateOptionsPanel()
    panel.load_language_capabilities(
        router.voice_language_capabilities(
            voice.id
        )
    )

    values = [
        panel.fixed_language_combo.itemData(
            index
        )
        for index in range(
            panel.fixed_language_combo.count()
        )
    ]

    assert values == [
        "vi",
        "en",
    ]


def test_route_blocked_for_not_ready_language(tmp_path):

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


def test_mixed_preview_preserves_order(tmp_path):

    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    service.set_enabled_languages(
        voice.id,
        [],
        allow_all=True,
    )
    detector = LanguageDetectionService()
    router = EngineCapabilityRouter(
        voice_service=service,
        language_detector=detector,
    )

    result = router.route_text(
        voice.id,
        "Xin chào. Hello.",
    )

    assert [
        item[
            "language_code"
        ]
        for item in result[
            "segments"
        ]
    ] == [
        "vi",
        "en",
    ]


def test_display_name_is_not_engine_evaluation_key(tmp_path):

    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    before = service.find_by_id(
        voice.id
    )
    service.rename_display_name(
        voice.id,
        "Tên mới"
    )
    after = service.find_by_id(
        voice.id
    )

    assert before.id == after.id
    assert before.path == after.path


def test_low_resource_profile_and_no_parallel_gpu_engines():

    profile = VietnameseEngineEvaluationService().low_resource_profile()

    assert profile[
        "gpu_concurrency"
    ] == 1
    assert not profile[
        "allow_parallel_gpu_engines"
    ]


def test_license_gate_blocks_missing_or_noncommercial_model_license():

    records = {
        item.engine_id: item
        for item in VietnameseEngineEvaluationService().candidates()
    }

    assert records[
        "f5_tts_vietnamese"
    ].license_audit[
        "status"
    ] == "BLOCKED"
    assert records[
        "vixtts"
    ].license_audit[
        "status"
    ] == "LICENSE_UNVERIFIED"


def test_source_license_does_not_replace_model_license():

    f5 = [
        item
        for item in VietnameseEngineEvaluationService().candidates()
        if item.engine_id == "f5_tts_vietnamese"
    ][
        0
    ]

    assert f5.source_license == "MIT for upstream SWivid/F5-TTS"
    assert "CC-BY-NC" in f5.model_checkpoint_license


def test_download_plan_requires_revision_size_target_and_permission():

    plans = VietnameseEngineEvaluationService().download_plans()[
        "items"
    ]

    for plan in plans:

        assert plan[
            "revision"
        ]
        assert plan[
            "expected_size"
        ]
        assert plan[
            "target_cache"
        ]
        assert plan[
            "requires_user_permission"
        ]
        assert not plan[
            "ready_to_download"
        ]


def test_canary_is_limited_and_non_production():

    canary = VietnameseEngineEvaluationService().local_canary_plan()

    assert canary[
        "max_processes_per_engine"
    ] == 1
    assert not canary[
        "production_write"
    ]
    assert not canary[
        "voice_binding_changed"
    ]


def test_evaluation_does_not_unlock_readiness():

    summary = VietnameseEngineEvaluationService().summary()

    assert not summary[
        "readiness_effect"
    ][
        "generate_readiness_unlocked"
    ]
    assert summary[
        "readiness_effect"
    ][
        "vietnamese_engine_binding"
    ] == "BLOCKED_PENDING_ENGINE_SELECTION"


def test_candidate_score_not_measured_without_local_audio():

    summary = VietnameseEngineEvaluationService().summary()

    for record in summary[
        "items"
    ]:

        statuses = {
            item[
                "status"
            ]
            for item in record[
                "scorecard"
            ]
        }

        assert "MEASURED" not in statuses


def test_vixtts_is_not_default_even_if_available():

    service = VietnameseEngineEvaluationService()

    assert service.recommendation() != "VIXTTS_PRIMARY_CANDIDATE"


def test_api_evaluation_smoke(tmp_path):

    voice_service = build_voice_service(
        tmp_path
    )
    voice_service.create(
        "Thu Minh"
    )
    api = LocalApiService(
        config={
            "local_api_enabled": True,
            "local_api_token": "token",
        },
        voice_catalog=VoiceCatalogService(
            voice_service=voice_service
        ),
    )

    response = api.route(
        "GET",
        "/api/v1/vietnamese-engines/evaluation",
        {},
    )

    assert response[
        "body"
    ][
        "status"
    ] == "STATIC_AUDIT_COMPLETE"


def test_all_mode_persisted_by_voice_id(tmp_path):

    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    updated = service.set_enabled_languages(
        voice.id,
        [],
        allow_all=True,
    )

    assert updated.config.language_selection_mode == "all"
    assert len(
        updated.config.enabled_languages
    ) == 6


def test_selected_mode_after_partial_language_save(tmp_path):

    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    updated = service.set_enabled_languages(
        voice.id,
        [
            "vi",
            "ja",
        ],
    )

    assert updated.config.language_selection_mode == "selected"


def test_api_rejects_empty_language_selection(tmp_path):

    voice_service = build_voice_service(
        tmp_path
    )
    voice = voice_service.create(
        "Thu Minh"
    )
    api = LocalApiService(
        config={
            "local_api_enabled": True,
            "local_api_token": "token",
        },
        voice_catalog=VoiceCatalogService(
            voice_service=voice_service
        ),
    )

    response = api.route(
        "PATCH",
        f"/api/v1/voices/{voice.id}/enabled-languages",
        {
            "language_codes": [],
        },
    )

    assert response[
        "status_code"
    ] == 400


def test_generate_panel_preview_route_keeps_blocker(tmp_path):

    app()
    service = build_voice_service(
        tmp_path
    )
    voice = service.create(
        "Thu Minh"
    )
    router = EngineCapabilityRouter(
        voice_service=service
    )
    panel = GenerateOptionsPanel()
    panel.direct_text.setPlainText(
        "Xin chào."
    )

    result = panel.preview_language_routes(
        router,
        voice.id,
    )

    assert result[
        "segments"
    ][
        0
    ][
        "route"
    ][
        "status"
    ] == "BLOCKED"


def test_evaluation_recommends_vieneu_not_ready_state():

    summary = VietnameseEngineEvaluationService().summary()

    assert summary[
        "selection_result"
    ] == "VIENEU_PRIMARY_CANDIDATE"
    assert summary[
        "readiness_effect"
    ][
        "vietnamese_engine_binding"
    ] == "BLOCKED_PENDING_ENGINE_SELECTION"


def test_api_download_plan_and_low_resource_endpoints(tmp_path):

    voice_service = build_voice_service(
        tmp_path
    )
    voice_service.create(
        "Thu Minh"
    )
    api = LocalApiService(
        config={
            "local_api_enabled": True,
            "local_api_token": "token",
        },
        voice_catalog=VoiceCatalogService(
            voice_service=voice_service
        ),
    )

    plans = api.route(
        "GET",
        "/api/v1/vietnamese-engines/download-plans",
        {},
    )
    profile = api.route(
        "GET",
        "/api/v1/vietnamese-engines/low-resource-profile",
        {},
    )

    assert plans[
        "body"
    ][
        "items"
    ]
    assert profile[
        "body"
    ][
        "profile_id"
    ] == "low_resource_safe"
