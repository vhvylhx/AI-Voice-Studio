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
