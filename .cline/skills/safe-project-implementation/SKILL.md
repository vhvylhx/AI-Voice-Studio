---
name: safe-project-implementation
description: Use for every source-code implementation, bug fix, feature development, integration, migration and repository modification task. Inspect current source and tests first, preserve architecture and UTF-8, use explicit decision gates, validate with evidence, and never make product decisions without user approval.
---

# Safe Project Implementation

Skill này là quy trình điều phối chính cho mọi task thay đổi repository: triển khai source code, bug fix, feature development, integration, migration, test, documentation hoặc repository metadata được phép.

Skill quy định cách thực hiện an toàn; không thay thế `AGENTS.md`, `.clinerules/`, Memory Bank, source contract, test contract hoặc chỉ dẫn task cụ thể.

## Shared Framework bắt buộc

Đọc và áp dụng tài liệu tương ứng trong [`../shared/`](../shared/README.md):

- [Operating Modes](../shared/operating-modes.md): chọn mode, scope protection, failure/retry, context recovery, large-task strategy và Git awareness.
- [Decision Gates](../shared/decision-gates.md): product/architecture/compatibility/data/resource/security/readiness gates.
- [Validation Contract](../shared/validation-contract.md): evidence ladder, regression prevention và compatibility checks.
- [Reporting Contract](../shared/reporting.md): evidence notation, report integrity và final-status discipline.

## Workflow bắt buộc

```text
0. Select Mode and Protect Scope
   ↓
1. Read Rules and Current Project Truth
   ↓
2. Inspect Source, Callers, Dependencies and Tests
   ↓
3. Define Evidence-based Acceptance Criteria
   ↓
4. Classify Change and Evaluate Decision Gates
   ↓
5. Plan Vertical Slices and Validation
   ↓
6. Obtain User Approval when a Gate Requires It
   ↓
7. Implement One Slice at a Time
   ↓
8. Run Targeted Validation after Each Slice
   ↓
9. Perform Compatibility, Safety and Diff Review
   ↓
10. Run Scope-appropriate Final Validation
   ↓
11. Complete with Evidence, Limitations and Allowed Final Status
```

Không nhảy từ task request sang edit. Nếu cần evidence mà chưa có, dùng `Investigation`; nếu task chạm decision gate, dừng trước Implementation.

## Phase Contract

### 0. Select Mode and Protect Scope

- Xác định `Planning`, `Investigation`, `Implementation`, `Validation`, `Review` hoặc `Recovery`.
- Liệt kê requested scope, allowed paths, excluded paths và dữ liệu/thao tác bị cấm.
- Kiểm tra worktree read-only trước edit; không gán thay đổi sẵn có cho task.
- Với task nhiều file, chia theo vertical slice có owner file, contract/caller, risk và targeted validation riêng.

### 1–2. Read and Inspect

Đọc theo thứ tự nguồn sự thật bắt buộc của dự án, sau đó đọc **toàn bộ** source liên quan, callers, dependencies và tests liên quan.

Không suy đoán:

- source behavior từ tên file/symbol;
- runtime readiness từ executable/cache/mock;
- ownership từ path/display name;
- artifact success từ Job success/file tồn tại;
- UI state từ selection hiển thị.

### 3–5. Define and Plan

Trước edit phải có:

- expected/current behavior có evidence;
- acceptance criteria quan sát được;
- affected contracts, callers và persistence/identity impact;
- resource/data/security/readiness impact;
- smallest safe change;
- validation strategy cho từng criterion;
- rollback/recovery implication khi scope chạm data, process hoặc persisted state.

Dùng [planning.md](planning.md), [inspection.md](inspection.md) và [checklists.md](checklists.md) làm checklist chi tiết.

### 6. Decision Gate

Xin user approval trước implementation khi thay đổi product semantics, architecture, API/schema compatibility, data operation, resource policy, security exposure hoặc production readiness theo [Decision Gates](../shared/decision-gates.md).

Không xem một user request chung là approval cho mọi side effect ngoài scope.

### 7–8. Implement and Validate by Slice

- Chỉ sửa minimal diff cần để đạt acceptance criteria.
- Không refactor, rename, cleanup hoặc dependency addition không cần thiết.
- Không bypass flow `UI → Page/Controller → Service → Job Queue → Engine Manager → Engine Adapter → Runtime`.
- Không đặt business workflow trong Widget, không để Worker phụ thuộc UI/open Project.
- Không sửa trực tiếp persistence để ép state, lineage, readiness hoặc success.
- Sau mỗi slice: đọc lại file đã sửa, chạy targeted validation, review diff scope và cập nhật context snapshot.

Khi failure xuất hiện, quay về `Investigation`; không suppress, catch rộng, sửa test assertion hoặc retry mù để che failure.

### 9–10. Final Review and Validation

Áp dụng [review.md](review.md), [validation.md](validation.md) và [Validation Contract](../shared/validation-contract.md).

Tối thiểu theo scope khi khả thi:

- targeted tests;
- `python -m compileall src tests` cho thay đổi Python;
- relevant UI/API/bootstrap/runtime smoke khi scope chạm boundary đó;
- `git diff --check`;
- `git status --short` read-only.

Không chạy operation có thể tác động dữ liệu thật, workload nặng hoặc production runtime khi contract/resource policy chưa cho phép.

### 11. Completion

Dùng [completion.md](completion.md) và [Reporting Contract](../shared/reporting.md). Báo chính xác work performed, file, commands/results, limitations, pre-existing issues, blockers và residual risks.

Final Status chỉ dùng một giá trị được `AGENTS.md` cho phép:

- `READY_FOR_GITHUB_REVIEW`
- `SOURCE_DOCS_TESTS_READY`
- `WORKTREE_NOT_CLEAN_DUE_TO_REAL_USER_DATA`
- `NOT_READY`

Không dùng `READY_FOR_GITHUB_REVIEW` khi required validation chưa chạy/pass hoặc capability chỉ được chứng minh bằng fake/test-only.

## Non-negotiable Guardrails

- Giữ UTF-8 và tiếng Việt; không gây line-ending churn ngoài scope.
- Không Git write operation nếu người dùng chưa yêu cầu rõ.
- Không tạo fake audio, model, checkpoint, artifact hoặc production readiness.
- Không silent overwrite, delete, move, rename hoặc modify dữ liệu thật.
- Không map giả language, không fallback runtime/resource/engine ngầm.
- Không biến Job success, exit code 0, file tạm hoặc test pass thành Artifact/Unit/production success.
- Không báo “completed” nếu có required blocker, unclassified failure hoặc validation gap quan trọng.