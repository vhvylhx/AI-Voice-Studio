---
name: refactor-safe
description: Refactor existing code without changing externally observable behavior. Use only when refactoring is explicitly requested or required to safely complete an approved task.
---

# Safe Refactor

Chỉ dùng khi người dùng yêu cầu refactor rõ ràng hoặc refactor nhỏ là bắt buộc để hoàn thành task đã phê duyệt. Mục tiêu là cải thiện cấu trúc nội bộ **không thay đổi behavior quan sát được**.

Áp dụng [`safe-project-implementation`](../safe-project-implementation/SKILL.md) và Shared Framework:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

## Entry Gate

Trước edit phải chứng minh:

- refactor nằm trong requested scope hoặc là prerequisite kỹ thuật không thể tránh;
- existing behavior/public contract/default/error/state/persistence semantics đã được đọc;
- callers, dependencies và tests liên quan đã được đọc;
- behavior preservation criteria và validation baseline đã xác định;
- allowed paths và excluded paths rõ ràng.

Nếu refactor đồng thời đổi behavior, API, schema, default, resource policy hoặc workflow, không gọi là refactor an toàn: tách thành feature/decision gate.

## Workflow

```text
1. Investigate current behavior, callers and test baseline
   ↓
2. State invariants that must remain observable
   ↓
3. Identify smallest structural change and risk boundaries
   ↓
4. Add characterization coverage only when evidence is missing
   ↓
5. Refactor one slice without semantic change
   ↓
6. Run targeted behavior/compatibility validation and diff review
   ↓
7. Repeat only within approved scope
   ↓
8. Report preserved contracts, limitations and evidence
```

## Invariants to Preserve

Kiểm tra khi phù hợp:

- public functions/classes/endpoints and return/error semantics;
- defaults, ordering, timing, side effects and state transitions;
- immutable IDs, ownership, persisted format, lineage and collision behavior;
- UI text/action lifecycle and API response semantics;
- Job/Worker/Queue/Engine boundaries;
- resource acquisition/release/cancel/timeout behavior;
- capability statuses and blocker messages;
- encoding, Vietnamese text and line-ending scope.

Không đổi tên public symbol/file, move layer, add dependency, rewrite module hay “cleanup” unrelated chỉ vì refactor.

## Safe Implementation Rules

- Prefer extract/inline/local simplification with minimal diff over broad rewrite.
- Không đổi source of truth, persistence shape hoặc dependency direction.
- Không replace validated explicit flow bằng implicit fallback/abstraction không có test evidence.
- Không remove validation/error handling vì path “có vẻ không cần”.
- Không alter fake/test composition hoặc production composition boundary.
- Mỗi slice phải có before/after observable behavior và targeted validation.

## Validation

- Chạy baseline tests trước refactor khi an toàn/khả thi.
- Chạy targeted tests sau từng slice.
- Kiểm tra caller/import/serialization compatibility khi affected.
- So sánh diff để phát hiện semantic/default/exception/encoding drift.
- Chạy compile/smoke theo scope; cuối task chạy `git diff --check` và `git status --short` read-only.
- Nếu baseline fail, phân loại `PRE-EXISTING`/environment/change-induced trước khi kết luận.

## Required Report

```text
## REFACTOR SCOPE
## PRESERVED INVARIANTS
## BASELINE EVIDENCE
## STRUCTURAL CHANGES
## COMPATIBILITY AND SAFETY
## VALIDATION
## LIMITATIONS / PRE-EXISTING ISSUES
## FILES CHANGED
## FINAL STATUS
```

Final Status dùng exact vocabulary trong `AGENTS.md`.