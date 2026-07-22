# Job, Queue và tài nguyên — AI Voice Studio

## Phạm vi

Áp dụng cho mọi công việc dài, có thể retry/resume hoặc tiêu thụ tài nguyên đáng kể, gồm Generate execution, preprocessing, train, alignment, export/import lớn, backup/restore và kiểm tra runtime nặng.

## Ownership và identity

- Mọi Job phải có `job_id` bất biến và mang các immutable ID cần thiết theo contract, tối thiểu là `project_id` và `session_id` khi ngữ cảnh đó tồn tại.
- Worker chỉ đọc payload/snapshot của Job đã được persist; không đọc Project đang mở, lựa chọn đang hiển thị hoặc state tạm của UI.
- Display name, folder name, filename và path không được dùng làm khóa Job, idempotency key hoặc khóa resume khi immutable ID đã tồn tại.
- Retry tạo `attempt_id` mới nhưng giữ nguyên identity và semantic snapshot đã freeze của Job/Session/Plan/Unit.
- Không dùng một Job thành công để suy diễn rằng Unit, Artifact hay toàn bộ Session đã thành công.

## State machine và điều phối

- Mọi chuyển state phải đi qua state machine/service hiện có; không sửa JSON persistence trực tiếp để ép state.
- Worker phải honor pause, cancel, dependency và timeout theo contract trước và trong quá trình thực thi.
- Job bị pause/error/cancel phải lưu state, log và thông tin recovery cần thiết; không tự xóa dữ liệu điều tra.
- Resume chỉ tiếp tục từ checkpoint/attempt/artifact đã được validate. Không tạo Job mới để né resume contract và không chạy lại phần đã hoàn thành hợp lệ.
- Dependency chưa thành công, bị hủy hoặc không còn hợp lệ phải làm Job phụ thuộc dừng với trạng thái/blocker trung thực, không âm thầm chạy tiếp.
- Idempotency phải dựa trên payload/snapshot bất biến; không dựa trên thời điểm chạy hay state UI.

## ResourceRequirement và lease

- Job nặng phải khai báo `ResourceRequirement` trước khi Worker chạy, gồm các tài nguyên phù hợp như GPU/VRAM, CPU, RAM, disk, process exclusivity hoặc network.
- Resource preflight phải đánh giá điều kiện thực tế trước khi acquire/run; không dùng tên GPU, cấu hình cũ hoặc test fake để suy đoán đủ tài nguyên.
- Resource lease phải được acquire trước phần cần tài nguyên và release ở mọi nhánh success, failed, timeout, cancel và exception.
- Không CPU/GPU fallback tự động nếu request/profile/policy không cho phép rõ ràng.
- Không xếp chồng workload GPU nặng khi policy/lease không cho phép; phải trả `BLOCKED`, `DEGRADED` hoặc chờ queue theo trạng thái thật.
- Thiếu disk/RAM/VRAM, process xung đột hoặc resource telemetry không đủ phải được ghi rõ vào Job/report; không được tiếp tục để tạo artifact dở dang rồi báo thành công.

## Logging, recovery và an toàn dữ liệu

- Job log phải gắn `job_id`, `attempt_id` khi có, stage và thời điểm; không ghi API token, secret hoặc path nhạy cảm vào API response/log công khai.
- Recovery chỉ được phân loại và báo cáo temp/orphan theo policy hiện có; không tự xóa hoặc promote artifact orphan.
- Temp phải nằm trong workspace/cache được quản lý theo `job_id`, không nằm trong output final hoặc thư mục dữ liệu gốc.
- Job không được sửa, xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong `projects/`, `workspace/`, `voices/`, `outputs/`, `backups/`, `exports/`, Reference Vault hoặc Dataset người dùng nếu task/policy chưa cho phép rõ.
- Test worker, fake handler và mock resource manager chỉ được đăng ký trong test composition; chúng không được mở khóa readiness production.