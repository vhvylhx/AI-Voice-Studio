---
name: feature-development
description: Implement a new approved feature while preserving existing architecture, behavior, compatibility, data safety, resource limits, and truthful production capability status.
---

# Feature Development

Dùng cho feature đã được người dùng phê duyệt. Không dùng để tự suy ra feature từ TODO, refactor cơ hội hoặc nâng capability production chỉ vì test/mock có thể chạy.

Áp dụng [`safe-project-implementation`](../safe-project-implementation/SKILL.md) và Shared Framework:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

## Entry Requirements

Trước Implementation phải có:

- user intent và scope được xác định;
- current source/caller/dependency/tests đã được đọc;
- existing convention/extension point đã được xác minh;
- acceptance criteria observable;
- allowed/excluded paths;
- compatibility, identity, data, resource, security và readiness impact;
- validation strategy theo slice.

Nếu feature thay đổi default behavior, workflow, naming, schema/API, Dataset/Training/Generate semantics, resource policy, local API exposure hoặc production readiness, phải mở [Decision Gate](../shared/decision-gates.md) trước edit.

## Development Workflow

```text
1. Investigate current behavior and extension points
   ↓
2. Define feature contract, non-goals and acceptance criteria
   ↓
3. Inspect callers, dependencies, persistence and related tests
   ↓
4. Classify compatibility/safety/readiness impact and pass gates
   ↓
5. Plan vertical slices with ownership and validation
   ↓
6. Implement smallest compatible slice
   ↓
7. Run targeted validation and diff review
   ↓
8. Repeat slice only while scope remains approved
   ↓
9. Run final compatibility/safety validation and report
```

## Design Constraints

- Reuse existing Service, repository, queue, state machine, event and UI patterns; không tự tạo đường đi song song.
- Giữ luồng `UI → Page/Controller → Service → Job Queue → Engine Manager → Engine Adapter → Runtime`.
- UI không quản lý workflow/persistence/runtime; Worker không đọc UI/open Project.
- Dùng immutable IDs và persisted snapshots; không dùng display name/path/UI index làm identity.
- Preserve backward compatibility trừ khi approval/policy nêu rõ thay đổi.
- Không thêm dependency nếu standard library/dependency hiện có đáp ứng.
- Không create fake artifact/audio/model/checkpoint hoặc `READY` claim để hoàn tất feature.
- Không silent overwrite output/persistence/user data.

## Required Analysis per Slice

Mỗi slice phải trả lời:

1. User-observable outcome là gì?
2. Existing contract/extension point nào được dùng?
3. File nào được đọc, file nào được phép sửa, caller nào bị ảnh hưởng?
4. Failure/cancel/retry/no-data path có thay đổi không?
5. Data/resource/security/readiness gate nào liên quan?
6. Test/smoke nào chứng minh slice?
7. Slice có làm thay semantic frozen state, identity hoặc persisted data không?

Nếu câu trả lời mới tạo product/architecture decision, dừng ở gate.

## Validation

Áp dụng [Validation Contract](../shared/validation-contract.md):

- targeted tests cho từng slice;
- caller/compatibility check khi interface/model/schema thay đổi;
- UI/API/resource/runtime smoke theo boundary đã chạm;
- compile check cho Python source khi khả thi;
- `git diff --check` và `git status --short` read-only;
- full suite chỉ khi scope/risk yêu cầu hoặc project policy bắt buộc.

Nêu rõ evidence layer; fake/mock only xác minh test contract, không xác minh production capability.

## Required Report

```text
## FEATURE SCOPE AND NON-GOALS
## CURRENT STATE AND EXTENSION POINTS
## ACCEPTANCE CRITERIA
## DESIGN AND DECISION GATES
## IMPLEMENTED SLICES
## COMPATIBILITY AND SAFETY
## VALIDATION
## NOT IMPLEMENTED / LIMITATIONS
## FILES CHANGED
## FINAL STATUS
```

Final Status dùng exact vocabulary của `AGENTS.md`.