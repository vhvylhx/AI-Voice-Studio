# Product Context — AI Voice Studio

## Người dùng và trải nghiệm

AI Voice Studio phục vụ workflow desktop để người dùng quản lý Project, Voice, dữ liệu huấn luyện, Reference, Style Profile, Job Queue và Generate Audio. Giao diện và hướng dẫn người dùng hiển thị bằng tiếng Việt.

## Các ranh giới domain

- **Project**: identity bằng `project_id`; đổi tên chỉ đổi display name.
- **Voice**: identity bằng `voice_id`; chứa dataset, model, runtime, preview và metadata.
- **Variant**: generate profile, không phải model.
- **Style Profile**: profile phong cách đọc có ID riêng, có thể tái sử dụng cho nhiều Voice.
- **Reference**: dùng stable asset ID/manifest khi đã có; path và filename chỉ là provenance hoặc legacy fallback.
- **Generate**: tách Generate Request khỏi Generate Session; Plan frozen không được đổi semantic.
- **Job**: dùng immutable `job_id`; queue, persistence, pause/cancel và resource scheduling là contract chung.

## Kỳ vọng an toàn

- Không xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong các thư mục Project, Workspace, Voice, Output, Backup, Export hoặc Reference Vault.
- Không sửa TXT/DOCX/audio gốc.
- Không silent overwrite output.
- Không tạo audio/model/checkpoint/artifact giả để mô tả thành công.
- Resume/Retry phải dùng snapshot, plan và immutable IDs đã freeze; không tự split/normalize/detect lại.

## Truth-status

Readiness được công bố theo từng capability, ví dụ `READY`, `DEGRADED`, `UNAVAILABLE`, `BLOCKED`, `MISSING` hoặc `TEST_ONLY`. Test fake/mock/provider test-only không làm capability production thành `READY`.