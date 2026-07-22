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

Thread Budget Phase 8 them integration contract cho production-safe enforcement:

- `monitor_only` van la default va chi sinh observation/plan/audit, khong mutate runtime.
- `enforce` chi apply khi JobRunner duoc inject `ThreadBudgetService` va engine co capability/adapter da dang ky.
- Environment enforcement la scoped copy truyen qua `JobExecutionContext`, khong ghi vao `os.environ`.
- Runtime enforcement di qua adapter contract `capture_current_settings`, `validate_thread_budget`, `apply_thread_budget`, `restore_thread_budget`.
- Apply dien ra truoc workload; restore dien ra sau workload trong lifecycle runner va khong che primary workload error.
- Khong co CPU affinity, khong kill process, khong thay queue ordering, retry, pause/cancel hoac final-state semantics mac dinh.

Thread Budget Phase 9 them controlled rollout policy:

- `thread_budget_engine_allowlist`: danh sach engine duoc phep rollout khi mode enforce.
- `thread_budget_engine_denylist`: danh sach engine luon defer, uu tien cao hon allowlist.
- `thread_budget_rollout_percentage`: gate deterministic 0-100 theo `job_id|engine_id`; default 0.
- `thread_budget_require_explicit_engine_opt_in`: default true.
- `thread_budget_fail_open`: default false va gia tri true bi xem la policy invalid.

Production apply chi duoc chay khi `thread_budget_mode=enforce`, engine co capability production-ready, adapter health check dat, engine nam trong allowlist hoac explicit opt-in, rollout selected va capture previous state thanh cong. Unknown/unregistered/unavailable engine deu deferred, khong fail-open.

Source evidence Phase 9:

- `gpt_sovits`: engine_id that trong `GPTSoVITSEngine.info()`, generate chay subprocess qua `GPTSoVITSAdapter.run(..., env=env)`, nen chi dang ky scoped subprocess environment adapter.
- `mock`, `xtts`, `vieneu`: khong production-ready cho Thread Budget production enforcement.
