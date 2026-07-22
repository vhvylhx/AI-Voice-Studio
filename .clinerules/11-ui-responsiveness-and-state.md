# UI, khả năng phản hồi và trạng thái hiển thị — AI Voice Studio

## Phân lớp UI và điều phối

- Widget chỉ chịu trách nhiệm trình bày, nhập liệu và phát signal; không chứa business workflow, persistence, resource scheduling hoặc engine/runtime execution.
- UI chỉ gọi Page, Controller hoặc Service theo contract hiện có. Không thêm đường gọi trực tiếp từ Widget/Page sang Repository, Job Worker, Engine Manager, Engine Adapter hoặc Runtime.
- Mọi thao tác dài, có thể retry/resume hoặc tiêu thụ tài nguyên đáng kể phải đi qua Service/Job Queue; không chạy đồng bộ trên UI thread để né job lifecycle.
- UI không được suy diễn state từ Project đang mở, label đang hiển thị hoặc index của combobox khi contract đã có immutable ID/snapshot.
- Action UI phải truyền ID/snapshot hợp lệ tới layer điều phối; Worker không được đọc lựa chọn tạm hay state của Widget.

## Responsiveness và lifecycle

- Không block Qt event loop bằng I/O, subprocess, polling dài, xử lý audio/dataset/model nặng hoặc chờ Job hoàn tất trên UI thread.
- Progress, log và trạng thái Job phải được cập nhật qua event/signal hoặc cơ chế thread-safe theo kiến trúc hiện có; không truy cập Widget từ Worker thread.
- UI phải xử lý rõ lifecycle loading, queued, running, paused, blocked, cancelled, failed và completed; không để action bị treo hoặc hiển thị trạng thái cũ.
- Khi Page/Widget bị đóng hoặc Project selection thay đổi, không được để callback muộn ghi đè state của entity/selection mới. Phải kiểm tra correlation ID, immutable ID hoặc lifecycle token theo contract hiện có.
- Không tự tạo thêm polling loop, global state hoặc thread riêng nếu Service/event/job contract hiện có đáp ứng nhu cầu.

## Hiển thị capability, lỗi và recovery

- UI phải hiển thị readiness/blocker thực tế cho từng capability; không chuyển `UNAVAILABLE`, `BLOCKED`, `MISSING`, `DEGRADED` hoặc `TEST_ONLY` thành `READY` chỉ vì placeholder, test fake hoặc cache asset.
- Generate, Preview Audio, WAV Output, MP3 Output, preprocessing và training phải phản ánh trạng thái riêng; không dùng một trạng thái tổng quát làm bằng chứng tất cả đã sẵn sàng.
- Nội dung hướng dẫn, validation error và blocker hiển thị cho người dùng phải bằng tiếng Việt, có thể hành động và không che mất stage/recovery context cần thiết.
- Không báo thành công chỉ vì Job được queue, command exit code 0, file tạm tồn tại hoặc provider trả response; kết quả phải tương ứng với Unit/Artifact đã được validate theo contract.
- UI không được tạo audio, artifact, checkpoint, model hoặc file giả để tạo cảm giác thao tác đã thành công.

## Data safety, accessibility và kiểm thử

- UI action không được silent overwrite, đổi tên, di chuyển hoặc xóa Project, Voice, Reference, source TXT/DOCX/audio, output, backup, export hay workspace ngoài workflow/policy được phép.
- Dialog xác nhận không thay thế validation, ownership, collision, lineage hoặc readiness gate ở Service; mọi thay đổi dữ liệu vẫn phải đi qua workflow an toàn.
- Giữ text UI bằng tiếng Việt và duy trì layout có thể cuộn/co giãn theo design system hiện có; không hard-code kích thước làm mất nội dung hoặc action quan trọng ở độ phân giải Desktop hỗ trợ.
- UI test phải dùng temporary directory/test composition và không dựa vào dữ liệu Project/Reference/Workspace thật của người dùng.
- Thay đổi UI phải chạy UI smoke hoặc targeted UI tests phù hợp khi khả thi; nếu không chạy được phải ghi rõ command chưa chạy, lý do và rủi ro.