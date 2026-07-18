import json
import shutil
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

from models.local_api_config import LocalApiConfig
from models.voice_config import VoiceConfig
from services.generation_job_service import GenerationJobService
from services.local_api_service import LocalApiService
from services.voice_catalog_service import VoiceCatalogService
from services.voice_service import VoiceService


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


def build_voice_catalog(
    ready=False,
):

    root = reset_root(
        "test_local_api_voices"
    )

    voice_service = VoiceService()

    voice_service._root = root

    voice_folder = root / "Thu Minh"

    voice_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    voice_service.ensure_folders(
        voice_folder
    )

    config = VoiceConfig(
        voice_id="0001",
        language="vi",
        default_variant_id="default",
    )

    if ready:

        gpt = voice_folder / "model" / "gpt.ckpt"
        sovits = voice_folder / "model" / "sovits.pth"
        ref = voice_folder / "dataset" / "ref.wav"

        gpt.write_text(
            "mock",
            encoding="utf-8",
        )

        sovits.write_text(
            "mock",
            encoding="utf-8",
        )

        ref.write_text(
            "mock",
            encoding="utf-8",
        )

        config.gpt_model = str(
            gpt
        )

        config.sovits_model = str(
            sovits
        )

        config.reference_audio = str(
            ref
        )

        config.reference_text = "Xin chào."

    voice_service.save_config(
        voice_folder,
        config,
    )

    return VoiceCatalogService(
        voice_service
    )


def build_api(
    ready=False,
):

    catalog = build_voice_catalog(
        ready=ready
    )

    jobs_root = reset_root(
        "test_local_api_jobs"
    )

    jobs = GenerationJobService(
        root=jobs_root,
        voice_catalog=catalog,
        concurrency=1,
    )

    api = LocalApiService(
        config=LocalApiConfig(
            local_api_enabled=True,
            local_api_token="secret-token",
            local_api_host="127.0.0.1",
            local_api_port=8765,
        ),
        voice_catalog=catalog,
        job_service=jobs,
    )

    return api


def test_voice_catalog_does_not_leak_paths():

    api = build_api(
        ready=True
    )

    response = api.route(
        "GET",
        "/api/v1/voices",
        {},
    )

    text = json.dumps(
        response,
        ensure_ascii=False,
    )

    assert response["status_code"] == 200
    assert "0001" in text
    assert "gpt.ckpt" not in text
    assert "sovits.pth" not in text


def test_variant_catalog_has_no_model_contract():

    api = build_api()

    response = api.route(
        "GET",
        "/api/v1/voices/0001/variants",
        {},
    )

    item = response["body"]["items"][0]

    assert "variant_id" in item
    assert "checkpoint" not in item
    assert "model_path" not in item


def test_create_job_blocks_voice_not_ready():

    api = build_api(
        ready=False
    )

    response = api.route(
        "POST",
        "/api/v1/generation/jobs",
        {
            "voice_id": "0001",
            "variant_id": "default",
            "text": "Xin chào.",
            "output_format": "wav",
            "request_id": "demo",
        },
    )

    assert response["status_code"] == 400
    assert response["body"]["status"] == "failed"
    assert "job_id" in response["body"]


def test_create_job_ready_is_queued_not_generated():

    api = build_api(
        ready=True
    )

    response = api.route(
        "POST",
        "/api/v1/generation/jobs",
        {
            "voice_id": "0001",
            "variant_id": "default",
            "text": "Xin chào.",
            "output_format": "wav",
            "request_id": "demo",
        },
    )

    assert response["status_code"] == 202
    assert response["body"]["status"] == "queued"

    job = api.job_service.get_job(
        response["body"]["job_id"]
    )

    assert job.status == "queued"
    assert "local_api_token" not in json.dumps(
        job.to_dict()
    )


def test_empty_text_and_bad_format_validation():

    api = build_api(
        ready=True
    )

    response = api.route(
        "POST",
        "/api/v1/generation/jobs",
        {
            "voice_id": "0001",
            "text": "",
            "output_format": "flac",
        },
    )

    assert response["status_code"] == 400


def test_cancel_and_result_not_ready():

    api = build_api(
        ready=True
    )

    created = api.route(
        "POST",
        "/api/v1/generation/jobs",
        {
            "voice_id": "0001",
            "text": "Xin chào.",
            "output_format": "wav",
        },
    )

    job_id = created["body"]["job_id"]

    cancelled = api.route(
        "POST",
        f"/api/v1/generation/jobs/{job_id}/cancel",
        {},
    )

    assert cancelled["body"]["status"] == "cancelled"

    result = api.route(
        "GET",
        f"/api/v1/generation/jobs/{job_id}/result",
        {},
    )

    assert result["body"]["error"] == "result_not_ready"


def test_default_host_and_token_config():

    api = build_api()

    assert api.config.local_api_host == "127.0.0.1"
    assert api.authorized(
        type(
            "Req",
            (),
            {
                "headers": {
                    "Authorization": "Bearer secret-token",
                }
            },
        )()
    )

    assert not api.authorized(
        type(
            "Req",
            (),
            {
                "headers": {
                    "Authorization": "Bearer wrong",
                }
            },
        )()
    )


test_voice_catalog_does_not_leak_paths()
test_variant_catalog_has_no_model_contract()
test_create_job_blocks_voice_not_ready()
test_create_job_ready_is_queued_not_generated()
test_empty_text_and_bad_format_validation()
test_cancel_and_result_not_ready()
test_default_host_and_token_config()

print("LOCAL_API_TEST_OK")
