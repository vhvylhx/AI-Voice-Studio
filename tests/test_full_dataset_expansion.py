import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.alignment_quality_config import AlignmentQualityConfig
from models.voice_architecture import GenerateRequestContract
from models.voice_architecture import VoiceIdentityContract
from services.dataset_service import DatasetService
from services.dataset_review_service import DatasetReviewService
from services.full_dataset_preparation_service import FullDatasetPreparationService
from services.project_service import ProjectService
from services.workflow_service import WorkflowService


def reset_root(name):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(
            root
        )

    root.mkdir(
        parents=True,
    )

    return root


def write_text(file, content="Chuong 171\nNoi dung dung."):

    file.write_text(
        content,
        encoding="utf-8",
    )


def write_audio(file):

    file.write_bytes(
        b"audio"
    )


def test_dataset_scan_supports_separate_audio_and_text_folders():

    root = reset_root(
        "test_full_dataset_separate_folders"
    )

    audio = root / "mp3"

    text = root / "text"

    audio.mkdir()

    text.mkdir()

    write_audio(
        audio / "171.mp3"
    )

    write_text(
        text / "Chuong 171.txt"
    )

    result = DatasetService().scan_folders(
        audio,
        text,
        root / "dataset",
    )

    assert result["health"]["total_mp3"] == 1
    assert result["health"]["total_text"] == 1
    assert result["health"]["matched"] == 1
    assert result["items"][0]["match_key"] == 171
    assert result["manifest"]["source_roots"]["audio_folder"].endswith(
        "mp3"
    )


def test_dataset_scan_supports_same_folder_mode():

    root = reset_root(
        "test_full_dataset_same_folder"
    )

    write_audio(
        root / "171.mp3"
    )

    write_text(
        root / "Chuong 171.txt"
    )

    workflow = WorkflowService().create_same_folder_config(
        root
    )

    result = DatasetService().scan_folders(
        workflow.audio_folder,
        workflow.text_folder,
        root / "dataset",
    )

    assert workflow.source_mode == "same_folder"
    assert workflow.audio_folder == workflow.text_folder
    assert result["health"]["matched"] == 1


def test_legacy_workspace_is_detected_as_same_folder():

    root = reset_root(
        "test_full_dataset_legacy_workspace"
    )

    workspace = root / "workspace"

    voice = workspace / "Thu Minh"

    voice.mkdir(
        parents=True,
    )

    workflow = WorkflowService().detect_legacy_workspace(
        "Thu Minh",
        workspace_root=workspace,
    )

    assert workflow is not None
    assert workflow.source_mode == "same_folder"
    assert Path(
        workflow.audio_folder
    ) == voice
    assert workflow.audio_folder == workflow.text_folder


def test_workflow_remembers_voice_runtime_and_project_selection():

    root = reset_root(
        "test_full_dataset_project_memory"
    )

    service = ProjectService()

    service.root = root / "projects"

    service.root.mkdir(
        parents=True,
    )

    project = service.create(
        "Alpha"
    )

    workflow = WorkflowService().create_config(
        input_folder="",
        source_mode="separate_folders",
        audio_folder="audio",
        text_folder="text",
        output_folder="out",
        use_input_folder_as_output=False,
        selected_voice_id="0001",
        runtime_profile_id="runtime-low",
    )

    service.save_dataset_workflow(
        project,
        workflow,
    )

    loaded = service.load(
        "Alpha"
    )

    assert loaded.config.last_audio_folder == "audio"
    assert loaded.config.last_text_folder == "text"
    assert loaded.config.last_source_mode == "separate_folders"
    assert loaded.config.last_output_folder == "out"
    assert loaded.config.last_use_input_as_output is False
    assert loaded.config.last_voice_id == "0001"
    assert loaded.config.last_runtime_profile_id == "runtime-low"


def test_full_dataset_service_runs_scan_repair_review_without_alignment():

    root = reset_root(
        "test_full_dataset_service"
    )

    audio = root / "mp3"

    text = root / "text"

    output = root / "output"

    audio.mkdir()

    text.mkdir()

    write_audio(
        audio / "171.mp3"
    )

    write_text(
        text / "171.txt"
    )

    workflow = WorkflowService().create_config(
        audio_folder=audio,
        text_folder=text,
        output_folder=output,
        use_input_folder_as_output=False,
    )

    result = FullDatasetPreparationService().run(
        workflow,
        quality_config=AlignmentQualityConfig(),
        run_alignment=False,
    )

    assert result["report"]["summary"]["total_mp3"] == 1
    assert result["report"]["summary"]["matched"] == 1
    assert result["review"]["summary"]["train_allowed"] is True
    assert (
        output / "full_dataset_report.json"
    ).exists()


def test_auto_review_maps_safe_statuses_and_clears_pending():

    report = {
        "items": [
            {
                "code": "test_version",
                "status": "pending",
            },
            {
                "code": "broken_file",
                "status": "pending",
            },
            {
                "code": "empty_file",
                "status": "pending",
            },
            {
                "code": "missing_audio",
                "status": "pending",
            },
            {
                "code": "missing_text",
                "status": "pending",
            },
            {
                "code": "invalid_filename",
                "status": "pending",
            },
            {
                "code": "filename_content_mismatch",
                "status": "pending",
            },
        ]
    }

    reviewed = DatasetReviewService().auto_review(
        report
    )

    statuses = {
        item["code"]: item["status"]
        for item in reviewed["items"]
    }

    assert statuses["test_version"] == "ignored"
    assert statuses["broken_file"] == "rejected"
    assert statuses["empty_file"] == "rejected"
    assert statuses["missing_audio"] == "ignored"
    assert statuses["missing_text"] == "ignored"
    assert statuses["invalid_filename"] == "ignored"
    assert statuses["filename_content_mismatch"] == "rejected"
    assert reviewed["summary"]["pending"] == 0
    assert reviewed["summary"]["train_allowed"] is True


def test_ignored_and_rejected_files_do_not_enter_dataset_items():

    root = reset_root(
        "test_full_dataset_error_files_not_matched"
    )

    write_audio(
        root / "171.mp3"
    )

    write_text(
        root / "171.txt"
    )

    write_audio(
        root / "172.mp3"
    )

    write_text(
        root / "173 test.txt"
    )

    (root / "174.docx").write_bytes(
        b"broken"
    )

    result = DatasetService().scan_folders(
        root,
        root,
        root / "dataset",
    )

    item_files = {
        Path(
            item["audio"]
        ).name
        for item in result["items"]
    } | {
        Path(
            item["text"]
        ).name
        for item in result["items"]
    }

    assert item_files == {
        "171.mp3",
        "171.txt",
    }


def test_voice_architecture_contract_separates_identity_from_generate_request():

    voice = VoiceIdentityContract(
        voice_id="0001",
        name="Thu Minh",
        dataset_path="dataset",
        model_path="model/main",
        preview_path="preview.wav",
        metadata_path="metadata.json",
    )

    request = GenerateRequestContract(
        voice_id=voice.voice_id,
        variant_id="story",
        preset_id="quality",
        reference_style_id="default",
        text_profile_id="audiobook",
        engine="gpt_sovits",
        text="Xin chao.",
    )

    assert voice.voice_id == request.voice_id
    assert "speed" not in voice.__dict__
    assert request.to_dict()["variant_id"] == "story"
