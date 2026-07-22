# AI Voice Studio - Project Status

Ngay cap nhat: 2026-07-22

## Trang thai hien tai

- Sprint vua thuc hien: Resource Safety Hardening Phase 9 - Production Engine Adapter Registration va Controlled Rollout.
- Nen Generate Pipeline AVS-014.16 da co o muc request/session/source snapshot/plan/manifest/recovery/API/job prepare.
- Resource Policy schema v2 da co foundation resolve/migration/fallback/fingerprint o muc monitor-only/disabled.
- Resource Safety Phase 2 da co snapshot validation/freshness va shadow Resource Decision v2 monitor-only, khong doi scheduling/runtime behavior.
- Resource Safety Phase 3 da co Lease Lifecycle v2 shadow observation monitor-only, khong doi actual lease/scheduling/runtime behavior.
- Resource Safety Phase 4 da co Lease Lifecycle v2 enforcement path chi kich hoat khi `resource_lease_v2_mode=enforce`; mac dinh van monitor_only.
- Resource Safety Phase 5 da co Process Supervisor foundation cho identity, registry, tree discovery, shadow shutdown plan va audit; mac dinh monitor_only va khong kill process production.
- Resource Safety Phase 6 da co Runtime Guard action foundation monitor_only/enforce-gated voi pressure classification, action recommendation, cooldown/hysteresis/retry, simulated executor va structured observation; mac dinh monitor_only va khong kill/pause/terminate production.
- Resource Safety Phase 7 da co Thread Budget foundation monitor_only/enforce-gated voi workload allocation, oversubscription/nested parallelism detection, environment/runtime plan, restore plan, cooldown/dedup/retry va simulated executor; khong mutate thread/env/runtime production.
- Resource Safety Phase 8 da co production-safe Thread Budget integration contract voi scoped environment copy, runtime adapter registry, apply-before-workload/restore-after-workload hook trong JobRunner khi duoc inject, rollback audit va primary-error preservation; mac dinh `thread_budget_mode` van monitor_only.
- Resource Safety Phase 9 da dang ky Thread Budget capability theo source evidence: `gpt_sovits` chi production-ready cho scoped subprocess environment, `mock`/`xtts`/`vieneu` khong production-ready; rollout enforce can allowlist/opt-in va deterministic gate.
- Engine routing da duoc sua: ngon ngu `vi` chi route sang `vieneu`; GPT-SoVITS runtime hien tai khong duoc quang ba ho tro `vi` va khong duoc fallback cho tieng Viet.
- Chua tich hop GPT-SoVITS runtime cho Generate production trong phase nay.
- Chua Train GPT-SoVITS that trong phase nay.
- Chua Generate Audio that trong phase nay.

## Capability Table

