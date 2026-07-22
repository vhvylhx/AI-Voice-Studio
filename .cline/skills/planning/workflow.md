# Planning Workflow

Planning là hoạt động read-only để tạo plan có evidence; không sửa source/test/docs/Memory Bank hoặc tạo artifact.

## 1. Establish Task Boundary

Xác định user intent, requested outcome, scope, non-goals, allowed/excluded paths và acceptance criteria còn thiếu. Không tự mở rộng yêu cầu từ TODO hoặc cơ hội refactor.

↓

## 2. Read Source of Truth

Đọc theo thứ tự bắt buộc của project:

1. `AGENTS.md` và `.clinerules/` áp dụng.
2. Roadmap/status/current sprint/architecture/decisions/changelog theo Rules.
3. Memory Bank.
4. Source/configuration trực tiếp liên quan.
5. Caller, dependency và tests liên quan.

Ghi evidence source và phân biệt fact hiện tại với historical context/intended work.

↓

## 3. Map Current Contract

Xác định current behavior, public/internal contract, default/error semantics, ownership, layer boundary, persistence/state machine và extension point.

Khi áp dụng, map:

- UI → Page/Controller → Service → Queue → Engine Manager → Adapter → Runtime;
- immutable ID, frozen snapshot, Job/Unit/Attempt/Artifact lineage;
- resource preflight/lease/cancel/retry/resume;
- capability/readiness, runtime/language/asset/security boundaries.

↓

## 4. Inspect Callers, Dependencies and Tests

Đọc caller chain thực tế, entry points, imports, model/schema/serialization/persistence, configuration, repository/service/worker/adapter/runtime dependencies và targeted tests/fixtures.

Không suy luận production readiness từ fake/mock/test-only composition. Ghi rõ caller/dependency không chịu ảnh hưởng nếu evidence xác nhận.

↓

## 5. Define Verified Outcome

Chuyển intent thành:

- desired user-observable outcome;
- acceptance criteria có thể kiểm chứng;
- preserved invariants;
- explicit non-goals;
- expected failure/blocker/cancel/retry behavior nếu scope liên quan.

Mỗi acceptance criterion phải có planned validation hoặc được đánh dấu `UNVERIFIED`/`BLOCKED`.

↓

## 6. Classify Risk and Decision Gates

Đánh giá compatibility, data, identity, security, resource, runtime/readiness, persistence/lineage, UI responsiveness và regression risk.

Nếu phát hiện quyết định **mới chưa được phê duyệt**, sử dụng [`../shared/decision-gates.md`](../shared/decision-gates.md) và dừng trước khi lập chi tiết dựa trên quyết định đó.

Nếu decision đã được phê duyệt, ghi source approval/decision và constraints; không re-open gate.

↓

## 7. Design Dependency-Safe Slices

Lập slices nhỏ nhất đáp ứng criteria theo thứ tự dependency-safe. Mỗi slice nêu:

- file/module dự kiến;
- existing extension point/caller affected;
- change intent;
- invariant/contract phải giữ;
- data/resource/security/readiness impact;
- test/smoke/diff evidence;
- rollback/recovery consideration nếu relevant.

Không thêm refactor, rename, schema/API/default behavior hoặc dependency ngoài scope đã phê duyệt.

↓

## 8. Define Validation Strategy

Theo [`../shared/validation-contract.md`](../shared/validation-contract.md), chọn targeted tests trước, sau đó compile/import, UI/API/bootstrap/runtime/resource smoke và final diff/status checks khi boundary bị chạm.

Ghi rõ:

- command/check dự kiến;
- claim mà check có thể chứng minh;
- environment/prerequisite;
- fallback evidence nếu không thể chạy;
- limitation còn lại.

↓

## 9. Publish Plan

Dùng [`report.md`](report.md) và [`checklist.md`](checklist.md). Kết thúc bằng đúng một status:

- `READY FOR IMPLEMENTATION`
- `BLOCKED`
- `USER DECISION REQUIRED`

`READY FOR IMPLEMENTATION` chỉ thể hiện plan đủ evidence để triển khai, không chứng minh production capability đã sẵn sàng.