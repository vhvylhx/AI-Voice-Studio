import json
import shutil
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "src"
    ),
)

from models.style_profile import STYLE_STATUS_EXTRACTION_PENDING
from models.style_profile import StyleProfile
from models.voice_config import VoiceConfig
from repositories.style_profile_repository import StyleProfileRepository
from services.feature_readiness_service import FeatureReadinessService
from services.generation_job_service import GenerationJobService
from services.local_api_service import LocalApiService
from services.style_profile_export_service import StyleProfileExportService
from services.style_profile_service import StyleProfileService
from services.voice_catalog_service import VoiceCatalogService


ROOT = Path(
    "cache/test_style_profile_foundation"
)


def reset():

    if ROOT.exists():

        shutil.rmtree(
            ROOT
        )

    ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )


class DummyEnvironment:

    def full_status(
        self,
    ):

        return {
            "app": {
                "ready_for_ui": True,
                "ready_for_tests": True,
                "packages": {
                    "docx": True,
                },
            },
            "alignment": {
                "faster_whisper": False,
            },
            "ffmpeg": {
                "available": True,
            },
            "voice_runtime": {
                "ready": False,
            },
        }


class DummyVoiceService:

    def list(
        self,
    ):

        return []


class DummyReadyCatalog:

    def __init__(
        self,
        style_profile_service,
    ):

        self.style_profile_service = style_profile_service

    def get_voice(
        self,
        voice_id,
    ):

        return {
            "voice_id": voice_id,
            "generation_ready": True,
        }


def test_model_and_variant_migration():

    config = VoiceConfig.from_dict(
        {
            "voice_id": "0001",
            "variants": [
                {
                    "id": "story",
                    "name": "Kể chuyện",
                }
            ],
        }
    )

    assert config.voice_id == "0001"

    assert config.reading_style[
        "default_style_profile_id"
    ] == ""

    assert config.variants[0][
        "style_mode"
    ] == "inherit_voice_default"

    assert config.variants[0][
        "style_strength"
    ] == 1.0


def test_repository_service_export_import():

    reset()

    repository = StyleProfileRepository(
        ROOT / "profiles"
    )

    service = StyleProfileService(
        repository=repository,
        voice_service=DummyVoiceService(),
    )

    profile = service.create_profile(
        "Kể chuyện tự nhiên"
    )

    assert profile.style_profile_id == "style_000001"

    assert profile.status == STYLE_STATUS_EXTRACTION_PENDING

    folder = repository.profile_dir(
        profile.style_profile_id
    )

    assert (
        folder / "prosody/pause_profile.json"
    ).exists()

    readiness = service.readiness(
        profile.style_profile_id
    )

    assert readiness[
        "generation_usage"
    ] == "degraded"

    export = StyleProfileExportService(
        repository
    )

    package = ROOT / "backup.avstyle"

    result = export.export_package(
        profile.style_profile_id,
        package,
    )

    assert result[
        "ok"
    ]

    assert package.exists()

    validation = export.validate_package(
        package
    )

    assert validation[
        "ok"
    ]

    imported_root = ROOT / "imported"

    imported = StyleProfileExportService(
        StyleProfileRepository(
            imported_root
        )
    ).import_package(
        package
    )

    assert imported[
        "ok"
    ]


def test_feature_readiness_and_generation_validation():

    readiness = FeatureReadinessService(
        DummyEnvironment()
    ).summary()

    ids = {
        item[
            "feature_id"
        ]
        for item in readiness[
            "items"
        ]
    }

    assert "style_profile_management" in ids

    assert "style_profile_extraction" in ids

    assert "style_profile_generation_usage" in ids

    reset()

    repository = StyleProfileRepository(
        ROOT / "profiles"
    )

    style_service = StyleProfileService(
        repository=repository,
        voice_service=DummyVoiceService(),
    )

    profile = style_service.create_profile(
        "Style API"
    )

    catalog = VoiceCatalogService(
        voice_service=DummyVoiceService(),
        style_profile_service=style_service,
    )

    job_service = GenerationJobService(
        root=ROOT / "jobs",
        voice_catalog=catalog,
    )

    errors = job_service.validate_request(
        {
            "voice_id": "0001",
            "text": "Xin chào",
            "style_profile_id": profile.style_profile_id,
        }
    )

    codes = {
        item[
            "code"
        ]
        for item in errors
    }

    assert "voice_not_found" in codes

    ready_job_service = GenerationJobService(
        root=ROOT / "jobs_ready",
        voice_catalog=DummyReadyCatalog(
            style_service
        ),
    )

    style_errors = ready_job_service.validate_request(
        {
            "voice_id": "0001",
            "text": "Xin chào",
            "style_profile_id": profile.style_profile_id,
            "style_mode": "explicit",
            "style_strength": 1.0,
        }
    )

    style_codes = {
        item[
            "code"
        ]
        for item in style_errors
    }

    assert "style_profile_generation_not_supported" in style_codes


def test_local_api_style_profile_methods():

    reset()

    repository = StyleProfileRepository(
        ROOT / "profiles"
    )

    style_service = StyleProfileService(
        repository=repository,
        voice_service=DummyVoiceService(),
    )

    profile = style_service.create_profile(
        "API Style"
    )

    api = LocalApiService(
        config={
            "local_api_enabled": False,
            "local_api_host": "127.0.0.1",
            "local_api_port": 8765,
            "local_api_token": "token",
            "local_api_auto_start": False,
            "allowed_origins": [],
            "output_access_policy": "managed_output_only",
            "concurrency": 1,
        },
        voice_catalog=VoiceCatalogService(
            voice_service=DummyVoiceService(),
            style_profile_service=style_service,
        ),
        job_service=GenerationJobService(
            root=ROOT / "jobs",
            voice_catalog=VoiceCatalogService(
                voice_service=DummyVoiceService(),
                style_profile_service=style_service,
            ),
        ),
        readiness=FeatureReadinessService(
            DummyEnvironment()
        ),
        style_profiles=style_service,
    )

    listed = api.style_profile_list()

    assert listed[
        "items"
    ][0][
        "style_profile_id"
    ] == profile.style_profile_id

    detail = api.style_profile_detail(
        profile.style_profile_id
    )

    assert "dataset_reference" not in detail

    assert api.capabilities()[
        "style_profile_support"
    ]


def test_ui_source_contains_required_sections():

    page = Path(
        "src/pages/style_profile_page.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "Phong cách đọc" in page

    assert "Tạo từ Dataset" in page

    assert "Nhập .avstyle" in page

    assert "Xuất .avstyle" in page


if __name__ == "__main__":

    test_model_and_variant_migration()
    test_repository_service_export_import()
    test_feature_readiness_and_generation_validation()
    test_local_api_style_profile_methods()
    test_ui_source_contains_required_sections()
    print(
        "test_style_profile_foundation OK"
    )
