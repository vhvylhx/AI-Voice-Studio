# Review

## Checklist review trước completion

Xác nhận từng mục phù hợp với phạm vi thay đổi:

- [ ] Architecture: giữ đúng boundary và luồng dependency đã được quy định.
- [ ] API: không phá public API schema, compatibility hoặc semantic status nếu không được yêu cầu.
- [ ] Regression: caller, contract và test liên quan đã được đánh giá.
- [ ] Performance: không thêm chi phí không cần thiết, polling, blocking UI hoặc công việc nặng sai layer.
- [ ] Resource: resource requirement, preflight, lease và blocker được giữ đúng khi có áp dụng.
- [ ] Encoding: không đổi encoding hoặc line ending ngoài yêu cầu rõ ràng.
- [ ] UTF-8: file sửa/tạo đọc được UTF-8 strict.
- [ ] Vietnamese text: UI/comment/thông báo người dùng bằng tiếng Việt khi có thay đổi UI.
- [ ] Capability state: trạng thái phản ánh production evidence thực tế.
- [ ] READY/BLOCKED: không báo `READY` khi gate thiếu; blocker `BLOCKED`, `UNAVAILABLE`, `MISSING` hoặc trạng thái khác phải trung thực.
- [ ] Immutable IDs: không dùng display name, filename hoặc path thay immutable ID.
- [ ] Dataset safety: source TXT/DOCX/audio và dữ liệu dataset không bị sửa trực tiếp.
- [ ] Training safety: không tạo checkpoint/model giả, không vượt validation/language/resource gate.
- [ ] Generate safety: không thay frozen semantic, không tạo artifact/audio giả, không silent overwrite.
- [ ] Git scope: diff chỉ chứa thay đổi đã được phê duyệt cho task hiện tại.

## Kết luận review

- Mọi mục chưa đạt phải được sửa, loại trừ khỏi phạm vi theo xác nhận người dùng hoặc ghi rõ trong `NOT TESTED`/`RISKS`.
- Không dùng review để hợp thức hóa thay đổi ngoài phạm vi hoặc thay thế validation cần thiết.