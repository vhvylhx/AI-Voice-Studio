# Coding Standards — AI Voice Studio

## Phạm vi thay đổi

- Đọc toàn bộ source và tests liên quan trước khi sửa.
- Chỉ sửa các file thực sự cần thiết cho task.
- Không tự refactor, đổi kiến trúc, đổi tên file, class hoặc public function ngoài phạm vi được yêu cầu.
- Không thêm dependency nếu Python standard library hoặc dependency hiện có đáp ứng yêu cầu.
- Giữ coding style nhất quán với source hiện tại.

## Quy ước ngôn ngữ

- UI hiển thị bằng tiếng Việt.
- Comment và thông báo hướng dẫn người dùng dùng tiếng Việt.
- Class, function, method, variable và module dùng tiếng Anh.
- Không đặt business logic trong Widget.
- UI chỉ gọi Page/Controller hoặc Service; không gọi Engine/Runtime trực tiếp.

## Kiến trúc và dependency

Luồng thực thi chuẩn:

```text
UI
→ Page/Controller
→ Service
→ Job Queue
→ Engine Manager
→ Engine Adapter
→ Runtime
```

- Service là application contract cho UI và API.
- Repository chỉ chịu trách nhiệm persistence; không đặt business workflow trong repository.
- Engine chỉ nhận request và trả result; không quản lý Project, Voice, Variant, Style hoặc UI state.
- Worker phải độc lập với Project đang mở trên UI.
- Job dài hoặc nặng phải mang immutable IDs cần thiết và `ResourceRequirement`.

## Identity và persistence

- Dùng immutable ID làm identity: `project_id`, `voice_id`, `variant_id`, `style_profile_id`, `reference_id`, `session_id`, `plan_id`, `unit_id`, `attempt_id`, `artifact_id`, `job_id`.
- Không dùng display name, filename hoặc path làm khóa khi immutable ID đã tồn tại.
- Rename chỉ thay đổi display metadata; không đổi ID, model path, lineage hoặc liên kết đã frozen.
- Không fallback theo tên hoặc đường dẫn khi contract đã có immutable ID.

## Data safety và artifact

- Không sửa hoặc ghi đè file TXT, DOCX, audio gốc.
- Không tự ý xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong `projects/`, `workspace/`, `voices/`, `outputs/`, `backups/`, `exports/` hoặc Reference Vault.
- Dataset processing chỉ ghi cache hoặc output được quản lý phù hợp.
- Không silent overwrite output hoặc artifact.
- Không tạo audio, WAV, MP3, model, checkpoint hoặc artifact giả trong production.
- Artifact chỉ được xem là thành công khi validation và lineage hợp lệ; job/provider/file tồn tại không tự đồng nghĩa success.

## Generate và runtime

- `speed` là tham số Generate, không phải lý do tạo Voice model mới.
- Variant và Style không phải checkpoint/model.
- Generate Request và Generate Session phải tách biệt.
- Frozen Plan không đổi semantic sau khi freeze.
- Resume/Retry không normalize, detect chapter, split hoặc thay frozen settings, selection, language route hay unit ID.
- Production capability phải phản ánh runtime thực tế; test fake/mock không được nâng trạng thái READY.