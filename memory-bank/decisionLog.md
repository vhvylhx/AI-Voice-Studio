# Decision Log — AI Voice Studio

## Quyết định kiến trúc và an toàn

- Giữ luồng bắt buộc: UI → Page/Controller → Service → Job Queue → Engine Manager → Engine Adapter → Runtime.
- Không dùng display name, filename hoặc path làm identity khi immutable ID đã có.
- Voice rename không đổi `voice_id`, model path, liên kết, Project, Session hoặc frozen artifact lineage.
- Variant và Style không phải model; `speed` là Generate parameter.
- Generate Request và Generate Session là hai thực thể tách biệt; frozen Plan không được đổi semantic.
- Production runtime chưa tích hợp/validate không được tạo audio, WAV, MP3, checkpoint, model hoặc artifact giả.

## Quyết định capability hiện hành

- GPT-SoVITS runtime hiện tại không có Vietnamese frontend hợp lệ cho `vi`; không được fake-map sang ngôn ngữ khác.
- GPT-SoVITS preprocessing/training tiếng Việt tiếp tục `BLOCKED` cho tới khi có runtime hoặc patch hợp lệ, đã validate.
- VieNeu CPU canary không đồng nghĩa production READY; manual listening review và production integration vẫn là gate bắt buộc.
- Generate production, Preview Audio, WAV/MP3 output phải phản ánh riêng trạng thái runtime/asset/real-smoke thực tế.

## Quyết định kiểm soát thay đổi

- Không tự thực hiện Git write operations.
- Không sửa, xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật của người dùng.
- Test fake/mock chỉ được dùng trong test composition và không được làm thay đổi production readiness.