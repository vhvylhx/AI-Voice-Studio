# Voice DNA Architecture

## AVS-014.12 Clarification

Voice DNA / Reading Style Profile khong phai Speaker Reference.

- Voice DNA mo ta cach doc, pacing, pause, emphasis, intonation va fingerprint doc.
- Speaker Reference mo ta audio/transcript tham chieu de clone chat giong/timbre.
- Training Dataset la du lieu de train model/checkpoint.

TrainingPage co the khoi tao draft Style Profile tu audio + text, nhung Style Profile domain van la owner cua profile va extraction state. Khi chua co analyzer that, draft khong duoc danh dau ready.

Rename Style Profile chi doi display name; `style_profile_id` bat bien va tiep tuc la khoa lien ket voi Voice/Variant/Training Reference.

## Mục tiêu

Voice DNA trong AI Voice Studio là lớp dữ liệu tham chiếu cho phong cách đọc: nhịp, pause, pacing, emphasis, breathing, intonation và fingerprint đọc. Nó không phải Voice model và không thay thế GPT/SoVITS checkpoint.

## Ranh giới chính

- Voice lưu danh tính, dataset, model, runtime, preview và metadata.
- Variant là Generate Profile, không chứa checkpoint, dataset hoặc weight.
- Reading Style Profile là dữ liệu phân tích phong cách đọc có ID riêng dạng `style_000001`.
- Một Reading Style Profile có thể dùng lại cho nhiều Voice.
- Generate Engine chỉ nhận request đã validate; engine không quản lý Voice, Variant, Project hoặc Style Profile.

## Thành phần

- `StyleProfile`: schema model cho Reading Style Profile.
- `StyleProfileRepository`: lưu/đọc/migrate/backup dữ liệu style profile.
- `StyleProfileService`: API nghiệp vụ để tạo, liệt kê, kiểm tra readiness và liên kết Voice.
- `StyleProfileExtractionService`: contract cho extraction thật sau này; hiện không giả lập hoàn tất.
- `StyleProfileIntegrityService`: kiểm tra file bắt buộc và JSON integrity.
- `StyleProfileExportService`: export/import gói `.avstyle`.

## Trạng thái extraction

Sprint AVS-014.11 chỉ tạo foundation. Nếu chưa có analyzer thật, trạng thái extraction phải là `extraction_pending`, `source_ready`, `degraded` hoặc `blocked`, không được báo `ready` giả.

## Local API

Local API thêm các endpoint an toàn:

- `GET /api/v1/style-profiles`
- `GET /api/v1/style-profiles/{style_profile_id}`
- `GET /api/v1/style-profiles/{style_profile_id}/readiness`
- `GET /api/v1/voices/{voice_id}/style-profile`

API chỉ trả metadata an toàn, không trả path runtime/model/checkpoint hoặc checksum nội bộ.
# AVS-014.13.1 Style draft source persistence

Style Profile co `source_assets` de giu audio/text/manifest asset IDs cua draft source.

Analyzer chua co thi khong tao Voice DNA gia, nhung source da chon van duoc giu trong Reference Vault.
