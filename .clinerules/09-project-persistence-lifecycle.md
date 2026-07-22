# Project, Persistence và Lifecycle — AI Voice Studio

## Project identity và ownership

- Mỗi Project phải dùng `project_id` bất biến làm identity; display name, thư mục hiển thị, filename và path không phải khóa thay thế khi `project_id` đã tồn tại.
- Đổi tên Project chỉ thay đổi metadata được workflow cho phép; không được làm thay đổi `project_id`, Voice ID, Reference ID, Session/Plan đã freeze, artifact lineage hoặc liên kết đã persist.
- Mọi entity thuộc Project phải giữ immutable ID và ownership rõ ràng. Không suy diễn ownership từ path hiện tại, thư mục đang mở, tên file hoặc UI selection.
- Service/Repository phải resolve Project và entity liên quan bằng immutable ID đã persist; không fallback theo display name hoặc path.
- Worker không đọc Project đang mở trên UI. Job cần Project context phải mang `project_id` cùng các snapshot/ID cần thiết trong payload đã persist.

## Persistence và thay đổi state

- Repository chỉ chịu trách nhiệm persistence; business workflow, validation gate và state transition phải nằm ở Service/state machine theo kiến trúc hiện có.
- Không sửa trực tiếp JSON registry, manifest, metadata hoặc file persistence để ép rename, repair state, Job success, Artifact valid hay capability readiness.
- Mọi ghi dữ liệu phải tuân thủ naming, collision và transaction policy hiện có; không silent overwrite Project registry, manifest, backup, export hay artifact.
- Khi persistence/validation thất bại, phải giữ lỗi/evidence có thể hành động và tránh tạo entity nửa vời ở trạng thái usable.
- Không tự sinh lại immutable ID để khớp name/path hoặc để xử lý collision; collision phải đi qua workflow/policy phù hợp.

## Import, export, backup và restore

- Import/export/backup/restore phải giữ identity, metadata và lineage theo contract. Không coi folder name hoặc file name là mapping đủ tin cậy.
- Restore/import phải validate format, integrity, version compatibility, ID collision và ownership trước khi persist bất kỳ thay đổi nào.
- Không ghi đè registry, Project, Voice, Reference, output hoặc backup hiện có nếu chưa có policy và xác nhận explicit của workflow.
- Migration/relink chỉ được thay đổi mapping mà contract cho phép; không được sửa source evidence, immutable ID hoặc frozen lineage.
- Phát hiện Project/manifest/artifact missing, orphan hoặc suspicious phải được phân loại, lưu evidence và báo cáo; không tự xóa, tái tạo, promote hoặc silent repair.

## Data safety và kiểm thử

- Không sửa, xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong `projects/`, `workspace/`, `voices/`, `outputs/`, `backups/` hoặc `exports/` nếu task/policy không cho phép rõ ràng.
- Mọi test import/export/backup/restore/migration phải chạy trên temporary directory hoặc fixture riêng; không dùng Project/data production của người dùng.
- Test fixture, fake registry và mock repository không được đăng ký vào production composition hoặc dùng để suy diễn persistence/capability production đã `READY`.