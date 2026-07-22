---
name: release-check
description: Perform a final release-readiness audit against project rules, architecture, decisions, tests, data safety, resource safety, security, and Definition of Done.
---

# Release Check

Mặc định là audit **read-only** trước release, milestone hoặc handoff. Không sửa source/test/docs, không tự commit/push và không chạy workload có side effect chỉ để làm một gate pass.

Áp dụng [`safe-project-implementation`](../safe-project-implementation/SKILL.md), [`code-review`](../code-review/SKILL.md) và Shared Framework:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

`RELEASE_READY` chỉ là verdict cho audit scope; không tự nâng production capability độc lập lên `READY`.

## Required Evidence

Đọc theo source-of-truth order của dự án, sau đó đọc:

- task/release acceptance criteria và Definition of Done;
- changed files, callers, dependencies và relevant tests;
- Git status/diff read-only, tách current-scope change khỏi dirty worktree pre-existing;
- test configuration, executed validation logs/results và skipped/xfail rationale;
- architecture/decisions/current status/sprint/roadmap/changelog khi thuộc scope;
- resource/runtime/capability evidence khi scope chạm execution, Generate, Preview, output hoặc training.

Không dùng intended work, test fake/mock, file tồn tại, executable discovery hoặc command exit code như bằng chứng release/production capability rộng hơn thực tế.

## Audit Workflow

```text
1. Establish release scope, acceptance criteria and pre-existing worktree boundary
   ↓
2. Inventory evidence and identify unverified required gates
   ↓
3. Audit implementation and diff in contract/failure/safety layers
   ↓
4. Audit validation quality, compatibility and capability truthfulness
   ↓
5. Classify every gate: PASS / FAIL / NOT EXECUTED / BLOCKED / NOT APPLICABLE
   ↓
6. Determine verdict from mandatory-gate evidence
   ↓
7. Report exact evidence, limitations, blockers and residual risks
```

## Release Gates

### Scope and Diff Gate

- No accidental/generated/secret/user-data files in release scope.
- No out-of-task behavior or architecture rewrite without approval.
- Pre-existing dirty files are identified, not attributed to current task.
- No encoding corruption or broad line-ending churn outside scope.
- `git diff --check` and `git status --short` read-only evidence are recorded.

### Build and Test Gate

- Python compile/import/build checks appropriate to scope have passed, or limitation is explicit.
- Targeted regression tests pass for changed contracts.
- Integration/UI/API/bootstrap/runtime smoke runs where affected boundary requires it.
- Full suite is run when required by scope/risk/policy; otherwise rationale is explicit.
- Failures, skips and xfails have evidence; no assertion change merely hides a regression.

### Contract, Architecture and Compatibility Gate

- Acceptance criteria are demonstrably met.
- Existing public behavior, default, schema, persistence and callers remain compatible unless approved otherwise.
- UI/API/Service/Queue/Engine/Runtime dependency flow is preserved.
- Immutable identity, frozen snapshots, state transitions, recovery and lineage contracts remain intact.
- No unapproved product/architecture/security/resource decision is embedded in the diff.

### Data, Artifact and Operational Safety Gate

- No source data modification, silent overwrite, unsafe delete/move/rename or production test fixture use.
- Temporary/intermediate data stays in managed workspace/cache according to contract.
- Job/resource/process lifecycle covers preflight, acquire/release, failure, cancel, timeout and evidence retention.
- Output/Artifact success is not claimed without required validation and lineage.
- Concurrency/resource settings remain within policy and available evidence.

### Runtime, Readiness and Security Gate

- Runtime/language/asset/resource gates are evaluated per capability.
- Generate, Preview Audio, WAV, MP3, preprocess and training are not inferred from a shared boolean, fake provider, cache, or executable.
- No fake artifact/checkpoint/audio/model/READY claim is added.
- API/network/auth/origin/rate-limit/path/subprocess boundaries comply with policy.
- No secrets, credentials, sensitive user content or prohibited paths leak through diff/log/report.

### Documentation and Evidence Gate

- Required documentation/Memory Bank/status/sprint/changelog updates match verified source only when task policy requires them.
- Documentation does not overclaim readiness or validation.
- Commands, results, environment limitations and remaining gaps are reportable and traceable.

## Verdict Rules

Use only:

- `RELEASE_READY`
- `RELEASE_READY_WITH_NOTES`
- `NOT_RELEASE_READY`
- `BLOCKED`

Rules:

- `RELEASE_READY`: all mandatory applicable gates pass with sufficient evidence; only non-blocking notes remain.
- `RELEASE_READY_WITH_NOTES`: mandatory gates pass, but clearly bounded non-blocking limitations/pre-existing issues remain.
- `NOT_RELEASE_READY`: a mandatory gate fails or required evidence shows a release-impacting defect.
- `BLOCKED`: a mandatory gate cannot be assessed safely due to missing evidence/environment/approval.

A `NOT EXECUTED` mandatory check prevents `RELEASE_READY` unless project policy explicitly establishes a valid alternative evidence path.

## Required Report

```text
## AUDIT SCOPE
## ACCEPTANCE CRITERIA AND EVIDENCE
## GATE MATRIX
| Gate | Status | Evidence | Limitation / Required Action |
## PASSED GATES
## FAILED GATES
## NOT EXECUTED
## BLOCKERS
## PRE-EXISTING ISSUES
## RISKS
## FINAL VERDICT
```

Use `VERIFIED`, `INFERRED`, `UNVERIFIED`, `BLOCKED` and `PRE-EXISTING` according to the Reporting Contract. Do not claim a clean worktree, full test pass, or production readiness without direct evidence.