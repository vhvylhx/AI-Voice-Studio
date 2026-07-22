---
name: code-review
description: Review repository changes deeply for correctness, regression, architecture, data and resource safety, security, encoding, compatibility, capability truthfulness, tests and scope violations. Default to read-only and require evidence for every finding.
---

# Code Review

Mặc định chỉ review read-only. Không sửa file trừ khi người dùng yêu cầu rõ “review và sửa”; khi đó phải chuyển sang `safe-project-implementation` trước bất kỳ edit nào.

Skill này áp dụng đầy đủ [`safe-project-implementation`](../safe-project-implementation/SKILL.md) và Shared Framework:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

Không tự commit, push, reset, restore, clean, checkout, stash, merge, rebase hoặc thay đổi Git history.

## Review Modes

| Mode | Khi dùng | Output |
| --- | --- | --- |
| Diff review | Có task diff/changed files rõ. | Findings theo hunk, scope và regression risk. |
| Contract review | Thay đổi service/API/model/persistence/state machine. | Compatibility, caller, identity và migration analysis. |
| Safety review | Chạm data, output, process, resource, runtime, API security. | Safety gate và operational failure paths. |
| Release review | Chuẩn bị kết thúc task/sprint/release. | Validation evidence, readiness truthfulness và final verdict. |
| Investigative review | Có symptom/failure nhưng diff hoặc cause chưa rõ. | Evidence, hypotheses được gắn nhãn, gaps và next safe checks. |

Không chuyển từ review sang code chỉ để xử lý finding; tách report và implementation để giữ độc lập.

## Review Workflow

```text
1. Establish scope, acceptance criteria and dirty-worktree boundaries
   ↓
2. Read Rules, Memory Bank, architecture/decisions and task evidence
   ↓
3. Inspect changed source, callers, dependencies and relevant tests
   ↓
4. Review in layers: contract → behavior → failure paths → safety → validation
   ↓
5. Verify diff hygiene, compatibility and capability/readiness claims
   ↓
6. Classify findings with evidence, severity and required validation
   ↓
7. Report limitations, pre-existing issues, gaps and verdict
```

### 1. Scope Integrity

- Ưu tiên task specification, acceptance criteria, limited Git diff và changed file list.
- Kiểm tra `git status --short` và diff theo scope read-only.
- Không kết luận toàn bộ dirty worktree là do task hiện tại.
- Không expand review thành architecture rewrite; chỉ nêu out-of-scope risk nếu evidence cho thấy impact thật.
- Nếu review scope không xác định, báo `BLOCKED` thay vì đánh giá toàn repository bằng suy đoán.

### 2. Evidence Discipline

