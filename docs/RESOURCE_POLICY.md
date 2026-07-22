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

Thread Budget Phase 7 dung `thread_budget_mode`, mac dinh `monitor_only`.

Policy additive cho Thread Budget:

- max_total_cpu_threads;
- max_threads_per_light_job;
- max_threads_per_cpu_heavy_job;
- max_threads_per_gpu_inference_job;
- max_threads_per_gpu_training_job;
- max_threads_per_io_heavy_job;
- max_parallel_heavy_jobs;
- reserve_cpu_threads;
- allow_nested_parallelism;
- thread_budget_cooldown_seconds;
- thread_budget_observation_ttl_seconds;
- thread_budget_restore_on_release.

Thread Budget modes:

- `disabled`: giu legacy behavior, khong production action.
- `monitor_only`: tinh structured observation va WOULD_* plan, khong mutate.
- `enforce`: Phase 7 chi goi simulated executor an toan; production executor van UNAVAILABLE neu chua co integration boundary.

Trong Phase 7, Thread Budget khong mutate `os.environ`, khong goi runtime library setter production, khong doi CPU affinity, khong doi JobQueue/JobRunner va khong bat Generate/Training production.
