# Reporting Contract

Báo cáo phải tách biệt fact đã xác minh, inference có căn cứ, unknown, blocker và recommendation. Không mô tả ý định như kết quả đã hoàn thành.

## 1. Evidence Notation

Dùng nhãn sau khi cần làm rõ:

- `VERIFIED`: có source, diff, command, test hoặc artifact evidence cụ thể.
- `INFERRED`: kết luận hợp lý từ evidence nhưng chưa có direct proof; phải nêu basis.
- `UNVERIFIED`: chưa kiểm tra hoặc không thể kiểm tra.
- `BLOCKED`: không thể tiếp tục an toàn; nêu gate/cause/action needed.
- `PRE-EXISTING`: được quan sát trước task hoặc ngoài task scope; không quy cho thay đổi hiện tại.

## 2. Standard Change Report

```text
## Scope
- Requested:
- Allowed paths:
- Excluded paths:
- Execution mode:

## Evidence and Current State
- VERIFIED:
- INFERRED:
- UNVERIFIED:

## Work Performed
- <thay đổi hoặc review thực tế, theo file/contract>

## Validation
| Check | Result | Evidence | Limitation |
| --- | --- | --- | --- |
| <command/test/inspection> | PASS / FAIL / NOT RUN / BLOCKED | <result ngắn> | <không chứng minh được gì> |

## Compatibility and Safety
- Identity/persistence:
- Data/output:
- Resource/process:
- UI/API/architecture:
- Production readiness:

## Risks and Blockers
- <severity/status, evidence, impact, next safe action>

## Files
- Modified:
- Added:
- Deleted:
- Not touched:

## Final Status
- <status được Skill/AGENTS cho phép>
```

Với task read-only, `Work Performed` chỉ mô tả inspection/review; `Modified/Added/Deleted` phải ghi “Không có” nếu không có write được phép.

## 3. Review Finding Template

Mỗi finding phải có đủ:

```text
[<SEVERITY>] <ngắn gọn, mô tả tác động>
Location: `<path>:<line hoặc symbol>`
Evidence: <đoạn source/diff/test/command chứng minh>
Problem: <hành vi hoặc contract bị vi phạm>
Impact: <điều có thể xảy ra và phạm vi>
Recommendation: <sửa nhỏ nhất hoặc action an toàn>
Validation: <test/check nên thêm hoặc chạy>
```

Quy tắc:

- Không tạo finding dựa trên style preference, suy đoán hoặc vấn đề không liên quan acceptance criteria trừ khi có impact rõ.
- Nếu line không ổn định, dùng symbol/hunk và mô tả unique context.
- Không gộp nhiều lỗi độc lập vào một finding.
- Với false-positive risk, hạ certainty hoặc ghi `UNVERIFIED` thay vì khẳng định.
- `PRE-EXISTING` không ảnh hưởng verdict của task trừ khi nó block việc xác minh thay đổi.

## 4. Severity Guide

| Severity | Điều kiện |
| --- | --- |
| CRITICAL | Mất/ghi đè dữ liệu, security exposure nghiêm trọng, execution nguy hiểm, corruption identity/lineage hoặc capability sai có hậu quả nghiêm trọng. |
| HIGH | Regression chức năng chính, bypass architecture/safety gate, failure state sai, resource/process leak đáng kể hoặc break public contract. |
| MEDIUM | Edge case rõ ràng, validation thiếu có nguy cơ regression, compatibility gap hoặc UI/API behavior sai giới hạn. |
| LOW | Maintainability/observability/test clarity có impact nhỏ, không phá contract hiện tại. |
| INFO | Ghi chú không cần thay đổi trước merge/completion. |

Severity phản ánh impact và probability có evidence, không phản ánh độ dài diff hay mức độ khó sửa.

## 5. No-Finding Review Report

Khi không có finding, phải vẫn ghi:

- review scope và file/hunk đã xem;
- checks đã chạy và chưa chạy;
- limitation của review;
- pre-existing changes/issues nếu có;
- verdict hợp lệ.

Không dùng “không có finding” để tuyên bố production readiness, full correctness hoặc full coverage.

## 6. Completion Integrity

- Chỉ dùng exact final-status vocabulary của Skill hoặc `AGENTS.md`.
- Không dùng status có vẻ mạnh hơn evidence.
- Nêu rõ test chưa chạy và lý do thay vì bỏ qua.
- Nếu worktree dirty, nêu phần diff được xác định thuộc scope và phần không thuộc scope/không đụng tới.
- Không kết thúc bằng yêu cầu hoặc câu hỏi mở; decision gate phải được nêu trước completion.