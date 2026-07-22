# Planning

## Mục tiêu

Trước khi thay đổi repository, hiểu chính xác task và chuyển yêu cầu thành kế hoạch có thể kiểm tra được.

## Yêu cầu lập kế hoạch

- Xác định mục tiêu, hành vi mong muốn và phạm vi thực tế của task.
- Xác định acceptance criteria rõ ràng, có thể xác minh bằng source, test hoặc hành vi quan sát được.
- Liệt kê file cần đọc, file có thể cần sửa và file tuyệt đối không được sửa.
- Kiểm tra caller, dependency, public contract, persistence, compatibility và dữ liệu chịu ảnh hưởng.
- Xác định dependency hiện có trước khi đề xuất dependency mới.
- Đánh giá rủi ro về regression, data safety, resource, compatibility, capability/readiness và phạm vi Git.
- Xác định validation phù hợp: compile, targeted test, caller test, integration test, UI/API smoke hoặc kiểm tra khác theo phạm vi.

## Điều kiện phải dừng và hỏi người dùng

Dừng implementation và xin phê duyệt rõ ràng nếu task ảnh hưởng hoặc buộc phải quyết định về:

- Architecture.
- Workflow.
- Dataset.
- Training.
- Voice.
- Variant.
- Style.
- Generate.
- Publish.
- Resource policy.

Không tự quyết định product behavior, semantic contract, data policy, engine route, fallback, readiness hoặc thay đổi kiến trúc chỉ để hoàn thành task.

## Kết quả của giai đoạn planning

Kế hoạch phải nêu được:

1. Acceptance criteria.
2. Phạm vi thay đổi tối thiểu.
3. File cần sửa và file không được sửa.
4. Caller/dependency bị ảnh hưởng.
5. Rủi ro và biện pháp kiểm soát.
6. Validation sẽ chạy.
7. Điểm cần user approval, nếu có.