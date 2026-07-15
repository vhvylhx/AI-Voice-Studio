# Current Sprint

## Trạng thái hiện tại

- AVS-013 hoàn thành.
- AVS-013.5 hoàn thành.
- AVS-013.6 hoàn thành.
- AVS-013.7 Text ↔ MP3 Matching Rules hoàn thành.
- AVS-013.8 Dataset Health hoàn thành.
- AVS-013.9 Dataset Workflow hoàn thành.
- Sprint tiếp theo chưa bắt đầu.

## Mốc ổn định gần nhất

- Complete AVS-013.6: Quality-First Dataset Alignment.
- Complete AVS-013.7: Text ↔ MP3 Matching Rules.
- Complete AVS-013.8: Dataset Health.
- Complete AVS-013.9: Dataset Workflow.
- Git commit hiện tại: `3b583e1`.

## Thành quả chính

- Faster-Whisper chạy local.
- Timestamp thật và word timestamp.
- Chia clip dài không cắt giữa từ.
- Quality config tập trung.
- Metadata chỉ chứa valid clip được phép train.
- Weak source không train tự động.
- Progress payload cho job dài.
- Runtime Profile nền tảng.
- Text ↔ MP3 ghép theo số chương trước.
- Một text có thể ghép nhiều MP3 cùng chương theo thứ tự part.
- File test hoặc gần giống test không ghép tự động.
- File không lấy được số chương bị loại khỏi ghép tự động.
- Dataset Workflow có Input Folder, Output Folder và Use Input Folder as Output.
- Dataset Health báo lỗi trước Alignment.
- Dataset Health có lỗi chặn thì không chạy Alignment.

## Quyết định đã chốt

- Quality-first.
- `similarity_threshold = 90`
- `min_clip_duration = 2.0`
- `max_clip_duration = 10.0`
- `target_clip_duration = 6.0`
- `max_source_error_rate = 0.35`
- `min_valid_segments_per_source = 3`
- `allow_ratio_fallback = False`
- `sample_rate = 32000`
- `language = vi`

## Blocker còn lại

- Cần review suspicious.
- Cần xử lý Dataset Health errors của workspace Thu Minh trước AVS-014.
- Chưa bắt đầu AVS-014 Train thật.

## Task đề xuất tiếp theo

- Review và xử lý Dataset Health report.
- Sau đó mới AVS-014.

## File cần đọc khi quay lại

- AGENTS.md
- ROADMAP.md
- docs/Architecture.md
- CURRENT_SPRINT.md
- docs/DECISIONS.md
- src/services/alignment_service.py
- src/services/train_audio_prep_service.py
- src/models/alignment_quality_config.py
- src/services/runtime_profile_service.py
- src/models/runtime_profile.py

## Không được tự ý

- Không đưa suspicious vào metadata.
- Không hạ threshold để tăng dữ liệu.
- Không dùng ratio fallback cho valid.
- Không đổi Voice ID.
- Không phá portable path.
- Không hard-code ổ đĩa.

---

## Cập nhật AVS-013.10 Dataset Repair

- AVS-013.10 hoàn thành ở mức service/model/config.
- Dataset Repair phát hiện: duplicate, empty_file, broken_file, missing_audio, missing_text, filename_content_mismatch, test_version, invalid_filename.
- Duplicate được repair an toàn bằng cách giữ bản tốt nhất đã được DatasetService chọn và copy bản trùng vào cache ignored.
- Các lỗi không sửa an toàn được chuyển sang skipped để Manual Review, không dừng toàn batch.
- Workflow đã chuẩn bị lựa chọn Auto Repair hoặc Manual Review cho UI sau này.
- Kiểm tra workspace Thu Minh: repaired 55 duplicate, skipped 42 lỗi còn cần review trước AVS-014.

## Task tiếp theo

- Review các skipped errors còn lại trong Dataset Repair report.
- Chỉ bắt đầu AVS-014 sau khi Dataset Health/Repair không còn blocker train thật.

---

## Cập nhật AVS-013.11 Dataset Review

- AVS-013.11 hoàn thành ở mức service/model.
- Dataset Review hỗ trợ mode Auto/Manual thông qua DatasetReviewConfig.
- Review item gồm source_audio, source_text, reason, suggestion và status pending/approved/rejected/ignored.
- ReviewService hỗ trợ approve_all, reject_all, ignore_all và filter theo reason/code.
- Dataset chỉ được phép đi tiếp khi blocking_errors = 0 hoặc toàn bộ blocking_errors đã có trạng thái reviewed.
- TrainAudioPrepService có thể nhận review_report; nếu không truyền report thì hành vi chặn Dataset Health giữ nguyên như cũ.
- Kiểm tra workspace Thu Minh: sau Repair còn 42 blocking items; Review tạo 42 pending; approve_all làm train_allowed = True.

## Task tiếp theo

- Người dùng cần chốt approve/reject/ignore cho 42 review items của workspace Thu Minh trước AVS-014.
- Sau khi chốt Review mới bắt đầu AVS-014 Train thật.
