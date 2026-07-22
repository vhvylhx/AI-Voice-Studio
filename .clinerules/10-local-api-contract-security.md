# Local API, Contract và Security — AI Voice Studio

## API thống nhất và phân lớp

- AI Voice Studio chỉ có một Local API dùng chung; không tạo API riêng theo từng Voice, engine, Widget hoặc Page.
- API endpoint chỉ gọi Service/application contract; không gọi trực tiếp Repository, Job Worker, Engine Manager, Engine Adapter hoặc Runtime.
- API không được phụ thuộc Project đang mở, selection trên UI hoặc state tạm của Widget.
- Request thực thi dài phải tạo/điều phối Job qua Service/Queue theo contract hiện có; API không tự chạy Engine/Runtime đồng bộ để né Job lifecycle.
- Không thay đổi public API schema, endpoint, semantic status hoặc compatibility behavior nếu task không yêu cầu rõ ràng.

## Identity, request và response

- API phải nhận và trả immutable ID phù hợp, gồm `project_id`, `voice_id`, `variant_id`, `style_profile_id`, `reference_id`, `session_id`, `plan_id`, `unit_id`, `attempt_id`, `artifact_id` và `job_id` khi ngữ cảnh tồn tại.
- Không dùng display name, filename hoặc path làm identity, lookup fallback, idempotency key hay key resume khi immutable ID đã tồn tại.
- API Generate phải hỗ trợ contract thống nhất gồm Voice ID, Variant, Speed, Emotion, Style, Similarity, Pitch và Volume; `speed` vẫn là tham số Generate, không phải model identity.
- Request cần frozen snapshot phải được tạo qua workflow Generate/Service hiện có; không cho API sửa Session, Plan, Unit hay attempt đã freeze.
- Response phải phân biệt kết quả request/Job/Unit/Artifact. Job queued hoặc command success không được biểu diễn như Artifact/Generate thành công.

## Capability, lỗi và observability

- API phải phản ánh capability production thực tế theo từng chức năng. Runtime chưa tích hợp/validate phải trả `UNAVAILABLE`, `BLOCKED` hoặc trạng thái thật tương đương.
- Không trả `READY` hay success chung chung chỉ vì fake provider, canary, cache asset, executable tồn tại hoặc test pass.
- Validation/resource/runtime/language blocker phải được trả theo contract với thông tin có thể hành động, không che lỗi bằng fallback ngầm.
- Response lỗi không được làm mất identity, stage hoặc recovery context cần thiết, nhưng không được lộ secret, token, nội dung nhạy cảm hay path máy cục bộ vượt policy.
- Log API phải có correlation/job/attempt ID phù hợp và không ghi token, password, secret hoặc dữ liệu nguồn không cần thiết.

## Security và thay đổi dữ liệu

- Local API phải tuân thủ authentication, bind address, CORS/origin, rate-limit và policy cấu hình hiện có; không tự mở rộng network exposure hoặc tắt guard bảo mật.
- Không nhận path tùy ý để đọc/ghi/xóa dữ liệu ngoài các workflow và thư mục được quản lý; phải validate ownership, identity và policy trước mọi thay đổi persistence.
- API không được silent overwrite Project, Reference, Voice, output, artifact, backup, export, workspace cache hay dữ liệu nguồn.
- Import/export/backup/restore qua API phải đi qua Service/Repository/validation workflow hiện có, giữ identity, lineage, collision policy và data safety.
- Tests API dùng temporary directory và test composition; mock/fake endpoint hoặc provider không được đăng ký làm production API capability.