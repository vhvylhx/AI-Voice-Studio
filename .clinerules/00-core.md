# Quy tắc cốt lõi — AI Voice Studio

## Phạm vi và kiến trúc

- AI Voice Studio là ứng dụng Desktop Windows dùng Python và PySide6, hướng tới NVIDIA GPU.
- GPT-SoVITS là engine chính hiện tại; kiến trúc phải cho phép mở rộng engine khác như XTTS, Fish Speech và engine tiếng Việt riêng.
- Không tự refactor, đổi kiến trúc, đổi tên file, class hoặc public function nếu task không yêu cầu rõ.
- Chỉ sửa các file thực sự cần thiết cho task.
- Nếu phát hiện vấn đề kiến trúc nghiêm trọng hoặc ngoài phạm vi, phải báo trước và chờ quyết định.

## Luồng xử lý bắt buộc

UI không được gọi Engine trực tiếp. Luồng chuẩn:

```text
UI
→ Page/Controller
→ Service
→ Job Queue
→ Engine Manager
→ Engine Adapter
→ Runtime
```

- Không đặt business logic trong Widget.
- Worker không phụ thuộc Project đang mở trên UI.
- Job phải mang `project_id`, `session_id` và các immutable ID cần thiết.
- Job nặng phải khai báo `ResourceRequirement` và được đánh giá tài nguyên trước khi Worker chạy.

## Identity và persistence

- Không dùng display name, filename hoặc path làm khóa định danh khi đã có immutable ID.
- Các ID đã tạo phải bất biến, bao gồm Project, Voice, Variant, Style, Reference, Session, Plan, Unit, Attempt, Artifact và Job.
- Đổi display name không được thay đổi ID, liên kết, model path hoặc frozen artifact lineage.
- Voice dùng `voice_id` làm identity; `display_name` chỉ là metadata.
- Variant không phải model; Style không phải Voice; một Voice chỉ có một model chính trừ khi capability riêng được triển khai thật.

## An toàn dữ liệu

Không tự ý sửa, xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong:

- `projects/`
- `workspace/`
- `voices/`
- `outputs/`
- `backups/`
- `exports/`
- Reference Vault
- Dataset người dùng

- File TXT, DOCX và audio gốc không được sửa.
- Mọi xử lý dataset phải thực hiện trong cache hoặc output quản lý phù hợp.
- Tests chỉ dùng temporary directory hoặc fixture riêng.
- Không tạo audio/model/artifact giả trong production để làm capability trông như READY.

## Generate và audio

- Generate Request và Generate Session phải tách biệt.
- Frozen Plan không được thay đổi semantic sau khi freeze.
- Resume/Retry không tự normalize, detect chapter, split lại, thay frozen settings/selection/unit ID.
- Unit chỉ thành công khi có Artifact hợp lệ; Job thành công không đồng nghĩa Unit thành công.
- Không silent overwrite output.
- `speed` là tham số Generate, không phải lý do tạo model mới.
- Runtime/engine chưa tích hợp thật thì Generate execution, Preview Audio, WAV output và MP3 output phải báo trạng thái thực tế là `UNAVAILABLE` hoặc `BLOCKED`, không được fake READY.

## Git và thay đổi

Không tự thực hiện Git write operations:

- commit, push, pull, merge, rebase
- reset, restore, clean, checkout, stash, tag

Chỉ dùng Git read-only khi cần: `git status`, `git diff`, `git diff --check`, `git log`.

## Ngôn ngữ

- UI hiển thị bằng tiếng Việt.
- Comment bằng tiếng Việt.
- Class, function và variable dùng tiếng Anh.