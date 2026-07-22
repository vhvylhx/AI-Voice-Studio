# Validation Contract

Validation phải chứng minh acceptance criteria và giới hạn thực tế của thay đổi. Không dùng một command pass để suy diễn mọi capability đã sẵn sàng.

## 1. Evidence Ladder

| Mức evidence | Chứng minh được | Không chứng minh được |
| --- | --- | --- |
| Static inspection | Code/diff khớp contract đã đọc; import/caller được kiểm tra. | Runtime behavior, integration, performance hoặc production readiness. |
| Compile/lint | Syntax, import/bề mặt tĩnh trong phạm vi tool. | Logic, state transition, resource cleanup hoặc runtime asset. |
| Targeted test | Contract cụ thể có coverage và result pass trong composition test. | Production runtime/readiness nếu dùng fake/mock. |
| Integration/smoke | Boundary thực được gọi trong environment đã nêu. | Mọi engine/capability khác hoặc quality không được đo. |
| Production real smoke | Capability được smoke theo policy production với assets/runtime/gate hợp lệ. | Capability độc lập khác, quality rộng hoặc workload scale. |
| Manual review | UX/listening/operational quality đã được con người kiểm tra. | Tính đúng toàn bộ pipeline nếu không có test/evidence bổ sung. |

Mọi kết luận phải nêu loại evidence và điều nó không chứng minh.

## 2. Validation Strategy

Trước implementation, xác định cho mỗi acceptance criterion:

- criterion và observable outcome;
- affected contract/caller;
- validation layer phù hợp;
- command/test/smoke cụ thể;
- required fixtures/environment;
- data/resource safety boundary;
- expected result;
- limitation còn lại.

Sau implementation, ghi chính xác command đã chạy, exit/result, phạm vi và failure nếu có. Không ghi “pass” khi chưa chạy.

## 3. Mandatory Checks by Scope

| Phạm vi | Kiểm tra tối thiểu ngoài targeted tests |
| --- | --- |
| Python source | `python -m compileall src tests` khi khả thi. |
| UI/PySide6 | Targeted UI test hoặc UI smoke; nêu rõ nếu không thể chạy. |
| Local API | Targeted API test/smoke, không mở network exposure ngoài policy. |
| Persistence/import/export | Test temporary directory/fixture, collision/rollback/identity path. |
| Job/worker/resource | State transition, cancel/pause/failure, lease release và blocker evidence. |
| Engine/runtime/generate/train | Runtime/language/asset/resource gates; không fake production output. |
| Cross-cutting/multi-file | Targeted tests từng slice, relevant integration, sau đó full `pytest` nếu scope/risk yêu cầu. |
| Documentation/Skill | Markdown/front matter/reference integrity, UTF-8, link target và duplicate/conflict check. |

Luôn chạy `git diff --check` và `git status --short` read-only trước completion khi task có thay đổi repository.

## 4. Regression Prevention

- Với bugfix, thêm regression test nếu contract có test seam hợp lý và không làm test giả production behavior.
- Với public/serialized contract, kiểm tra caller, existing fixture và backward compatibility.
- Với state machine, kiểm tra successful, blocked, failed/cancelled và retry/resume path theo contract.
- Với data/output, kiểm tra no-overwrite, ownership, temporary workspace và lineage.
- Với resource/process, kiểm tra acquire/release trong success, exception, cancel và timeout path.
- Với UI async, kiểm tra stale callback/correlation, UI-thread boundary và lifecycle state.
- Với API/security, kiểm tra input validation, ID ownership, redaction và response semantic.

## 5. Compatibility Checklist

Đánh giá khi scope chạm contract:

- Existing public function/class/endpoint/schema có thay semantic không?
- Caller có truyền/đọc immutable IDs đúng contract không?
- Default behavior có giữ nguyên nếu chưa được phê duyệt đổi?
- Persisted data cũ có đọc được hoặc có migration policy rõ không?
- Rename có giữ identity, path và frozen lineage không?
- Fake/test composition có bị leak sang production composition không?
- Capability status có phản ánh gate độc lập và evidence thật không?

## 6. Validation Failure Protocol

Khi validation fail:

1. Lưu command/result và phạm vi.
2. So sánh failure với baseline nếu worktree đã dirty hoặc test có thể fail sẵn.
3. Điều tra nguyên nhân trước sửa.
4. Chỉ thay đổi source/test khi contract chứng minh cần thiết.
5. Chạy lại targeted validation sau khi sửa.
6. Nếu còn fail, report `NOT_READY`/`BLOCKED` theo Skill contract; không tuyên bố completed.