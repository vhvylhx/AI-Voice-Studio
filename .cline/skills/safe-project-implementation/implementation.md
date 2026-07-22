# Implementation

## Nguyên tắc triển khai

- Chỉ thay đổi sau khi inspection, planning và các approval bắt buộc đã hoàn tất.
- Áp dụng minimal diff: chỉ sửa file và dòng cần thiết để đáp ứng acceptance criteria.
- Giữ nguyên kiến trúc, boundary và luồng dependency hiện có.
- Giữ tương thích với public contract, caller, persistence, immutable ID, frozen snapshot và API behavior hiện hành.
- Tái sử dụng logic/service/validation hiện có khi phù hợp; không duplicate logic.

## Không được tự ý làm

- Không refactor ngoài phạm vi task.
- Không format hàng loạt.
- Không rename file, class, public function hoặc public contract.
- Không đổi encoding.
- Không đổi line ending.
- Không đổi workflow hoặc state machine.
- Không thêm dependency khi dependency hiện có hoặc Python standard library đáp ứng yêu cầu.
- Không tạo abstraction thừa.
- Không đưa business logic vào Widget.
- Không thêm đường gọi tắt từ UI/Page/Controller đến Repository, Worker, Engine Manager, Engine Adapter hoặc Runtime.
- Không dùng Git write operation nếu không có yêu cầu rõ ràng của người dùng.

## An toàn dữ liệu và capability

- Không sửa, ghi đè, di chuyển, đổi tên hoặc xóa dữ liệu thật ngoài workflow/policy đã được phê duyệt.
- Không tạo audio, model, checkpoint, artifact hoặc output giả để biểu diễn thành công.
- Không nâng trạng thái `READY` từ fake/mock/test-only, cache, file tồn tại hoặc command exit code.
- Không tự thêm fallback engine, runtime, CPU/GPU hoặc language route khi policy và request chưa cho phép rõ ràng.

## Khi phát hiện vấn đề ngoài phạm vi

Không tự sửa. Báo rõ tác động, lý do và rủi ro; chờ người dùng quyết định.