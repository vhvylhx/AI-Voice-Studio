# Shared Skill Framework

Thư mục này chứa các hợp đồng workflow tái sử dụng cho toàn bộ Skill của AI Voice Studio. Các tài liệu này **không thay thế** `AGENTS.md`, `.clinerules/`, Memory Bank hoặc source hiện hành; khi có mâu thuẫn, nguồn quy tắc cấp cao hơn luôn được ưu tiên.

## Mục đích

- Giảm lặp lại các quy tắc workflow giữa Skill.
- Chuẩn hoá evidence, decision gate, validation và reporting.
- Giữ mỗi Skill tập trung vào mục tiêu chuyên biệt.
- Hỗ trợ task lớn, nhiều file, gián đoạn ngữ cảnh và review sâu mà không suy đoán.

## Tài liệu dùng chung

| Tài liệu | Mục đích |
| --- | --- |
| [operating-modes.md](operating-modes.md) | Xác định mode làm việc, scope protection, recovery và hiệu quả ngữ cảnh. |
| [decision-gates.md](decision-gates.md) | Xác định khi nào phải dừng để xin quyết định hoặc không được tiếp tục. |
| [validation-contract.md](validation-contract.md) | Chuẩn hoá evidence, chiến lược validation, compatibility và prevention regression. |
| [reporting.md](reporting.md) | Chuẩn hoá mẫu báo cáo, finding và cách nêu phần chưa xác minh. |

## Cách sử dụng

1. Skill chuyên biệt xác định mục tiêu, phạm vi và mode mặc định.
2. Đọc tài liệu chung phù hợp trước khi thực hiện bước tương ứng.
3. Áp dụng Rules, Memory Bank, source và test hiện hành theo thứ tự bắt buộc của dự án.
4. Không dùng template để thay thế việc kiểm tra source, test hoặc evidence thực tế.
5. Nếu task chỉ đọc, không được chuyển sang implementation chỉ vì template có mục implementation.

## Contract không thể nới lỏng

- Không tự thay đổi source, tests, runtime, dependency, dữ liệu thật hoặc Git history ngoài quyền hạn task.
- Không tuyên bố production capability, artifact, Unit, Job hay validation thành công khi evidence chưa đủ.
- Không coi fake/mock/test-only là bằng chứng production `READY`.
- Không suy đoán trạng thái source, caller, dependency, test, runtime hoặc dữ liệu người dùng.
- Không che blocker bằng fallback ngầm, báo cáo mơ hồ hoặc thay đổi ngoài scope.