# Changelog

## AVS-001 đến AVS-012

### Added

- Phân tích kiến trúc và lập roadmap.
- Chuẩn hóa AppContext, EngineManager, Project, Workspace, Voice, Runtime và Engine Config.
- GPT-SoVITS Generate end-to-end.
- Dataset validation, manifest, report, ZIP protection, workspace scan và segmentation.

### Changed

- Chuẩn hóa contract chính giữa model/config/service/json cho Project, Workspace và Voice.
- Tách cấu hình máy cá nhân khỏi source sau test generate thật.

### Validation

- Các test core/workspace/event/settings được dùng làm baseline.
- Generate thật đã được kiểm chứng ở AVS-009, sau đó dọn dữ liệu test ở AVS-010.

### Notes

- AVS-014 Train thật chưa bắt đầu.

## AVS-013: Audio Alignment Pipeline

### Added

- Pipeline chuẩn bị audio train từ dataset/segmentation.
- Output cache gồm clip, transcript, metadata.list, alignment manifest/report và errors.log.

### Changed

- Không sửa audio/text gốc.
- Chỉ xử lý trong cache.

### Validation

- Chạy thử giới hạn nhỏ trên workspace Thu Minh.

### Notes

- Pipeline cần Faster-Whisper runtime ổn định để có timestamp thật.

## AVS-013.5: Faster-Whisper Runtime Validation

### Added

- Runtime validation cho Faster-Whisper.
- Trạng thái package_missing, model_missing, cuda_unavailable, model_load_failed, ready.
- Hỗ trợ model local/cache, device và compute_type.

### Changed

- Không tải model âm thầm.
- Metadata language thống nhất `vi`.

### Validation

- Kiểm tra package/model/runtime.
- Mock alignment test và chạy thật giới hạn nhỏ.

### Notes

- Runtime thật đã dùng model `small` local cache.

## AVS-013.6: Quality-First Dataset Alignment

### Added

- AlignmentQualityConfig tập trung ngưỡng.
- Word timestamp từ Faster-Whisper.
- Split clip dài theo sentence/word timestamp, không cắt giữa từ.
- Source report, weak_source, progress payload.
- RuntimeProfile model/service nền tảng.

### Changed

- metadata.list chỉ chứa valid clip được phép train.
- Weak source mặc định không ghi vào metadata.
- Ratio fallback không được dùng cho valid.

### Validation

- `python -m compileall src tests`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- Chạy thật giới hạn 1 source trên workspace Thu Minh: 19 valid, 9 suspicious, 0 errors.
- ffprobe clip valid: pcm_s16le, mono, 32000 Hz, duration 5.16s.

### Notes

- Cần review suspicious và hoàn thiện Text ↔ MP3 Matching Rules trước AVS-014.

## AVS-013.7: Text ↔ MP3 Matching Rules

### Added

- Ghép Text ↔ MP3 theo số chương trước.
- Hỗ trợ một text ghép nhiều MP3 cùng chương theo thứ tự part.
- Test cho matching theo chương, không ghép chéo số, bỏ file test và file có chữ Trung.

### Changed

- DatasetService ghi thêm `match_rule`, `match_key`, `audio_part` vào item/manifest.
- File có dấu hiệu `test` không được ghép tự động.

### Validation

- `python -m compileall src/services/dataset_service.py tests/test_dataset_matching.py`
- `tests/test_dataset_matching.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`

### Notes

- Chưa dùng ASR để xác minh nội dung ở bước matching; ASR vẫn thuộc bước alignment/quality sau đó.
- Dataset Health là bước tiếp theo trước AVS-014.

## AVS-013.8: Dataset Health

### Added

- TextMatchingService cho luật ghép Text ↔ MP3.
- Dataset Health report gồm total_mp3, total_text, matched, unmatched, ignored_test, ignored_chinese, filename_content_mismatch, duplicate, missing_audio, missing_text, usable_percent.
- Issue report có file, reason và suggestion.
- Chặn trước Alignment nếu Dataset Health có lỗi chặn.

### Changed

- DatasetService dùng TextMatchingService để chuẩn hóa tên, lấy số chương và phát hiện file test gần giống.
- Dataset manifest/report nâng schema lên 2 và chứa health.
- DatasetSegmentationService truyền Dataset Health lên bước sau.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- Chạy Dataset Health trên workspace Thu Minh: total_mp3 68, total_text 160, matched 54, missing_text 14, ignored_test 22, ignored_chinese 137, duplicate 1, usable_percent 79.41.

### Notes

- Workspace Thu Minh còn Dataset Health blocking_errors, cần xử lý trước AVS-014.

## AVS-013.9: Dataset Workflow

### Added

- WorkflowConfig model cho Input Folder, Output Folder và Use Input Folder as Output.
- WorkflowService để tạo, validate và resolve output folder.
- Config mặc định cho workflow dùng input folder làm output.
- Test workflow config/service.

### Changed

- TextMatchingService được đơn giản hóa: bỏ kiểm tra tiếng Trung, chỉ bỏ file test/gần giống test và trích số chương.
- DatasetService bỏ phân loại Chinese.
- Dataset Health chuyển sang các trường: total_mp3, total_text, matched, missing_audio, missing_text, duplicate, invalid_filename, test_version, filename_content_mismatch, usable_percent.
- File không lấy được số chương trả `invalid_filename`.
- File test/gần giống test trả `test_version`.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- Chạy Dataset Health trên workspace Thu Minh: total_mp3 68, total_text 160, matched 68, duplicate 55, test_version 22, usable_percent 100.0.

### Notes

- Chưa Train.
- Chưa Generate.
- Workspace Thu Minh vẫn còn blocking_errors do duplicate, test_version, broken_file và empty_file.

## AVS-013.10: Dataset Repair

### Added

- DatasetRepairService cho detect, repair, skip và report các lỗi Dataset Health.
- DatasetRepairConfig và DatasetRepairIssue để chuẩn bị Auto Repair hoặc Manual Review.
- WorkflowConfig bổ sung `auto_repair` và `review_mode`.
- Dataset Health đếm thêm `empty_file`, `empty_content` và `broken_file`.

### Changed

- Duplicate được repair an toàn trong cache bằng cách copy bản trùng vào ignored, không sửa file gốc.
- Các lỗi không sửa an toàn như broken_file, empty_file, missing_audio, missing_text, filename_content_mismatch, test_version và invalid_filename được skip/report để review.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- Chạy Dataset Health + Repair trên workspace Thu Minh: repaired 55 duplicate, skipped 42 lỗi còn cần review.

### Notes

- Chưa Train.
- Chưa Generate.
- AVS-014 chỉ nên bắt đầu sau khi review xong các skipped errors còn lại.

## AVS-013.11: Dataset Review

### Added

- DatasetReviewService để tạo review_report.json trước Alignment/Train.
- DatasetReviewConfig và DatasetReviewItem.
- Review item gồm source_audio, source_text, reason, suggestion và status pending/approved/rejected/ignored.
- Hỗ trợ approve_all, reject_all, ignore_all và filter theo reason/code.

### Changed

- Dataset workflow cập nhật thành Scan → Health → Repair → Review → Alignment → Train.
- TrainAudioPrepService có thể nhận review_report; nếu không có review_report thì vẫn chặn Dataset Health như trước.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- Chạy Dataset Health + Repair + Review trên workspace Thu Minh: 42 review items pending; approve_all làm train_allowed = True.

### Notes

- Chưa Train.
- Chưa Generate.
- AVS-014 chỉ nên bắt đầu sau khi người dùng chốt approve/reject/ignore cho review_report.
