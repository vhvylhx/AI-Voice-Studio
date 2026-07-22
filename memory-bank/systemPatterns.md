# System Patterns — AI Voice Studio

## Phân lớp và trách nhiệm

- UI chỉ thể hiện tương tác và gọi Page/Controller/Service.
- Page/Controller điều phối thao tác giao diện, không gọi Engine/Runtime trực tiếp.
- Service là contract nghiệp vụ dùng chung cho UI và API.
- Repository chịu trách nhiệm persistence, không chứa business workflow.
- Job Queue điều phối công việc dài; Worker thực thi không phụ thuộc UI state.
- Engine Manager chọn/điều phối engine; Adapter cô lập contract engine; Runtime thực hiện tích hợp thực tế.

## Identity và persistence

- Dùng immutable ID thay vì display name, filename hoặc path khi ID đã tồn tại.
- Rename chỉ thay đổi display metadata; không thay đổi ID, model path, frozen lineage hoặc liên kết đã tồn tại.
- Không fallback theo name/path nếu contract đã có immutable ID.
- Persistence phải an toàn (atomic khi contract hiện tại yêu cầu) và không silent overwrite artifact.

## Generate patterns

- Tách Generate Request, Generate Session và frozen Plan.
- Snapshot source khi tạo session; không sửa source TXT/DOCX/pasted input.
- Plan frozen không đổi semantic sau freeze.
- Resume/Retry dùng session/plan/unit/attempt đã freeze; không normalize, detect chapter hoặc split lại.
- Unit chỉ thành công khi có Artifact hợp lệ với lineage; Job success không tự xác nhận Unit/Artifact success.
- Runtime/handler chưa tích hợp thật phải trả trạng thái thực tế như `UNAVAILABLE` hoặc `BLOCKED`, không giả lập output production.

## Test và readiness patterns

- Fake engine/mock runtime/test provider chỉ thuộc test composition.
- Tests dùng temporary directory hoặc fixture riêng, không dùng dữ liệu thật.
- Chạy targeted tests sau thay đổi; chạy các kiểm tra rộng hơn theo phạm vi trước khi kết thúc.
- Nếu không chạy được kiểm tra, báo rõ command chưa chạy, lý do và rủi ro còn lại.