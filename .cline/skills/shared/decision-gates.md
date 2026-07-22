# Decision Gates

Decision gate là điểm dừng bắt buộc. Skill phải nêu evidence, impact và lựa chọn; không tự chọn thay người dùng khi contract hiện hành chưa quyết định.

## 1. Gate Matrix

| Gate | Kích hoạt khi | Action bắt buộc | Không được làm |
| --- | --- | --- | --- |
| Product semantics | Đổi default behavior, workflow, naming, threshold, UX meaning, data handling hoặc output behavior. | `USER DECISION REQUIRED`. Nêu current behavior, options, trade-off và recommended safe option. | Suy đoán ý định hoặc âm thầm đổi default. |
| Architecture | Đổi dependency direction, layer responsibility, public contract, schema, queue/worker route, engine boundary hoặc persistence ownership. | Dừng và xin phê duyệt trước implementation. | Refactor “tiện tay”, bypass Service/Queue hoặc dùng adapter/runtime trực tiếp từ UI. |
| Compatibility | Đổi API/schema/file format/serialized state, migration behavior, ID semantics hoặc caller compatibility. | Đánh giá backward/forward compatibility, migration, rollback và test impact; xin quyết định nếu không có policy. | Break caller, tự migration dữ liệu thật hoặc tự sinh ID mới. |
| Data safety | Có thể đọc/ghi/di chuyển/xóa/đổi tên/ghi đè dữ liệu người dùng, artifact final, Project, Reference, Voice, dataset hoặc output. | Xác định ownership, policy, collision và rollback; chỉ tiếp tục khi workflow cho phép rõ. | Silent overwrite, direct manifest/JSON repair, dùng dữ liệu thật cho test. |
| Resource safety | Tăng GPU/CPU/RAM/disk/network/process use, concurrency, batch, subprocess hoặc fallback. | Xác minh ResourceRequirement, preflight, lease/release, timeout/cancel và recovery. | CPU/GPU fallback ngầm, chạy workload nặng từ UI thread, stack workload GPU không policy. |
| Production readiness | Tuyên bố `READY`, enable generate/train/preview/output hoặc đưa fake/mock vào production composition. | Kiểm tra runtime, asset, language, validation, real smoke và evidence theo capability riêng. | Suy diễn từ test, executable, cache, file tồn tại hoặc exit code 0. |
| Security/exposure | Đổi local API, auth, bind address, CORS, import path, subprocess/network boundary hoặc secret handling. | Threat-check input, authorization, path ownership, logging và test. | Mở network exposure, expose secret/path nhạy cảm, nhận path tùy ý. |

## 2. Required Decision Request

Khi gặp gate chưa được quyết định, báo theo cấu trúc:

```text
USER DECISION REQUIRED
Gate: <product semantics | architecture | compatibility | data safety | resource safety | production readiness | security>
Evidence: <source/rule/test/command evidence>
Current contract: <hành vi và giới hạn hiện tại>
Decision needed: <câu hỏi cụ thể>
Options:
1. <option an toàn + impact>
2. <option khác + impact>
Recommendation: <không phải quyết định thay người dùng>
Blocked work: <phần không thể tiếp tục>
```

Không đưa “tiếp tục bằng cách giả định” như một option mặc định.

## 3. Hard Stop Conditions

Dừng implementation/validation có thể gây thay đổi khi:

- Source/test/caller chưa đọc đủ để xác định contract.
- Worktree conflict hoặc thay đổi ngoài scope có nguy cơ bị ghi đè.
- Runtime, language, asset, resource hoặc security gate block execution.
- Test chỉ ra regression mà nguyên nhân chưa phân loại.
- Required test có thể tác động dữ liệu thật hoặc production runtime không an toàn.
- Evidence mâu thuẫn và chưa xác định nguồn ưu tiên.
- User yêu cầu capability trái Rules hoặc architecture nhưng chưa có quyết định thay đổi Rules.

## 4. Change Classification

| Loại thay đổi | Ví dụ | Mặc định |
| --- | --- | --- |
| Local safe implementation | Sửa lỗi đã tái hiện, giữ contract, thay đổi nội bộ có targeted test. | Có thể tiếp tục sau Investigation. |
| Contract-sensitive | Thay đổi model, Service signature, persistence, state transition, UI/API semantics. | Kiểm tra caller và compatibility; có thể cần gate. |
| Product-sensitive | Default, threshold, naming, workflow, Dataset/Generate/Training choice. | Luôn yêu cầu user decision nếu source không có policy rõ. |
| Operationally sensitive | Runtime, process, resource, output, path, import/export, API bind. | Cần evidence về safety/preflight/recovery trước execution. |
| Production claim | Readiness, success, artifact/model/audio output. | Chỉ được công bố theo evidence capability riêng. |

## 5. Approval Recording

Khi người dùng đã quyết định:

- Ghi nguyên văn hoặc tóm tắt trung thực decision và phạm vi áp dụng.
- Liên kết decision với file/contract/slice bị ảnh hưởng.
- Không mở rộng approval sang behavior tương tự nhưng chưa được nêu.
- Nếu implementation phát hiện impact mới, mở gate mới thay vì suy diễn approval còn hiệu lực.