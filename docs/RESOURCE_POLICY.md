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

Process Supervisor Phase 5 dung `process_supervisor_mode`, mac dinh `monitor_only`.

Policy additive cho Process Supervisor:

- graceful_shutdown_timeout_seconds;
- terminate_timeout_seconds;
- kill_tree_timeout_seconds;
- process_identity_required;
- orphan_handling_mode;
- process_observation_ttl_seconds.

Trong Phase 5, `enforce` chi la contract/gate fail-safe va khong tu kill process production.

Runtime Guard Phase 6 dung `runtime_guard_mode`, mac dinh `monitor_only`.

Policy additive cho Runtime Guard:

- action_cooldown_seconds;
- deescalation_stable_seconds;
- observation_ttl_seconds;
- max_action_attempts;
- action_retry_backoff_seconds;
- allow_simulated_throttle;
- allow_simulated_pause;
- allow_simulated_graceful_stop;
- allow_simulated_terminate;
- allow_simulated_kill_tree.

Runtime Guard modes:

- `disabled`: sinh skip/deferred, khong action.
- `monitor_only`: sinh structured observation va WOULD_* recommendation, khong execute.
- `enforce`: Phase 6 chi goi simulated executor an toan; destructive terminate/kill-tree van deferred.

Trong Phase 6, Runtime Guard khong pause, terminate, kill-tree, doi Job state, doi scheduling, doi thread/batch hoac goi GPT-SoVITS runtime production.
