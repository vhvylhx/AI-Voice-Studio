---
name: planning
description: Analyze a task and create a complete implementation plan before any code modification. Never change source code.
---

# Planning Skill

Skill này chỉ phân tích task và tạo implementation plan có thể thực hiện an toàn. Mặc định chỉ-đọc: không code, không sửa source/test/docs/Memory Bank và không chạy thao tác có side effect.

Áp dụng Shared Framework:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

## Entry Requirements

Trước khi công bố plan, phải có đủ evidence về:

- user intent, scope và non-goals;
- source-of-truth theo thứ tự Rules → Memory Bank → Architecture/Decisions → source → callers/dependencies → tests;
- existing behavior, contracts, extension points và constraints liên quan;
- acceptance criteria observable;
- files/layers affected và files explicitly excluded;
- compatibility, identity, data, resource, security và readiness impact;
- validation strategy khả thi cho từng implementation slice.

Không dùng tên file/class, report cũ, TODO, fake/mock pass hoặc runtime discovery để suy đoán behavior/capability production.

## Workflow

Thực hiện theo [`workflow.md`](workflow.md), xác nhận bằng [`checklist.md`](checklist.md), và trả report theo [`report.md`](report.md).

```text
1. Establish verified current state and task boundary
   ↓
2. Inspect source, callers, dependencies and related tests
   ↓
3. Define desired outcome, non-goals and observable acceptance criteria
   ↓
4. Classify decisions, risks and invariants
   ↓
5. Define smallest dependency-safe implementation slices
   ↓
6. Assign validation evidence for every slice and final integration
   ↓
7. Publish plan or stop with explicit blocker/decision request
```

## Decision Gate

Nếu task yêu cầu hoặc có thể buộc phải tạo **quyết định mới chưa được phê duyệt** về architecture, workflow, data semantics, default, naming, schema/API, persistence, security, resource policy, engine/runtime route, capability/readiness hoặc user-visible behavior:

**STOP BEFORE IMPLEMENTATION PLAN DETAILS THAT ASSUME THE DECISION.**

Báo theo template Decision Gate của Shared Framework. Không tự quyết định chỉ vì implementation “dễ hơn”.

Nếu decision đã được user/Rules/DECISIONS phê duyệt, ghi evidence và lập plan trong boundary đã phê duyệt; không yêu cầu xác nhận lại.

## Plan Quality Rules

- Plan phải dùng existing service/repository/queue/engine/UI boundary, không tự tạo path song song.
- Mỗi step nêu rõ file/module dự kiến, purpose, preserved invariant, caller/dependency impact và validation.
- Không đổi immutable ID, frozen snapshot, lineage, persistence contract, public API/default hay capability state trừ khi approval evidence cho phép.
- Với long-running/heavy work, plan phải nêu Job identity, snapshot, ResourceRequirement/preflight/lease và cancel/retry/resume implications.
- Với runtime/generate/train/output, plan phải tách production readiness khỏi fake/mock/test evidence.
- Không liệt kê “có thể refactor” hoặc scope growth không cần cho acceptance criteria.

## Completion Status

Chỉ dùng:

- `READY FOR IMPLEMENTATION`
- `BLOCKED`
- `USER DECISION REQUIRED`

`READY FOR IMPLEMENTATION` chỉ hợp lệ khi required investigation, acceptance criteria, boundaries, risk analysis, decision classification và validation plan đều có evidence đủ. Status này không phải xác nhận feature/capability production đã READY.