# AI Voice Studio - Project Status

Ngay cap nhat: 2026-07-22

## Trang thai hien tai

- Sprint vua thuc hien: Resource Safety Hardening Phase 4 - Lease Lifecycle v2 Enforcement gated.
- Nen Generate Pipeline AVS-014.16 da co o muc request/session/source snapshot/plan/manifest/recovery/API/job prepare.
- Resource Policy schema v2 da co foundation resolve/migration/fallback/fingerprint o muc monitor-only/disabled.
- Resource Safety Phase 2 da co snapshot validation/freshness va shadow Resource Decision v2 monitor-only, khong doi scheduling/runtime behavior.
- Resource Safety Phase 3 da co Lease Lifecycle v2 shadow observation monitor-only, khong doi actual lease/scheduling/runtime behavior.
- Resource Safety Phase 4 da co Lease Lifecycle v2 enforcement path chi kich hoat khi `resource_lease_v2_mode=enforce`; mac dinh van monitor_only.
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
| Style Profile / Voice DNA foundation | DEGRADED | Quan ly/import/export foundation co; prosody analyzer that chua co. |
| Runtime GPT-SoVITS integration cho Generate | UNAVAILABLE | La pham vi sprint sau, khong lam trong AVS-014.16A. |

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
- Chua co Process Supervisor enforcement/kill-tree, runtime pressure guard action, thread budget enforcement hoac per-job CPU fallback confirmation workflow.
- Resource Decision v2 hien chi shadow/monitor-only; chua duoc dung de block Queue, doi job state, cap/release lease, doi CPU fallback, thread, batch hoac runtime guard.
- Resource Lease v2 enforcement chi chay khi `resource_lease_v2_mode=enforce`; mac dinh monitor_only van giu legacy/Phase 3 behavior.
- Chua co Process Supervisor/kill-tree, Runtime Guard action, Thread Budget enforcement hay process identity provider production day du.

## Sprint tiep theo du kien

- AVS-014.17 GPT-SoVITS Runtime Integration chi bat dau sau khi source/docs/tests hien tai dat va Resource Safety Hardening Phase 4 neu co duoc phe duyet rieng.