| Capability | Status | Ghi chu |
|---|---|---|
| App bootstrap | READY | Bootstrap co the kiem tra moi truong va chuyen vao main app khi dependency san sang. |
| Main Window / UI shell | READY | UI desktop PySide6 da co shell va cac page chinh. |
| Project / Workspace foundation | READY | Project ID bat bien, workspace/project manager foundation da co. |
| Voice schema / Voice ID | READY | Voice ID bat bien, rename khong doi ID. |
| Dataset scan/health/repair/review | READY | Chay tren cache/output job, khong sua file goc. |
| Alignment quality-first | READY | Faster-Whisper/timestamp pipeline da co contract va metadata valid. |
| Training validation_only | READY | Kiem tra dataset/runtime/model path truoc train; chua train that. |
| Real GPT-SoVITS Train | UNAVAILABLE | Chua chay s1/s2 train production trong sprint nay. |
| Generate planning foundation | READY | Request, snapshot, normalized text, plan, manifest va registry da co. |
| Generate resume/retry inspection | READY | Inspect duoc state; execution production van bi chan. |
| Generate production execution | UNAVAILABLE | Chua co real handler/provider trong production AppContext. |
| WAV/MP3 production output qua Generate foundation | UNAVAILABLE | Foundation khong tao audio gia. |
| Full audio validation policy | DEGRADED | Da co basic WAV validation; ffprobe/codec policy day du thuoc sprint sau. |
| Local API foundation | READY | API localhost stdlib co readiness/catalog/job/generate foundation endpoints. |
| API real Generate | UNAVAILABLE | API khong generate that neu chua co Voice/runtime/model ready va handler production. |
| Job Queue foundation | READY | Persistent job/queue/worker foundation da co. |
| Resource Manager foundation | READY | Hardware snapshot/resource decision/lease foundation da co. |
| Resource Policy v2 foundation | READY | Schema v2, feature modes doc lap, migration v1, safe resolve, backup/fallback va fingerprint deterministic da co. Runtime enforcement moi chua bat. |
| Resource Snapshot validation | READY | Phan biet valid/invalid/unknown/stale cho RAM/GPU/VRAM/Disk, co freshness age va TTL tu policy. |
| Resource Decision v2 shadow observation | READY | Tra structured shadow_observation monitor-only gom actual_decision, shadow_decision, reason_codes, snapshot_status, workload_class va policy_fingerprint. |
| Resource Lease v2 shadow observation | READY | Lease lifecycle v2 monitor-only co structured observation cho acquire/renew/release/expiry/stale/reconciliation/duplicate va stable reason codes; actual legacy lease path khong doi. |
| Resource Lease v2 enforcement gated | READY | Acquire/renew/release/reconcile v2 co atomic persistence, owner/job validation, corrupt-store fail-safe va stable reason codes; chi active khi policy resolved la `enforce`. |
| Resource Policy v2 enforcement | UNAVAILABLE | Van chi monitor-only/shadow; khong block job moi, khong doi scheduling/thread/batch/runtime action. |
| Resource Lease v2 production rollout | DEGRADED | Enforcement path da co sau feature flag, nhung default production van monitor_only va chua co Process Supervisor/Runtime Guard/Thread Budget Phase 5. |
| Process Supervisor foundation | READY | Process identity khong chi dua PID, registry atomic, tree discovery, shadow observation, shutdown plan simulated va stable reason codes. |
| Process Supervisor production kill-tree | UNAVAILABLE | Phase 5 khong goi kill/terminate process that; enforce mode chi la contract/gate fail-safe. |
| Runtime Guard action foundation | READY | Phase 6 co RuntimeGuardObservation, pressure level, WOULD_* action, cooldown/hysteresis/retry va simulated executor dung policy resolved. |
| Runtime Guard production action | UNAVAILABLE | Default monitor_only; enforce chi goi simulated executor an toan, khong pause/terminate/kill-tree process that va khong doi Job state/scheduling. |
| Thread Budget foundation | READY | Phase 7 co ThreadBudgetObservation, workload allocation deterministic, oversubscription/nested detection, environment/runtime/restore plan va simulated executor. |
| Thread Budget production enforcement integration | DEGRADED | Phase 9 co registry/rollout va GPT-SoVITS scoped subprocess environment adapter; default van monitor_only, khong runtime setter/model load/GPU. |
| Style Profile / Voice DNA foundation | DEGRADED | Quan ly/import/export foundation co; prosody analyzer that chua co. |
| Runtime GPT-SoVITS integration cho Generate | UNAVAILABLE | La pham vi sprint sau, khong lam trong AVS-014.16A. |
| VieNeu-TTS Vietnamese routing | UNAVAILABLE | `vieneu` la engine bat buoc cho `vi`, nhung runtime/app integration hien chua san sang; khong fallback sang GPT-SoVITS. |
| GPT-SoVITS Vietnamese support | NOT_APPLICABLE | Runtime GPT-SoVITS hien tai khong co frontend/ngon ngu `vi` hop le. |

## Data safety

- Source khong duoc tu y sua/xoa/di chuyen du lieu that trong `projects/`, `workspace/`, `voices/`, `outputs/`, `backups/`, `exports/` hoac Reference Vault.
- Tests phai dung fixture/cache tam rieng, khong dung du lieu that cua nguoi dung.
- Worktree co the dirty do du lieu/project that; khong restore/clean neu nguoi dung chua xac nhan.

## Blocker / chua trien khai

- Chua co real Generate worker/provider noi GPT-SoVITS production.
- Chua co WAV/MP3 output production trong Generate foundation.
- Chua co full audio validation policy bang ffprobe/codec cho artifact production.
- Chua chay Train GPT-SoVITS production.
- Chua co prosody analyzer that cho Voice DNA.
- Chua co Process Supervisor production kill-tree, runtime guard production action hoac per-job CPU fallback confirmation workflow.
- Resource Decision v2 hien chi shadow/monitor-only; chua duoc dung de block Queue, doi job state, cap/release lease, doi CPU fallback, thread, batch hoac runtime guard.
- Resource Lease v2 enforcement chi chay khi `resource_lease_v2_mode=enforce`; mac dinh monitor_only van giu legacy/Phase 3 behavior.
- Process Supervisor hien chi foundation/monitor-only/simulated; chua co provider production day du, khong kill process that.
- Runtime Guard hien chi foundation/monitor-only/simulated; chua co action executor production, khong pause/terminate/kill-tree process that.
- Thread Budget Phase 9 da co GPT-SoVITS scoped subprocess environment registration, nhung default monitor_only va enforce van can allowlist/opt-in/rollout; khong co CPU affinity/system-wide environment mutation.

## Sprint tiep theo du kien

- Phase 10 neu co moi duoc mo rong sang engine-specific rollout production sau khi Phase 9 duoc review.
