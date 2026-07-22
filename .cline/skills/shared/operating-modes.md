# Operating Modes and Execution Control

Tài liệu này chuẩn hoá cách Skill chọn mode làm việc. Quy tắc của task, `AGENTS.md`, `.clinerules/`, Memory Bank và contract source vẫn có độ ưu tiên cao hơn.

## 1. Mode Selection

| Mode | Mục đích | Có được sửa repository? | Điều kiện thoát |
| --- | --- | --- | --- |
| Planning | Hiểu task, contract, risk, acceptance criteria và kế hoạch. | Không, trừ khi task cho phép file kế hoạch. | Kế hoạch có evidence hoặc bị block/đòi quyết định. |
| Investigation | Xác minh symptom, source, caller, dependency, test và phạm vi thực tế. | Không. | Root cause/phạm vi được chứng minh hoặc blocker được ghi rõ. |
| Implementation | Thực hiện thay đổi đã được phê duyệt trong scope. | Chỉ file được phép và cần thiết. | Mỗi thay đổi có lý do, caller/test impact và validation path. |
| Validation | Chứng minh thay đổi đáp ứng acceptance criteria. | Không sửa để “làm pass” nếu chưa quay lại Investigation/Implementation. | Evidence đủ hoặc gap/blocker được báo trung thực. |
| Review | Đánh giá diff và trạng thái kết quả độc lập với ý định triển khai. | Mặc định không. | Finding, validation gap và verdict có evidence. |
| Recovery | Khôi phục hiểu biết sau gián đoạn/failure mà không suy đoán. | Không, cho đến khi scope và state được xác minh lại. | Context snapshot và trạng thái repository được xác nhận. |

Không trộn mode: khi evidence thiếu, quay về `Investigation`; khi semantic/product decision xuất hiện, dừng tại `Decision Gate`; khi validation fail, không che failure bằng report.

## 2. Investigation Protocol

1. Đọc nguồn sự thật theo thứ tự bắt buộc của dự án.
2. Xác định task intent, requested scope, forbidden scope và acceptance criteria.
3. Đọc toàn bộ file liên quan, caller, dependency và tests trước khi kết luận.
4. Phân biệt fact, inference và unknown.
5. Dùng immutable ID/contract thay vì display name, UI state, path hoặc giả định runtime.
6. Ghi rõ evidence nguồn: file, vị trí, command output hoặc test result.
7. Không coi “không thấy lỗi” là bằng chứng absence nếu coverage chưa đủ.

## 3. Scope Protection

Trước khi implementation:

- Liệt kê allowed paths và explicitly forbidden paths.
- Kiểm tra worktree đã có thay đổi; không gán thay đổi có sẵn cho task hiện tại.
- Không mở rộng từ symptom sang refactor/cleanup/architecture change nếu không cần cho acceptance criteria.
- Không đổi public API, persistence schema, identity, default behavior, resource policy, runtime route hoặc readiness semantic khi chưa có quyết định rõ.
- Với task multi-file, định nghĩa responsibility của từng file trước khi sửa.
- Nếu thay đổi đòi hỏi file ngoài scope, dừng và nêu lý do, impact và lựa chọn an toàn.

Sau mỗi nhóm thay đổi, review diff theo scope; chỉ tiếp tục nếu diff vẫn giải quyết đúng mục tiêu.

## 4. Large Task and Multi-file Strategy

### Chia lát theo vertical slice

Mỗi slice phải có:

- mục tiêu quan sát được;
- contract/caller bị ảnh hưởng;
- file cần đọc và file được phép sửa;
- risk riêng;
- validation nhỏ nhất chứng minh slice;
- tiêu chí dừng hoặc decision gate.

Không sửa hàng loạt trước rồi mới hiểu tích hợp. Kết thúc một slice bằng targeted validation và diff review trước slice tiếp theo.

### Thứ tự ưu tiên

1. Contract/model/validation gate.
2. Service/state transition.
3. Queue/worker/engine boundary khi có.
4. UI/API caller.
5. Tests và documentation chỉ khi scope cho phép.

Không dùng thứ tự này để bypass architecture hiện có; nó chỉ là cách giảm regression và context loss.

## 5. Failure Handling and Retry

Khi command, test, validation hoặc edit thất bại:

1. Giữ nguyên evidence đầu ra; không bỏ qua lỗi.
2. Phân loại: environment, command invocation, existing failure, change-induced failure, missing dependency, product/architecture decision, data/resource safety blocker.
3. Kiểm tra state/diff trước retry; không retry destructive command hoặc operation trên dữ liệu thật.
4. Sửa nguyên nhân đã xác minh, không sửa assertion hay suppress error để che failure.
5. Retry tối đa khi có thông tin mới hoặc thay đổi điều kiện; retry lặp lại cùng lệnh không tạo evidence mới là không hợp lệ.
6. Nếu không thể tiếp tục, báo command, kết quả, nguyên nhân, impact và residual risk.

## 6. Context Recovery and Long Conversation Strategy

Sau gián đoạn, compact context hoặc task resumption:

1. Đọc lại task hiện tại và scope được phép.
2. Kiểm tra `git status --short`, `git diff --check` và diff giới hạn path task ở chế độ read-only.
3. Đọc lại file vừa sửa trước khi tạo diff edit mới.
4. Lập context snapshot: completed, pending, validation run/result, unverified, blockers và file ownership.
5. Không giả định tool call bị gián đoạn đã thành công.
6. Không dựa vào báo cáo cũ thay cho source/diff hiện tại.
7. Nếu state không thể phân biệt an toàn, dừng và báo `BLOCKED`.

## 7. Token and Tool Efficiency

- Bắt đầu từ cấu trúc, definitions và search có mục tiêu; chỉ đọc toàn file khi contract yêu cầu.
- Gom các thay đổi liên quan trong một file thành một edit có các block theo thứ tự file.
- Không đọc lặp nội dung đã có nếu state không đổi; đọc lại sau edit/formatter hoặc resumption.
- Ưu tiên targeted test trước full suite, nhưng không bỏ qua required validation do scope lớn.
- Không tạo script/fake artifact chỉ để quan sát nếu command/test hiện có đủ.
- Đầu ra dài phải được phân đoạn theo mục tiêu; không thay evidence bằng summary suy đoán.

## 8. Git Conflict Awareness

- Chỉ dùng Git read-only trừ khi task cho phép rõ thao tác khác.
- Khi worktree dirty, xác định diff thuộc task bằng path và hunk; không restore/clean/checkout/stash thay đổi khác.
- Nếu file cần sửa có hunk ngoài scope hoặc conflict marker, dừng để tránh ghi đè công việc khác.
- Không dùng Git history để thay thế việc đọc source hiện tại.
- Trước completion, xác minh diff chỉ nằm trong allowed paths và không có whitespace error.