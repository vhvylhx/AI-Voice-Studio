# Safe Project Implementation Checklists

Dùng checklist theo phase; không đánh dấu hoàn tất khi không có evidence tương ứng. `Không áp dụng` phải ghi lý do trong context/report thay vì bỏ qua im lặng.

## Before Any Edit

- [ ] Đã chọn operating mode phù hợp và xác định requested scope, non-goals, allowed/excluded paths.
- [ ] Đã kiểm tra `git status --short` read-only; các thay đổi tồn tại trước được phân biệt với task hiện tại.
- [ ] Đã đọc Rules, project truth, Architecture/Decisions và Memory Bank theo thứ tự áp dụng.
- [ ] Đã đọc toàn bộ source/configuration trực tiếp liên quan.
- [ ] Đã đọc callers, entry points, dependencies, extension points và tests/fixtures liên quan.
- [ ] Current behavior, contract/default/error semantics và acceptance criteria có evidence.
- [ ] Affected identity, ownership, persistence, frozen snapshot/lineage/state machine đã được đánh giá khi áp dụng.
- [ ] Affected data, artifact/output, resource/job, runtime/readiness, security và UI responsiveness đã được đánh giá khi áp dụng.
- [ ] Files to modify/not modify và smallest safe change đã xác định.
- [ ] Mỗi acceptance criterion có planned validation; fake/mock/test-only được phân biệt với production evidence.

## Decision Gate

- [ ] Các decision đã có được liên kết source approval.
- [ ] Không có decision mới chưa được phê duyệt về product semantics, architecture, API/schema/default compatibility, data operation, resource/security policy, engine/runtime route hoặc capability/readiness.
- [ ] Nếu có decision mới, đã dừng trước edit, nêu options/trade-offs và chờ user approval.
- [ ] User request không bị suy diễn thành approval cho side effect hoặc scope ngoài yêu cầu.

## Per Implementation Slice

- [ ] Slice có mục tiêu nhỏ, owner files và extension point rõ ràng.
- [ ] Diff chỉ chứa thay đổi cần thiết cho criterion của slice; không refactor/rename/format/dependency addition ngoài scope.
- [ ] Caller, contract, failure behavior và compatibility impact đã được kiểm tra.
- [ ] Không bypass UI → Page/Controller → Service → Job Queue → Engine Manager → Adapter → Runtime.
- [ ] Không sửa trực tiếp persistence để ép state, success, lineage hoặc readiness.
- [ ] Với work dài/nặng: Job immutable IDs/snapshot, ResourceRequirement, preflight/lease, cancel/retry/resume được giữ theo contract.
- [ ] Với data/artifact: không overwrite source/final output, không promote temp/orphan, không tạo fake production artifact.
- [ ] Đã đọc lại file sau edit; UTF-8/Vietnamese text và line-ending scope không bị thay đổi ngoài ý muốn.
- [ ] Targeted validation đã chạy hoặc được phân loại chính xác `FAIL` / `NOT RUN` / `NOT APPLICABLE`.
- [ ] Nếu validation fail: evidence, suspected scope, recovery path và residual risk đã được ghi; không suppress hoặc retry mù.

## Final Completion

- [ ] Tất cả acceptance criteria đã có evidence xác minh hoặc được nêu rõ là blocker/limitation.
- [ ] Targeted tests, compile/import và relevant integration/UI/API/bootstrap/runtime/resource smoke đã chạy theo scope hoặc được báo chính xác chưa chạy.
- [ ] `git diff --check` đã chạy.
- [ ] `git diff` đã được review về correctness, safety, scope, encoding và unexpected changes.
- [ ] `git status --short` đã được kiểm tra; task files và pre-existing changes được phân biệt.
- [ ] Capability table phân biệt production, foundation, test-only, unavailable/blocked; không overclaim từ fake/mock.
- [ ] Completion report đủ `KEEP`, `NEW`, `REPLACE`, `DELETE`, `TESTED`, `NOT TESTED`, `PRE-EXISTING ISSUES`, `RISKS`, `FILES CHANGED`, `FINAL STATUS`.
- [ ] Final status dùng đúng một giá trị được `AGENTS.md` cho phép.