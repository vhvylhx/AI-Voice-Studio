import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.dataset_service import DatasetService
from services.dataset_repair_service import DatasetRepairService
from services.dataset_review_service import DatasetReviewService
from services.train_audio_prep_service import TrainAudioPrepService
from services.workflow_service import WorkflowService


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


def write_text(
    file,
    content="Noi dung chuong.",
):

    file.write_text(
        content,
        encoding="utf-8",
    )


def write_audio(
    file,
):

    file.write_bytes(
        b"audio"
    )


def test_match_text_with_multiple_mp3_by_chapter_number():

    root = reset_root(
        "test_dataset_matching_chapter"
    )

    write_text(
        root / "109.txt"
    )

    write_audio(
        root / "109 2.mp3"
    )

    write_audio(
        root / "109 1.mp3"
    )

    write_audio(
        root / "110 1.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 2
    assert [
        Path(item["audio"]).name
        for item in result["items"]
    ] == [
        "109 1.mp3",
        "109 2.mp3",
    ]
    assert all(
        item["match_rule"] == "chapter_number"
        for item in result["items"]
    )
    assert result["health"]["missing_text"] == 1


def test_match_chapter_text_name_with_numbered_audio():

    root = reset_root(
        "test_dataset_matching_chapter_name"
    )

    write_text(
        root / "Chương 109.txt"
    )

    write_audio(
        root / "109 1.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 1
    assert result["items"][0]["match_key"] == 109
    assert result["items"][0]["audio_part"] == 1


def test_do_not_cross_match_different_chapter_numbers():

    root = reset_root(
        "test_dataset_matching_no_cross"
    )

    write_text(
        root / "109.txt"
    )

    write_audio(
        root / "110 1.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 0
    assert {
        error["code"]
        for error in result["errors"]
    } == {
        "missing_audio",
        "missing_text",
    }


def test_test_files_are_not_auto_matched_with_typo():

    root = reset_root(
        "test_dataset_matching_test_file"
    )

    write_text(
        root / "109 tset.txt"
    )

    write_audio(
        root / "109 tset.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 0
    assert all(
        error["code"] == "test_version"
        for error in result["errors"]
    )
    assert result["health"]["test_version"] == 2


def test_invalid_filename_is_reported():

    root = reset_root(
        "test_dataset_matching_invalid_filename"
    )

    write_text(
        root / "chuong-cuoi.txt"
    )

    write_audio(
        root / "audio-cuoi.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 0
    assert result["health"]["invalid_filename"] == 2
    assert all(
        error["code"] == "invalid_filename"
        for error in result["errors"]
    )


def test_chinese_is_not_classified_anymore_when_filename_has_chapter():

    root = reset_root(
        "test_dataset_matching_chinese_allowed"
    )

    write_text(
        root / "109 中文.txt",
        "中文 noi dung.",
    )

    write_audio(
        root / "109 中文.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["summary"]["valid_pairs"] == 1
    assert "ignored_chinese" not in result["health"]
    assert all(
        error["code"] != "ignored_chinese"
        for error in result["errors"]
    )


def test_filename_content_mismatch_is_reported_and_not_rematched():

    root = reset_root(
        "test_dataset_matching_content_mismatch"
    )

    write_text(
        root / "100.txt",
        "Chương 101\nNoi dung chuong 101.",
    )

    write_audio(
        root / "100.mp3"
    )

    write_text(
        root / "101.txt",
        "Chương 101\nNoi dung chuong 101.",
    )

    result = DatasetService().scan(
        root
    )

    assert result["health"]["filename_content_mismatch"] == 1
    assert any(
        error["code"] == "filename_content_mismatch"
        and error["file"].endswith(
            "100.txt"
        )
        for error in result["errors"]
    )
    assert all(
        not (
            Path(item["audio"]).name == "100.mp3"
            and Path(item["text"]).name == "101.txt"
        )
        for item in result["items"]
    )


def test_duplicate_is_reported():

    root = reset_root(
        "test_dataset_matching_duplicate"
    )

    write_text(
        root / "109.txt"
    )

    write_text(
        root / "Chương 109.txt"
    )

    write_audio(
        root / "109.mp3"
    )

    result = DatasetService().scan(
        root
    )

    assert result["health"]["duplicate"] == 1
    assert any(
        error["code"] == "duplicate"
        for error in result["errors"]
    )


def test_dataset_repair_keeps_best_duplicate_and_copies_rest_to_ignored():

    root = reset_root(
        "test_dataset_repair_duplicate"
    )

    write_text(
        root / "109.txt"
    )

    duplicate = root / "ChÆ°Æ¡ng 109.txt"

    write_text(
        duplicate
    )

    write_audio(
        root / "109.mp3"
    )

    dataset = DatasetService().scan(
        root
    )

    report = DatasetRepairService().repair(
        dataset,
        root / "repair",
    )

    assert report["before"]["duplicate"] == 1
    assert len(
        report["repaired"]
    ) == 1
    assert report["repaired"][0]["code"] == "duplicate"
    assert report["after"]["duplicate"] == 0
    assert report["after"]["blocking_errors"] == (
        report["before"]["blocking_errors"] - 1
    )
    assert Path(
        report["repaired"][0]["repaired_file"]
    ).exists()
    assert (
        root
        / "repair"
        / "dataset_repair_report.json"
    ).exists()
    assert duplicate.exists()


def test_dataset_repair_skips_unsafe_errors_and_keeps_running():

    root = reset_root(
        "test_dataset_repair_skip"
    )

    write_text(
        root / "100.txt",
        "Chuong 101\nNoi dung.",
    )

    write_audio(
        root / "100.mp3"
    )

    write_text(
        root / "bad-name.txt"
    )

    write_audio(
        root / "171 test.mp3"
    )

    write_text(
        root / "172.txt"
    )

    write_audio(
        root / "173.mp3"
    )

    (root / "174.txt").write_text(
        "",
        encoding="utf-8",
    )

    (root / "175.docx").write_bytes(
        b"not a docx"
    )

    dataset = DatasetService().scan(
        root
    )

    report = DatasetRepairService().repair(
        dataset,
        root / "repair",
    )

    skipped_codes = {
        item["code"]
        for item in report["skipped"]
    }

    assert {
        "filename_content_mismatch",
        "invalid_filename",
        "test_version",
        "missing_audio",
        "missing_text",
        "empty_file",
        "broken_file",
    }.issubset(
        skipped_codes
    )
    assert len(
        report["repaired"]
    ) == 0
    assert report["final_usable_percent"] == report["after"]["usable_percent"]


def create_review_fixture():

    root = reset_root(
        "test_dataset_review"
    )

    write_text(
        root / "100.txt",
        "Chuong 101\nNoi dung.",
    )

    write_audio(
        root / "100.mp3"
    )

    (root / "101.txt").write_text(
        "",
        encoding="utf-8",
    )

    write_audio(
        root / "102 test.mp3"
    )

    dataset = DatasetService().scan(
        root
    )

    repair = DatasetRepairService().repair(
        dataset,
        root / "repair",
    )

    return root, dataset, repair


def test_dataset_review_creates_pending_items_from_repair_report():

    root, dataset, repair = create_review_fixture()

    report = DatasetReviewService().create_review(
        dataset_result=dataset,
        repair_report=repair,
        output_dir=root / "review",
    )

    assert report["summary"]["pending"] == len(
        report["items"]
    )
    assert report["summary"]["train_allowed"] is False
    assert {
        item["status"]
        for item in report["items"]
    } == {
        "pending",
    }
    assert (
        root
        / "review"
        / "review_report.json"
    ).exists()


def test_dataset_review_approve_all_allows_train_after_review():

    root, dataset, repair = create_review_fixture()

    service = DatasetReviewService()

    report = service.create_review(
        dataset_result=dataset,
        repair_report=repair,
        output_dir=root / "review",
    )

    approved = service.approve_all(
        report
    )

    assert approved["summary"]["approved"] == len(
        approved["items"]
    )
    assert approved["summary"]["all_reviewed"] is True
    assert service.can_train(
        dataset_result=dataset,
        repair_report=repair,
        review_report=approved,
    ) is True


def test_dataset_review_filter_by_reason_or_code():

    root, dataset, repair = create_review_fixture()

    service = DatasetReviewService()

    report = service.create_review(
        dataset_result=dataset,
        repair_report=repair,
        output_dir=root / "review",
    )

    filtered = service.set_status(
        report,
        "ignored",
        code="test_version",
    )

    assert any(
        item["code"] == "test_version"
        and item["status"] == "ignored"
        for item in filtered["items"]
    )
    assert any(
        item["code"] != "test_version"
        and item["status"] == "pending"
        for item in filtered["items"]
    )
    assert "test_version" in filtered["filters"]["codes"]


def test_health_report_summary():

    root = reset_root(
        "test_dataset_matching_health"
    )

    write_text(
        root / "171.txt"
    )

    write_audio(
        root / "171.mp3"
    )

    write_audio(
        root / "172.mp3"
    )

    result = DatasetService().scan(
        root
    )

    health = result["health"]

    assert health["total_mp3"] == 2
    assert health["total_text"] == 1
    assert health["matched"] == 1
    assert health["missing_text"] == 1
    assert health["missing_audio"] == 0
    assert health["usable_percent"] == 50.0
    assert "ignored_chinese" not in health
    assert "ignored_test" not in health


def test_train_audio_prep_stops_before_alignment_when_dataset_health_has_errors():

    root = reset_root(
        "test_dataset_matching_alignment_block"
    )

    source = root / "source"

    source.mkdir(
        parents=True,
    )

    write_audio(
        source / "171.mp3"
    )

    service = TrainAudioPrepService()

    called = {
        "alignment": False,
    }

    def align_mock(*args, **kwargs):

        called["alignment"] = True

        return []

    service.alignment.align = align_mock

    result = service.prepare(
        source,
        root / "dataset",
        root / "segmentation",
        root / "alignment",
    )

    assert called["alignment"] is False
    assert result["report"]["summary"]["blocked"] is True
    assert result["report"]["summary"]["block_reason"] == "dataset_health_failed"


def test_workflow_uses_input_folder_as_output_by_default():

    service = WorkflowService()

    config = service.create_config(
        input_folder="input",
        output_folder="output",
        use_input_folder_as_output=True,
    )

    assert config.resolved_output_folder() == "input"

    result = service.validate(
        config
    )

    assert result["ready"] is True
    assert result["output_folder"] == "input"
    assert result["auto_repair"] is True
    assert result["review_mode"] == "auto"


def test_workflow_requires_output_folder_when_not_using_input():

    service = WorkflowService()

    config = service.create_config(
        input_folder="input",
        output_folder="",
        use_input_folder_as_output=False,
    )

    result = service.validate(
        config
    )

    assert result["ready"] is False
    assert "output_folder_required" in result["errors"]


def test_workflow_supports_manual_review_mode():

    service = WorkflowService()

    config = service.create_config(
        input_folder="input",
        output_folder="output",
        use_input_folder_as_output=False,
        auto_repair=False,
        review_mode="manual",
    )

    result = service.validate(
        config
    )

    assert result["ready"] is True
    assert result["output_folder"] == "output"
    assert result["auto_repair"] is False
    assert result["review_mode"] == "manual"


test_match_text_with_multiple_mp3_by_chapter_number()
test_match_chapter_text_name_with_numbered_audio()
test_do_not_cross_match_different_chapter_numbers()
test_test_files_are_not_auto_matched_with_typo()
test_invalid_filename_is_reported()
test_chinese_is_not_classified_anymore_when_filename_has_chapter()
test_filename_content_mismatch_is_reported_and_not_rematched()
test_duplicate_is_reported()
test_dataset_repair_keeps_best_duplicate_and_copies_rest_to_ignored()
test_dataset_repair_skips_unsafe_errors_and_keeps_running()
test_dataset_review_creates_pending_items_from_repair_report()
test_dataset_review_approve_all_allows_train_after_review()
test_dataset_review_filter_by_reason_or_code()
test_health_report_summary()
test_train_audio_prep_stops_before_alignment_when_dataset_health_has_errors()
test_workflow_uses_input_folder_as_output_by_default()
test_workflow_requires_output_folder_when_not_using_input()
test_workflow_supports_manual_review_mode()

print("DATASET_MATCHING_TEST_OK")
