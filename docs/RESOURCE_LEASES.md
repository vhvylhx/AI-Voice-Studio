# Resource Leases

ResourceLease la quyen tam thoi de Job dung tai nguyen theo policy.

Lease duoc luu trong `workspace/jobs/resources/resource_leases.json`.

Lease phai duoc release khi job completed, failed, cancelled, interrupted, paused hoac app shutdown.

Lease het han duoc danh dau stale de recovery.

## Lease Lifecycle v2 Monitor

Resource Safety Hardening Phase 3 them Lease Lifecycle v2 o che do monitor-only.

Actual runtime van dung lease legacy hien co. Lease v2 chi:

- doc state lease legacy;
- tinh shadow lifecycle;
- ghi structured observation;
- de xuat action WOULD_ACQUIRE, WOULD_RENEW, WOULD_RELEASE, WOULD_EXPIRE, WOULD_MARK_STALE, WOULD_RECONCILE, WOULD_SKIP hoac WOULD_BLOCK_DUPLICATE;
- phat hien stale, duplicate, orphan, owner/process/policy mismatch.

Observation path khong duoc:

- renew actual lease;
- release actual lease;
- cleanup stale actual lease;
- block queue;
- doi Job state;
- doi scheduling, retry, pause/cancel hoac runtime behavior.

Policy cua lease v2 lay tu `ResourcePolicyService.resolve()` va `ResolvedResourcePolicy`, gom `resource_lease_v2_mode`, max job/GPU job, `lease_ttl_seconds`, `lease_renew_interval_seconds`, `stale_lease_handling_mode` va policy fingerprint.

Corrupt/unavailable lease store duoc report bang shadow observation, khong ghi de file corrupt trong monitor-only.

## Lease Lifecycle v2 Enforcement

Resource Safety Hardening Phase 4 them enforcement path nhung chi kich hoat khi resolved policy co `resource_lease_v2_mode=enforce`.

Activation modes:

- `disabled`: giu legacy behavior.
- `monitor_only`: giu Phase 3 shadow observation, khong v2 mutate/block/reconcile.
- `enforce`: dung acquire/renew/release/reconcile v2.

Enforce path:

- acquire idempotent cho cung job/owner/resource;
- deny duplicate, owner mismatch, concurrency conflict va corrupt/unavailable store bang reason code on dinh;
- expired lease khong duoc tinh la active lease;
- renew chi thanh cong khi lease_id/job_id/owner khop va lease con active;
- release chi thanh cong khi lease_id/job_id/owner khop, idempotent voi lease da released;
- reconcile danh dau expired/stale/duplicate theo huong deterministic, khong xoa unknown data.

Lease store duoc ghi bang atomic temp file + replace voi `schema_version=2`. Enforce path khong ghi de corrupt store.

Phase 4 khong bao gom Process Supervisor, kill-tree, Runtime Guard action hay Thread Budget enforcement.

## Process Supervisor Foundation

Resource Safety Hardening Phase 5 bo sung nen Process Supervisor doc lap voi lease lifecycle.

Lease reconciliation co the truyen identity/process state cho observation, nhung Phase 5 khong thay doi acquire/renew/release lease va khong kill process production.

Process Supervisor co the phat hien:

- process missing trong khi lease con;
- process con khi job missing;
- lease expired/stale trong khi process con;
- owner/identity mismatch;
- PID reuse;
- tree incomplete hoac provider unavailable.

Ket qua chi la shadow observation/proposed reconciliation trong Phase 5.
