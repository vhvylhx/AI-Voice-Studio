---
name: bugfix
description: Diagnose and fix a confirmed defect with the smallest safe change. Require evidence, preserve existing contracts, add focused regression prevention, and do not hide failures.
---

# Bugfix

Dùng khi behavior hiện có đã được xác nhận là sai, crash, inconsistent hoặc failing validation. Skill này không dùng để mở rộng tính năng, refactor cơ hội hoặc thay đổi product semantics.

Áp dụng [`safe-project-implementation`](../safe-project-implementation/SKILL.md) và Shared Framework, đặc biệt:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

## Required Workflow

```text
1. Investigation: collect defect evidence and establish baseline
   ↓
2. Reproduce safely or explain why reproduction is unavailable
   ↓
3. Read affected source, callers, dependencies and tests
   ↓
4. Prove root cause, expected contract and affected failure paths
   ↓
5. Evaluate decision/compatibility/data/resource gates
   ↓
6. Plan the smallest safe fix and regression validation
   ↓
7. Implement only the confirmed root-cause fix
   ↓
8. Validate reproduction, regression, compatibility and diff scope
   ↓
9. Report evidence, limitation and allowed final status
```

## Investigation Requirements

Trước edit, ghi rõ:

- symptom/error/log/failing test/reproduction evidence;
- expected behavior và actual behavior;
- affected inputs, callers, state/data and environment;
- baseline: lỗi có sẵn, introduced by current diff hay chưa xác định;
- root cause có direct source/test evidence;
- failure/exception/cancel/retry/cleanup paths bị ảnh hưởng;
- regression risk và test seam.

Nếu không tái hiện được, không suy đoán root cause. Dùng evidence có sẵn, nêu limitation và chỉ tiếp tục khi source contract chứng minh rõ fix an toàn.

## Fix Constraints

- Chỉ sửa root cause đã xác nhận và required caller/test adaptation.
- Không catch exception rộng, suppress error, return fake success hoặc bỏ validation để làm symptom biến mất.
- Không đổi default behavior, public API, persistence schema, architecture, resource policy hoặc readiness semantic nếu chưa qua Decision Gate.
- Không sửa test assertion để khớp behavior sai; regression test phải mô tả contract đúng.
- Không dùng production data/runtime fake artifact để tái hiện hoặc xác nhận fix.
- Không sửa lỗi ngoài scope; ghi chúng là `PRE-EXISTING` hoặc `RISKS`.

## Regression and Validation

Theo [Validation Contract](../shared/validation-contract.md):

1. Chạy reproduction/failing test trước fix nếu an toàn.
2. Thêm hoặc cập nhật targeted regression test khi contract có seam hợp lý.
3. Chạy targeted test sau fix.
4. Kiểm tra caller/compatibility nếu contract chạm interface, persistence hoặc state.
5. Chạy compile/smoke theo scope.
6. Chạy `git diff --check` và `git status --short` read-only.

Test pass bằng fake/mock không là bằng chứng production runtime/readiness.

## Required Report

```text
## BUG EVIDENCE
## BASELINE AND REPRODUCTION
## ROOT CAUSE
## FIX
## REGRESSION PREVENTION
## VALIDATION
## NOT TESTED / LIMITATIONS
## RISKS AND PRE-EXISTING ISSUES
## FILES CHANGED
## FINAL STATUS
```

Final Status phải dùng vocabulary của `AGENTS.md` và chỉ phản ánh evidence đã có.