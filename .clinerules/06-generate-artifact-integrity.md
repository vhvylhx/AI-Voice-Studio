# Generate, Frozen Plan và Artifact — AI Voice Studio

## Tách thực thể và snapshot

- `GenerateRequest` chỉ mô tả ý định Generate; `GenerateSession` là bản ghi thực thi bất biến theo contract. Không gộp hai khái niệm này chỉ để đơn giản hóa UI hoặc persistence.
- Khi tạo Session/Plan, phải snapshot các input, lựa chọn Voice/Variant/Style/Reference, language route, setting Generate và immutable ID cần thiết theo contract hiện có.
- Source TXT, DOCX, pasted input và Reference gốc là dữ liệu nguồn; không sửa trực tiếp trong bước normalize, chapter detection, split hay execution.
- Frozen Plan không được thay đổi semantic sau khi freeze. Nếu người dùng đổi input/selection/settings ảnh hưởng semantic, phải tạo request/session/plan mới theo workflow hiện có.
- `speed` là tham số Generate; không dùng speed để suy luận model mới, Voice mới, Variant mới hoặc thay đổi frozen lineage.

## Unit, attempt và resume/retry

- Mỗi Unit phải giữ `unit_id` bất biến cùng snapshot/lineage cần thiết. Không dùng index hiển thị, text đã render hoặc filename làm identity thay thế.
- Retry tạo attempt mới theo contract nhưng không thay Unit ID, frozen text, split, selection, engine route hoặc settings đã freeze.
- Resume chỉ tiếp tục Unit/Attempt hợp lệ từ checkpoint đã validate; không normalize lại, detect chapter lại, split lại hoặc thay semantic snapshot.
- Job success, provider response thành công hoặc file tạm tồn tại không tự xác nhận Unit success.
- Khi Unit failure/cancel/blocked, phải lưu blocker và recovery context trung thực; không đánh dấu thành công để làm Session có vẻ hoàn tất.

## Artifact và lineage

- Unit chỉ thành công khi có Artifact hợp lệ, được validate theo contract và có lineage liên kết đúng tới Session/Plan/Unit/Attempt/Voice selection cần thiết.
- File tồn tại, metadata đơn lẻ, exit code 0 hay path có thể đọc không đủ để chứng minh Artifact hợp lệ.
- Artifact phải được persist qua service/repository phù hợp; không sửa trực tiếp manifest/JSON để ép success hoặc repair lineage.
- Không promote temporary file thành final Artifact khi validation, lineage, naming policy hoặc persistence transaction chưa hoàn tất.
- Artifact orphan/suspicious chỉ được phân loại, giữ evidence và xử lý theo recovery policy hiện có; không tự xóa, tự promote hoặc silent repair.

## Output và an toàn dữ liệu

- Không silent overwrite output, preview, WAV, MP3, manifest hay artifact đã tồn tại.
- Temp/intermediate output phải nằm trong workspace/cache được quản lý, không ghi vào thư mục output final hoặc dữ liệu nguồn trước khi hoàn tất validation.
- Không ghi, đổi tên, di chuyển hoặc xóa dữ liệu thật trong `outputs/`, `projects/`, `workspace/`, `voices/`, `exports/` hay Reference Vault nếu task/policy không cho phép rõ ràng.
- Khi execution/output capability chưa tích hợp hoặc chưa validate thật, phải trả `UNAVAILABLE`/`BLOCKED` với blocker có thể hành động; không tạo audio, WAV, MP3 hoặc Artifact giả để mô phỏng thành công.
- Preview Audio, WAV Output và MP3 Output phải được đánh giá readiness độc lập; không suy diễn từ discovery runtime, một file cache hay test fake.