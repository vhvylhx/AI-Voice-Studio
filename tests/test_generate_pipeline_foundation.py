import json
import shutil
import sys
import wave
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

from models.generate_pipeline_foundation import (  # noqa: E402
    GENERATE_STATE_READY,
    GenerateArtifactRecord,
    GenerateRequestRecord,
    GenerateStateMachine,
    GenerateUnitRecord,
)
from services.generate_repository import GenerateRepository  # noqa: E402
from services.generate_session_service import (  # noqa: E402
    GenerateSessionService,
)
from services.generate_text_structure_service import (  # noqa: E402
    GenerateTextStructureService,
)
from services.job_handler_registry import JobHandlerRegistry  # noqa: E402
from services.job_log_service import JobLogService  # noqa: E402
from services.job_queue_service import JobQueueService  # noqa: E402
from services.job_repository import JobRepository  # noqa: E402
from services.job_runner import JobRunner  # noqa: E402
from services.local_api_service import LocalApiService  # noqa: E402
from models.local_api_config import LocalApiConfig  # noqa: E402


def clean_cache(
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


def build_service(
    name="test_generate_foundation",
):

    root = clean_cache(
        name
    )

    repository = GenerateRepository(
        root / "generate"
    )

    service = GenerateSessionService(
        repository=repository
    )

    return root, service


def sample_request(
    root,
):

    return {
        "project_id": "project_000001",
        "voice_id": "0001",
        "variant_id": "default",
        "style_id": "natural",
        "text": "Chương 1\n\nXin chào. Đây là câu thứ hai. Đây là một câu đủ dài để tạo plan.",
        "output_folder": str(
            root / "out"
        ),
        "output_name": "demo",
        "output_format": "wav",
        "language": "vi",
    }


def write_valid_wav(
    path,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(
            path
        ),
        "wb",
    ) as wav:

        wav.setnchannels(
            1
        )

        wav.setsampwidth(
            2
        )

        wav.setframerate(
            32000
        )

        wav.writeframes(
            b"\x00\x00" * 320
        )


def test_no_loss_reconstruction_vietnamese_titles_intro_outro():

    service = GenerateTextStructureService()

    text = (
        "Intro mở đầu...\n\n"
        "Chương 1\n\n"
        "“Xin chào...” Đây là câu thứ hai.\n\n\n"
        "Chương 2\n\n"
        "Một câu rất dài cần hard split nhưng không được mất chữ "
        "và không được cắt giữa từ trong quá trình tạo unit.\n\n"
        "Outro kết thúc."
    )

    document, chapters, units, normalized = service.build_structure(
        text,
        "session_test",
        max_unit_characters=28,
    )

    report = service.verify_reconstruction(
        text,
        normalized,
        units,
    )

    assert report.ok
    assert service.reconstruct_units(
        units
    ) == normalized
    assert all(
        unit.text.strip()
        for unit in units
    )
    assert any(
        unit.boundary == "chapter_title"
        for unit in units
    )
    assert "Intro mở đầu" in units[0].text
    assert "Outro kết thúc." in service.reconstruct_units(
        units
    )

    broken = [
        GenerateUnitRecord.from_dict(
            unit.to_dict()
        )
        for unit in units
    ]

    broken[
        0
    ].text = broken[
        0
    ].text.replace(
        "I",
        "X",
        1,
    )

    broken_report = service.verify_reconstruction(
        text,
        normalized,
        broken,
    )

    assert not broken_report.ok
    assert broken_report.mismatch_index >= 0


def test_model_roundtrip_and_state_machine():

    record = GenerateRequestRecord(
        project_id="project_1",
        voice_id="0001",
    )

    data = record.to_dict()

    loaded = GenerateRequestRecord.from_dict(
        data
    )

    assert loaded.request_id == record.request_id
    assert loaded.voice_id == "0001"

    machine = GenerateStateMachine()

    assert machine.can_transition(
        "created",
        "validated",
    )
    assert not machine.can_transition(
        "completed",
        "running",
    )


def test_text_snapshot_structure_and_plan_manifest():

    root, service = build_service()

    result = service.create_session(
        sample_request(
            root
        )
    )

    assert result["validation"]["ok"]
    assert result["session"]["status"] == GENERATE_STATE_READY
    assert result["manifest"]["units_total"] >= 2

    snapshot = Path(
        result["request"]["source"]["snapshot_path"]
    )

    assert snapshot.exists()
    assert "Xin chào" in snapshot.read_text(
        encoding="utf-8"
    )

    plan = service.get_plan(
        result["session"]["session_id"]
    )

    assert plan["units"]
    assert all(
        item["text"].strip()
        for item in plan["units"]
    )
    assert plan["frozen"]
    assert plan["plan_checksum_sha256"]
    assert plan["settings_snapshot"]["default_language"] == "vi"
    assert plan["selection_snapshot"]["voice_id"] == "0001"
    assert plan["output_snapshot"]["output_format"] == "wav"
    assert result["request"]["revision"] == 1
    assert result["request"]["materialized_at"]
    assert result["request"]["request_checksum_sha256"]


def test_external_source_deletion_keeps_session_usable():

    root, service = build_service(
        "test_generate_foundation_source_delete"
    )

    source = root / "source.txt"

    source.write_text(
        "Xin chào. Đây là nguồn ngoài.",
        encoding="utf-8",
    )

    request = sample_request(
        root
    )

    request.pop(
        "text",
    )

    request[
        "text_file"
    ] = str(
        source
    )

    result = service.create_session(
        request
    )

    source.unlink()

    session_id = result["session"]["session_id"]

    detail = service.get_session(
        session_id
    )

    plan = service.get_plan(
        session_id
    )

    snapshot = Path(
        detail["request"]["source"]["snapshot_path"]
    )

    assert detail["session"]["session_id"] == session_id
    assert plan["units"]
    assert snapshot.exists()


def test_txt_source_is_not_modified():

    root, service = build_service(
        "test_generate_foundation_txt"
    )

    source = root / "source.txt"

    original = "Xin chào.\n\nĐây là file gốc."

    source.write_text(
        original,
        encoding="utf-8",
    )

    request = sample_request(
        root
    )

    request.pop(
        "text",
    )

    request[
        "text_file"
    ] = str(
        source
    )

    result = service.create_session(
        request
    )

    assert result["validation"]["ok"]
    assert source.read_text(
        encoding="utf-8"
    ) == original


def test_validation_blocks_missing_text_and_bad_format():

    _, service = build_service(
        "test_generate_foundation_validation"
    )

    report = service.validate_request(
        {
            "voice_id": "0001",
            "output_format": "flac",
        }
    )

    codes = [
        issue.code
        for issue in report.issues
    ]

    assert not report.ok
    assert "generate_text_missing" in codes
    assert "generate_output_format_unsupported" in codes


def test_output_collision_and_path_escape_block_materialize():

    root, service = build_service(
        "test_generate_foundation_output_safety"
    )

    request = sample_request(
        root
    )

    output = root / "out" / "demo.wav"

    output.parent.mkdir(
        parents=True,
    )

    output.write_bytes(
        b"exists"
    )

    result = service.create_session(
        request
    )

    codes = [
        issue["code"]
        for issue in result["validation"]["issues"]
    ]

    assert result["session"]["status"] == "blocked"
    assert "generate_output_collision" in codes

    request = sample_request(
        root
    )

    request["output_name"] = "..\\escape"

    result = service.create_session(
        request
    )

    codes = [
        issue["code"]
        for issue in result["validation"]["issues"]
    ]

    assert "generate_output_path_escape" in codes

    request = sample_request(
        root
    )

    request["output_name"] = "CON"

    result = service.create_session(
        request
    )

    codes = [
        issue["code"]
        for issue in result["validation"]["issues"]
    ]

    assert "generate_output_windows_reserved_name" in codes


def test_frozen_plan_rejects_semantic_mutation_and_detects_corruption():

    root, service = build_service(
        "test_generate_foundation_frozen_plan"
    )

    result = service.create_session(
        sample_request(
            root
        )
    )

    session_id = result["session"]["session_id"]

    plan = service.repository.load_plan(
        session_id
    )

    checksum = plan.immutable_checksum_sha256

    plan.units[
        0
    ].status = "failed"

    service.repository.save_plan(
        plan
    )

    reopened = service.repository.load_plan(
        session_id
    )

    assert reopened.immutable_checksum_sha256 == checksum

    reopened.units[
        0
    ].text = reopened.units[
        0
    ].text + "x"

    try:

        service.repository.save_plan(
            reopened
        )

        assert False

    except ValueError as exc:

        assert str(
            exc
        ) == "generate_plan_frozen_mutation"

    raw = service.repository.read_json(
        service.repository.session_dir(
            session_id
        )
        / "plan.json"
    )

    raw[
        "units"
    ][
        0
    ][
        "text"
    ] += "!"

    service.repository.atomic_write_json(
        service.repository.session_dir(
            session_id
        )
        / "plan.json",
        raw,
    )

    integrity = service.plan_integrity(
        session_id
    )

    assert not integrity["ok"]
    assert integrity["code"] == "generate_plan_corrupted"


def test_resume_and_retry_inspection():

    root, service = build_service(
        "test_generate_foundation_resume"
    )

    result = service.create_session(
        sample_request(
            root
        )
    )

    session_id = result["session"]["session_id"]

    resume = service.inspect_resume(
        session_id
    )

    assert resume["can_resume"]
    assert resume["pending_units"]

    plan = service.repository.load_plan(
        session_id
    )

    unit_id = plan.units[0].unit_id

    retry = service.inspect_retry(
        session_id,
        unit_id,
    )

    assert not retry["can_retry"]

    plan.units[0].status = "failed"

    service.repository.save_plan(
        plan
    )

    retry = service.inspect_retry(
        session_id,
        unit_id,
    )

    assert retry["can_retry"]


def test_manifest_has_planned_artifacts_and_wav_validation():

    root, service = build_service(
        "test_generate_foundation_artifacts"
    )

    result = service.create_session(
        sample_request(
            root
        )
    )

    manifest = service.get_manifest(
        result["session"]["session_id"]
    )

    assert manifest["artifact_records"]
    assert all(
        item["status"] == "planned"
        for item in manifest["artifact_records"]
    )

    artifact = manifest["artifact_records"][0]

    missing = service.validate_wav_artifact(
        artifact
    )

    assert missing.validation_status == "missing"

    wav_path = Path(
        artifact["final_path"]
    )

    write_valid_wav(
        wav_path
    )

    valid = service.validate_wav_artifact(
        artifact
    )

    assert valid.validation_status == "valid"
    assert valid.channels == 1
    assert valid.sample_rate == 32000


def test_artifact_reservation_promote_and_test_provider_execution():

    root, service = build_service(
        "test_generate_foundation_artifact_lifecycle"
    )

    result = service.create_session(
        sample_request(
            root
        )
    )

    session_id = result["session"]["session_id"]

    artifacts = service.repository.load_artifacts(
        session_id
    )

    artifact = artifacts[
        0
    ]

    reserve = service.reserve_artifact(
        artifact
    )

    assert reserve["ok"]

    other_writer = GenerateArtifactRecord.from_dict(
        reserve[
            "artifact"
        ]
    )

    other_writer.reservation_id = ""

    reserved_again = service.reserve_artifact(
        other_writer
    )

    assert not reserved_again["ok"]

    artifact = GenerateArtifactRecord.from_dict(
        reserve["artifact"]
    )

    promoted_missing = service.promote_artifact(
        artifact,
        artifact.reservation_id,
    )

    assert not promoted_missing["ok"]
    assert promoted_missing["code"] == "temp_output_missing"

    # Test-only provider: chỉ tồn tại trong test, không đăng ký readiness/production.
    def provider(
        artifact,
        temp_path,
    ):

        write_valid_wav(
            temp_path
        )

    plan = service.repository.load_plan(
        session_id
    )

    unit_id = plan.units[
        0
    ].unit_id

    output = service.execute_unit_with_provider(
        session_id,
        unit_id,
        provider=provider,
    )

    assert output["ok"]
    assert output["artifact"]["status"] == "valid"

    plan = service.repository.load_plan(
        session_id
    )

    assert plan.units[
        0
    ].status == "completed"
    assert plan.attempts[
        0
    ].status == "completed"


def test_resume_retry_execution_unavailable_and_test_provider_path():

    root, service = build_service(
        "test_generate_foundation_resume_execution"
    )

    result = service.create_session(
        sample_request(
            root
        )
    )

    session_id = result["session"]["session_id"]

    resume = service.inspect_resume(
        session_id
    )

    unavailable = service.execute_resume(
        session_id,
        expected_fingerprint=resume["fingerprint"],
    )

    assert unavailable["status"] == "UNAVAILABLE"

    stale = service.execute_resume(
        session_id,
        expected_fingerprint="stale",
        provider=lambda artifact, path: write_valid_wav(
            path
        ),
    )

    assert stale["code"] == "generate_stale_inspection"

    plan = service.repository.load_plan(
        session_id
    )

    plan.units[
        0
    ].status = "failed"

    service.repository.save_plan(
        plan
    )

    retry = service.inspect_retry(
        session_id,
        plan.units[
            0
        ].unit_id,
    )

    assert retry["can_retry"]

    unavailable_retry = service.retry_unit(
        session_id,
        plan.units[
            0
        ].unit_id,
        expected_fingerprint=retry["fingerprint"],
    )

    assert unavailable_retry["status"] == "UNAVAILABLE"


def test_repository_registry_lists_sessions():

    root, service = build_service(
        "test_generate_foundation_registry"
    )

    service.create_session(
        sample_request(
            root
        )
    )

    sessions = service.list_sessions(
        "project_000001"
    )

    assert sessions["items"]
    assert sessions["items"][0]["project_id"] == "project_000001"


def test_job_queue_generate_prepare_worker():

    root, service = build_service(
        "test_generate_foundation_job"
    )

    job_repository = JobRepository(
        root / "jobs"
    )

    queue = JobQueueService(
        job_repository,
        handler_registry=JobHandlerRegistry(),
    )

    logs = JobLogService(
        job_repository
    )

    registry = JobHandlerRegistry()

    runner = JobRunner(
        repository=job_repository,
        queue_service=queue,
        handler_registry=registry,
        log_service=logs,
        app_context=SimpleNamespace(
            generate_session_service=service
        ),
    )

    job = queue.enqueue_new(
        "generate_prepare",
        voice_id="0001",
        project_id="project_000001",
        payload={
            "request": sample_request(
                root
            ),
        },
    )

    result = runner.run_next()

    assert result.job_id == job.job_id
    assert result.state == "completed"
    assert result.result["ok"]
    assert result.resource_requirement == {}

    requirement = registry.resource_requirement(
        "generate_prepare"
    )

    assert not requirement.requires_gpu


def test_local_api_generate_foundation_endpoints():

    root, service = build_service(
        "test_generate_foundation_api"
    )

    api = LocalApiService(
        config=LocalApiConfig(
            local_api_enabled=True,
            local_api_token="secret-token",
        ),
        generate_session_service=service,
    )

    readiness = api.route(
        "GET",
        "/api/v1/generate/readiness",
        {},
    )

    assert readiness["body"]["status"] == "planning_ready_execution_unavailable"
    assert readiness["body"]["capabilities"]["generate_execution"] == "UNAVAILABLE"

    created = api.route(
        "POST",
        "/api/v1/generate/sessions",
        sample_request(
            root
        ),
    )

    assert created["status_code"] == 201

    session_id = created["body"]["session"]["session_id"]

    detail = api.route(
        "GET",
        f"/api/v1/generate/sessions/{session_id}",
        {},
    )

    assert detail["body"]["session"]["session_id"] == session_id
    assert "original_path" not in json.dumps(
        detail,
        ensure_ascii=False,
    )

    manifest = api.route(
        "GET",
        f"/api/v1/generate/sessions/{session_id}/manifest",
        {},
    )

    assert manifest["body"]["units_total"] >= 1

    units = api.route(
        "GET",
        f"/api/v1/generate/sessions/{session_id}/units",
        {
            "limit": 1,
        },
    )

    assert units["body"]["items"]
    assert units["body"]["limit"] == 1

    artifacts = api.route(
        "GET",
        f"/api/v1/generate/sessions/{session_id}/artifacts",
        {},
    )

    assert artifacts["body"]["items"]
    assert isinstance(
        artifacts["body"]["items"][0]["final_path"],
        dict,
    )

    resume = api.route(
        "GET",
        f"/api/v1/generate/sessions/{session_id}/resume",
        {},
    )

    resume_action = api.route(
        "POST",
        f"/api/v1/generate/sessions/{session_id}/resume",
        {
            "expected_fingerprint": resume["body"]["fingerprint"],
        },
    )

    assert resume_action["status_code"] == 503
    assert resume_action["body"]["status"] == "UNAVAILABLE"

    recovery = api.route(
        "GET",
        "/api/v1/generate/recovery",
        {},
    )

    assert recovery["body"]["engine_loaded"] is False

    rebuild = api.route(
        "POST",
        f"/api/v1/generate/sessions/{session_id}/manifest/rebuild",
        {},
    )

    assert rebuild["body"]["ok"]
    assert rebuild["body"]["manifest"]["units_total"] >= 1
    assert "original_path" not in json.dumps(
        rebuild,
        ensure_ascii=False,
    )


def test_text_splitter_does_not_cut_between_words():

    service = GenerateTextStructureService()

    parts = service.split_long_sentence(
        "một hai ba bốn năm sáu bảy tám",
        max_characters=12,
    )

    assert all(
        "  " not in item
        for item in parts
    )
    assert "một hai ba" in parts[0]
