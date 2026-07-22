# Inspection

## Quy tắc bắt buộc

Inspection luôn diễn ra trước implementation và chỉ ở chế độ đọc.

Không sửa file trong giai đoạn inspection.

Không suy đoán source, contract, dependency, caller, trạng thái capability hoặc hành vi runtime khi chưa đọc source hiện tại.

## Phạm vi cần đọc

Tùy task, luôn kiểm tra các thành phần liên quan:

- Rules hiện hành.
- Memory Bank hiện hành.
- Caller của code hoặc contract cần thay đổi.
- Dependency trực tiếp và dependency ngược có liên quan.
- Model, schema, immutable ID, persistence và data lineage.
- Service/application contract.
- UI/Page/Controller khi tác động tới luồng giao diện.
- Engine, runtime, job/queue và resource contract khi tác động tới công việc dài hoặc capability.
- Tests hiện có, fixtures, fake/mock composition và các assertion liên quan.

## Mục tiêu inspection

- Xác nhận source of truth hiện tại.
- Hiểu luồng gọi thực tế và các boundary kiến trúc.
- Phát hiện public contract, caller, persistence hoặc test có thể regression.
- Xác định file nhỏ nhất cần thay đổi.
- Phân biệt rõ production behavior với fake, mock, test-only hoặc placeholder.
- Xác định dữ liệu/source/artifact không được chạm tới.
- Đối chiếu source với tài liệu; khi có mâu thuẫn, source hiện tại được ưu tiên và mâu thuẫn phải được báo rõ.

## Không được làm trong inspection

- Không chỉnh source, test, docs, runtime profile hoặc cấu hình.
- Không chạy Git write operation.
- Không tự sửa vấn đề ngoài phạm vi.
- Không tự coi file tồn tại, command exit code hoặc test fake là production capability `READY`.