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

from models.local_api_config import LocalApiConfig  # noqa: E402
from models.voice_config import VoiceConfig  # noqa: E402
from repositories.style_profile_repository import StyleProfileRepository  # noqa: E402
from services.local_api_service import LocalApiService  # noqa: E402
from services.style_profile_service import StyleProfileService  # noqa: E402
from services.voice_catalog_service import VoiceCatalogService  # noqa: E402
from services.voice_publish_service import VoicePublishService  # noqa: E402
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

    voice = service.create(
        "Thu Minh"
    )

    return service, voice


def write_asset(
    path,
    text,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        text,
        encoding="utf-8",
    )

    return path


def test_voice_config_display_name_migrates_without_changing_id():

    config = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "language": "vi",
        }
    )

    assert config.voice_id == "0001"
    assert config.display_name == ""
    assert config.publish_validation_status == "unpublished"
    assert config.runtime_profile_id == ""
    assert config.variants[0]["id"] == "default"


def test_voice_rename_display_name_keeps_folder_id_and_assets(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    folder = voice.path
    voice_id = voice.id

    voice.config.gpt_model = str(
        folder / "model" / "gpt.ckpt"
    )
    voice.config.sovits_model = str(
        folder / "model" / "sovits.pth"
    )
    voice.config.reference_audio = str(
        folder / "dataset" / "ref.wav"
    )
    voice.config.reference_text = "Xin chào."
    service.save(
        voice
    )

    renamed = service.rename_display_name(
        voice_id,
        "Thu Minh mới",
    )

    assert renamed.id == voice_id
    assert renamed.path == folder
    assert renamed.name == "Thu Minh"
    assert renamed.display_name == "Thu Minh mới"
    assert service.exists(
        "Thu Minh"
    )
    assert not service.exists(
        "Thu Minh mới"
    )
    assert renamed.config.gpt_model.endswith(
        "gpt.ckpt"
    )
    assert renamed.config.reference_text == "Xin chào."


def test_find_by_id_supports_legacy_folder_name(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    found = service.find_by_id(
        voice.id
    )

    assert found is not None
    assert found.name == "Thu Minh"
    assert found.display_name == "Thu Minh"


def test_publish_requires_confirmation_and_does_not_fake_ready(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    gpt = write_asset(
        voice.model_dir / "run_1" / "model.ckpt",
        "gpt",
    )
    sovits = write_asset(
        voice.model_dir / "run_1" / "model.pth",
        "sovits",
    )
    ref = write_asset(
        tmp_path / "reference_vault" / "ref.wav",
        "wav",
    )

    publish = VoicePublishService(
        service
    )

    request = {
        "voice_id": voice.id,
        "training_run_id": "run_1",
        "gpt_model": str(
            gpt
        ),
        "sovits_model": str(
            sovits
        ),
        "reference_audio": str(
            ref
        ),
        "reference_text": "Xin chào.",
        "prompt_language": "vi",
        "text_language": "vi",
        "runtime_profile_id": "runtime_default",
    }

    validation = publish.validate_publish(
        request
    )

    assert validation.status == "ready"
    assert validation.validation_status == "ready"
    assert validation.fingerprint

    pending = publish.publish(
        request
    )

    assert pending.status == "confirmation_required"
    assert "confirm_publish_required" in pending.blockers

    loaded = service.find_by_id(
        voice.id
    )

    assert loaded.config.gpt_model == ""
    assert loaded.config.publish_validation_status == "unpublished"


def test_publish_writes_assets_atomically_after_confirmation(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    gpt = write_asset(
        voice.model_dir / "run_1" / "model.ckpt",
        "gpt",
    )
    sovits = write_asset(
        voice.model_dir / "run_1" / "model.pth",
        "sovits",
    )
    ref = write_asset(
        voice.path / "dataset" / "ref.wav",
        "wav",
    )

    result = VoicePublishService(
        service
    ).publish(
        {
            "voice_id": voice.id,
            "training_run_id": "run_1",
            "gpt_model": str(
                gpt
            ),
            "sovits_model": str(
                sovits
            ),
            "reference_audio": str(
                ref
            ),
            "reference_text": "Xin chào.",
            "runtime_profile_id": "runtime_default",
            "confirm_publish": True,
        }
    )

    loaded = service.find_by_id(
        voice.id
    )

    assert result.status == "published"
    assert loaded.config.gpt_model == str(
        gpt
    )
    assert loaded.config.sovits_model == str(
        sovits
    )
    assert loaded.config.reference_audio == str(
        ref
    )
    assert loaded.config.reference_text == "Xin chào."
    assert loaded.config.publish_id == result.publish_id
    assert loaded.config.training_status == "published"


def test_checkpoint_discovery_does_not_blind_pick_multiple(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    write_asset(
        voice.model_dir / "run_1" / "a.ckpt",
        "a",
    )
    write_asset(
        voice.model_dir / "run_1" / "b.ckpt",
        "b",
    )
    write_asset(
        voice.model_dir / "run_1" / "a.pth",
        "a",
    )

    result = VoicePublishService(
        service
    ).discover_checkpoints(
        voice.id,
        voice.model_dir,
    )

    assert result["ok"]
    assert len(
        result["gpt_candidates"]
    ) == 2
    assert result["suggestion"]["confidence"] == "manual_selection_required"
    assert "multiple_checkpoint_candidates" in result["warnings"]


def test_publish_fingerprint_ignores_display_name(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    gpt = write_asset(
        voice.model_dir / "run_1" / "model.ckpt",
        "gpt",
    )
    sovits = write_asset(
        voice.model_dir / "run_1" / "model.pth",
        "sovits",
    )
    ref = write_asset(
        voice.path / "dataset" / "ref.wav",
        "wav",
    )

    request = {
        "voice_id": voice.id,
        "training_run_id": "run_1",
        "gpt_model": str(
            gpt
        ),
        "sovits_model": str(
            sovits
        ),
        "reference_audio": str(
            ref
        ),
        "reference_text": "Xin chào.",
        "runtime_profile_id": "runtime_default",
    }

    publish = VoicePublishService(
        service
    )

    before = publish.validate_publish(
        request
    ).fingerprint

    service.rename_display_name(
        voice.id,
        "Tên mới",
    )

    after = publish.validate_publish(
        request
    ).fingerprint

    assert before == after


def test_style_profile_schema_and_variant_binding_are_model_free(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    style_service = StyleProfileService(
        repository=StyleProfileRepository(
            tmp_path / "style_profiles"
        ),
        voice_service=service,
    )

    profile = style_service.create_profile(
        "Kể chuyện",
        description="Đọc tự nhiên.",
        parameters={
            "pace": "medium",
        },
        prompt_instructions={
            "positive_prompt": "Đọc tự nhiên",
            "negative_prompt": "",
            "system_prompt": "",
        },
    )

    linked = style_service.bind_variant_style(
        voice,
        "default",
        profile.style_profile_id,
    )

    variant = linked.config.variants[0]

    assert profile.intended_use == "generate_style_profile"
    assert profile.style_classification == "style_only"
    assert not profile.compatibility["separate_checkpoint_required"]
    assert variant["style_profile_id"] == profile.style_profile_id
    assert variant["separate_model_required"] is False
    assert "model_path" in variant
    assert variant["model_path"] == ""


def test_local_api_voice_detail_rename_and_publish_validation(tmp_path):

    service, voice = build_voice_service(
        tmp_path
    )

    catalog = VoiceCatalogService(
        voice_service=service
    )

    api = LocalApiService(
        config=LocalApiConfig(
            local_api_enabled=True,
            local_api_token="secret-token",
        ),
        voice_catalog=catalog,
        voice_publish_service=VoicePublishService(
            service
        ),
    )

    detail = api.route(
        "GET",
        f"/api/v1/voices/{voice.id}",
        {},
    )

    assert detail["body"]["display_name"] == "Thu Minh"

    renamed = api.route(
        "PATCH",
        f"/api/v1/voices/{voice.id}/display-name",
        {
            "display_name": "Thu Minh API",
        },
    )

    assert renamed["status_code"] == 200
    assert renamed["body"]["voice_id"] == voice.id
    assert renamed["body"]["display_name"] == "Thu Minh API"

    validation = api.route(
        "POST",
        "/api/v1/voice-publish/validate",
        {
            "voice_id": voice.id,
        },
    )

    assert validation["body"]["status"] == "blocked"
    assert "gpt_model" in validation["body"]["blockers"]
    assert service.find_by_id(
        voice.id
    ).name == "Thu Minh"