- Đọc source đã đổi cùng toàn bộ caller/dependency/test cần thiết để hiểu contract.
- Mỗi finding theo mẫu tại [Reporting Contract](../shared/reporting.md#3-review-finding-template), gắn rõ changed location/caller path, violated contract, observable impact, evidence hoặc reproduction và required validation/fix direction.
- Dùng `VERIFIED`, `INFERRED`, `UNVERIFIED`, `BLOCKED`, `PRE-EXISTING` khi cần; không nâng `INFERRED` thành finding blocking nếu chưa có direct evidence.
- Phân biệt lỗi do diff hiện tại, pre-existing issue và validation gap; không gán thay đổi ngoài review scope cho author/task.
- Không tạo finding từ naming/style preference nếu không có impact.
- Không gọi test pass là production readiness; không gọi file/exit code/Job success là Artifact/Unit success.

## Layered Review Checklist

### A. Contract, Correctness and Failure Paths

- Expected/actual behavior có giữ acceptance criteria và default hiện có không?
- Public signature, return/error semantic, caller expectation và serialized shape có tương thích không?
- Validation có xảy ra trước side effect không?
- Exception, timeout, cancel, pause, retry, resume, partial failure và cleanup path có đúng contract không?
- State transition có đi qua state machine/service, giữ blocker/recovery context và không mark success sớm không?
- Race, stale callback, idempotency, duplicate request và correlation/immutable ID có được xử lý khi phù hợp không?

### B. Architecture and Dependency Direction

- UI có gọi Engine/Adapter/Runtime/Repository/Worker trực tiếp không?
- Widget có business logic, persistence, blocking I/O hoặc resource scheduling không?
- API có gọi Service thay vì lower layer trực tiếp không?
- Worker có chỉ dùng persisted payload/snapshot hay đọc UI/open Project/selection không?
- Queue, Engine Manager, Adapter và Runtime có giữ đúng ownership không?
- Có duplicate domain logic hoặc bypass validation/persistence transaction không?

### C. Identity, Persistence and Compatibility

- Có dùng immutable ID thay vì display name, filename hoặc path khi contract đã có ID không?
- Rename có giữ ID, model path, frozen lineage và links không?
- Persisted data có collision/no-overwrite/atomic policy hợp lệ không?
- API/schema/file format/default behavior có breaking change, caller gap hoặc migration/rollback gap không?
- Có direct JSON/manifest mutation để repair/force state không?
- Fake/mock/test composition có leak vào production AppContext không?

### D. Generate, Artifact and Runtime Truthfulness

- Request/Session/Plan/Unit/Attempt/Artifact có còn tách biệt không?
- Frozen Plan, Unit ID, selection, language route và settings có bị retry/resume thay semantic không?
- Unit chỉ success khi Artifact validation + lineage hợp lệ không?
- Temp có nằm workspace/cache, final output có no-overwrite không?
- Capability Generate, Preview, WAV, MP3, preprocess, train có được đánh giá độc lập không?
- Runtime/language/asset/resource blocker có bị che bằng fallback giả, fake output hoặc READY claim không?
- `vi` có bị map giả sang token GPT-SoVITS khác không?

### E. Dataset, Training and Reference Integrity

- Source TXT/DOCX/audio/dataset có bất biến không; derived data có ở cache/workspace với lineage không?
- Validation threshold, transcript/quality gate, approval state hoặc listening-review requirement có bị hạ/bypass không?
- Training/preprocess có bị chạy khi language/runtime/asset/resource gate block không?
- Reference có resolve từ `reference_id`/snapshot thay vì filename/path/UI selection không?
- Import/export/backup/restore có collision, ownership, evidence và no-overwrite handling không?

### F. Resource, Process and Operational Safety

- Job nặng có `ResourceRequirement`, preflight, lease acquire/release, timeout/cancel và recovery evidence không?
- Có tăng batch/concurrency/GPU/RAM/disk/network/process load mà không policy/guard không?
- Subprocess có bounded lifecycle, safe command/input handling, log redaction và orphan cleanup không?
- Có implicit CPU/GPU/engine fallback, UI-thread blocking hoặc GPU workload stacking không?
- Error state có giữ forensic evidence thay vì tự delete/rewrite temp/artifact không?

### G. Security and API Boundaries

- Path/input/subprocess/network input có validation/ownership/allowlist phù hợp không?
- Local API auth/bind/CORS/rate-limit/origin policy có bị nới lỏng không?
- Secret/token/password/source-sensitive data có bị log, response hoặc diff leak không?
- API response có giữ correct identity/stage/recovery context nhưng không lộ path/secret vượt policy không?
- Tests có sử dụng temporary directory/fixture thay vì production user data không?

### H. UI, Encoding and Accessibility

- UI text/help/error có tiếng Việt, actionable và phản ánh blocker thật không?
- UI có hiển thị queued/running/paused/blocked/cancelled/failed/completed rõ và không stale state không?
- Callback worker có kiểm correlation/lifecycle token và không update Widget từ worker thread không?
- UTF-8/tiếng Việt có nguyên vẹn; có line-ending churn hoặc encoding corruption ngoài scope không?
- Layout/responsive/scroll/action availability có regression rõ khi UI thay đổi không?

### I. Tests and Validation Evidence

- Test mới/sửa có kiểm đúng contract hay chỉ làm assertion pass?
- Bugfix có regression test hợp lý không?
- Test fake/mock có giới hạn test composition và không nâng readiness production không?
- Targeted test, integration/smoke, compile và diff check có tương xứng risk/scope không?
- Có validation gap về failure path, compatibility, persistence/data safety, resource cleanup hoặc UI async không?

## Severity and Verdict

Dùng severity tại [Reporting Contract](../shared/reporting.md#4-severity-guide).

Một finding CRITICAL/HIGH phải có direct evidence về contract violation hoặc failure path, affected caller/input/state và impact thực tế có thể xảy ra; nếu evidence chưa đủ, ghi `UNVERIFIED`/validation gap thay vì overstate.

Finding phải nêu validation cần có để xác nhận hoặc phủ định kết luận. Không yêu cầu sửa speculative concern chỉ vì reviewer không có đủ context.

`FINAL VERDICT` chỉ dùng:

- `APPROVE`
- `APPROVE_WITH_NOTES`
- `REQUEST_CHANGES`
- `BLOCKED`

`APPROVE` không có nghĩa production capability `READY`; nó chỉ nghĩa review scope không có finding cần chặn theo evidence đã kiểm tra.

## Required Report

```text
## REVIEW SCOPE
## EVIDENCE REVIEWED
## FINDINGS
## VALIDATION GAPS
## PRE-EXISTING ISSUES
## LIMITATIONS
## FINAL VERDICT
```

Khi không có findings, ghi rõ “No verified findings in reviewed scope”, checks đã chạy/chưa chạy và limitations. Không tuyên bố toàn repository hay production runtime đúng chỉ từ review diff.