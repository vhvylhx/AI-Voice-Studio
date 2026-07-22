# Resource Policy

ResourcePolicy tap trung cac nguong:

- max_concurrent_jobs;
- max_gpu_jobs;
- reserve_ram_mb;
- reserve_vram_mb;
- reserve_disk_mb;
- snapshot_ttl_seconds;
- lease_ttl_seconds;
- lease_renew_interval_seconds;
- stale_lease_handling_mode;
- pressure warning thresholds.

Auto pause khi pressure critical mac dinh tat cho den khi co quyet dinh rieng.

`resource_lease_v2_mode` mac dinh la `monitor_only`.

Lease Lifecycle v2 modes:

- `disabled`: legacy behavior.
- `monitor_only`: Phase 3 shadow observation, khong v2 mutate/block/reconcile.
- `enforce`: Phase 4 Lease Lifecycle v2 enforcement.

Literal `enforced` cu duoc ho tro nhu legacy alias, nhung policy Phase 4 dung `enforce` lam mode chinh. Fallback policy phai disable enforcement modes khi primary policy loi.
