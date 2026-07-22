# Validation

Validation phải tương ứng với scope, acceptance criteria và risk đã xác định. Áp dụng thêm [Validation Contract](../shared/validation-contract.md).

Không báo `READY`, success hoặc completion nếu required validation chưa đạt. Không dùng exit code, file tồn tại, cache, fake/mock hoặc test-only làm bằng chứng thay thế cho production behavior/capability.

## Evidence Record

Với từng check, ghi:

- acceptance criterion, contract hoặc risk mà check đánh giá;
- command/check và phạm vi module/caller/flow;
- prerequisite/environment/fixture;
- kết quả thực tế: `PASS`, `FAIL`, `NOT RUN`, `NOT APPLICABLE` hoặc `BLOCKED`;
- claim mà evidence cho phép kết luận;
- limitation, blocker hoặc residual risk.

Nếu check không chạy được, báo chính xác command, lý do, impact và lý do không có alternative evidence tương đương.

## Validation by Slice

Sau mỗi implementation slice:

1. Đọc lại file đã sửa để kiểm tra contract, syntax, UTF-8/Vietnamese text và unintended line-ending churn.
2. Chạy targeted test/check gần nhất với changed behavior.
3. Chạy caller/dependency test nếu contract/caller bị ảnh hưởng.
4. Review diff slice về scope, API/schema/default/error semantics, identity/lineage/data safety và architecture boundary.
5. Nếu fail, giữ evidence, quay lại Investigation, xác định scope/cause/recovery; không suppress failure, đổi assertion để che lỗi hoặc retry mù.

## Validation for Python

Khi phạm vi có Python source/test, chọn theo boundary thực sự bị chạm:

- `py_compile` hoặc `python -m compileall` cho module/package bị tác động;
- direct module tests;
- caller tests;
- integration test khi thay đổi vượt nhiều layer hoặc persistence/queue/engine contract;
- UI/API/bootstrap/runtime/resource smoke nếu scope chạm boundary đó và môi trường cho phép;
- behavior/capability validation theo contract, không chỉ process exit code.

Không sửa test assertion chỉ để pass khi source sai, trừ khi user đã phê duyệt contract change.

## Domain Safety Checks

Khi áp dụng:

- Job/resource: immutable IDs/snapshot, preflight, lease/release, dependency, timeout, pause/cancel/retry/resume và blocker evidence.
- Generate/train/runtime/output: language/runtime/asset gates, independent readiness, Artifact lineage/validation, không fake output.
- Persistence/identity: immutable IDs, ownership, collision/no-overwrite policy, frozen snapshot/lineage và state-machine transition.
- UI/API: layer boundary, responsive lifecycle/correlation, public schema/compatibility, security exposure và actionable Vietnamese errors.
- Data: tests dùng temp/fixture riêng; source/user/production data không bị sửa, xóa, move, rename hoặc overwrite.

## Repository and Encoding Checks

Trước completion:

- Chạy `git diff --check`.
- Đọc `git diff` để review contents, safety, ownership và scope.
- Chạy `git status --short` để phân biệt changes của task với pre-existing worktree changes.
- Xác minh strict UTF-8 cho file sửa/tạo và không thay Git config, line ending hoặc dữ liệu tồn tại để làm validation pass.

## Final Validation Outcome

Report tất cả checks theo Evidence Record. Required `FAIL`, `BLOCKED` hoặc `NOT RUN` phải ảnh hưởng final status đúng theo Rules; không diễn giải thành pass hoặc production readiness.