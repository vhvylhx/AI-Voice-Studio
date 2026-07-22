# Changelog

## Resource Safety Hardening Phase 8: Production Thread Enforcement Integration

### Added

- `ThreadBudgetEngineCapability` va `ThreadBudgetApplyState` cho contract apply/restore co audit.
- `ThreadBudgetCapabilityRegistry` de dang ky engine capability va runtime adapter theo `engine_id`.
- `ThreadBudgetRuntimeAdapter` contract va fake adapter deterministic cho tests.
- `ScopedThreadBudgetExecutor` apply scoped environment copy, runtime adapter setting, rollback khi apply fail va restore sau workload.
- Optional JobRunner hook qua `thread_budget_service`, apply truoc worker workload va restore trong lifecycle runner.
- Tests Phase 8 cho monitor_only no-mutation, enforce scoped env/runtime, missing capability fail-safe, rollback, primary error preservation va JobRunner integration.

### Changed

- Production default van `thread_budget_mode=monitor_only`.
- Khong ghi `os.environ`; environment contract la scoped dict trong `JobExecutionContext`.
- Khong CPU affinity, khong kill process, khong doi queue ordering, retry, pause/cancel hoac final state mac dinh.

### Notes

- Phase 8 chua dang ky GPT-SoVITS/VieNeu adapter production va chua rollout enforcement mac dinh.
- Canonical suite Phase 8: 275 passed, tang 7 tests so voi Phase 7 baseline 268.

## Resource Safety Hardening Phase 7: Thread Budget Enforcement Foundation

### Added

- Thread Budget foundation voi `ThreadBudgetObservation`, budget statuses, action states, stable reason codes va policy fingerprint.
- Policy additive cho total CPU threads, per-workload limits, reserve CPU threads, heavy job concurrency, nested parallelism, cooldown, TTL va restore-on-release.
- `ThreadBudgetService` cho workload allocation deterministic, oversubscription detection, nested parallelism detection, environment/runtime/restore plan, cooldown, duplicate suppression, retry exhaustion va lease/process/runtime guard reconciliation boundary.
- `ThreadBudgetExecutor` va `SimulatedThreadBudgetExecutor` deterministic cho foundation/tests.
- Tests Phase 7 cho workload classes, reserve/oversubscription, heavy job limit, unknown/stale/invalid, environment/runtime plan, mode boundary, simulated enforce, restore, cooldown/dedup/retry, integration va stable reason codes.

### Changed

- Production default van `thread_budget_mode=monitor_only`.
- Enforce trong Phase 7 chi goi simulated executor an toan; khong mutate environment/runtime thread setting.
- Khong doi JobQueue scheduling, JobRunner final state/retry/pause/cancel, Generate/Training execution, engine adapter, CPU affinity hoac GPT-SoVITS runtime.

### Notes

- Khong goi `taskset`, `start /affinity`, `psutil.cpu_affinity`, runtime library setter production hoac CPU stress.
- Chua Phase 8/production Thread Budget enforcement.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 6: Runtime Guard Action Foundation

### Added

- Runtime Guard action foundation voi `RuntimeGuardObservation`, pressure levels, action states, stable reason codes va policy fingerprint.
- `runtime_guard_mode` mac dinh monitor_only, giu `runtime_pressure_guard_mode` cu nhu fallback tuong thich.
- Policy additive cho action cooldown, deescalation stable window, observation TTL, retry/backoff va simulated action allow-list.
- `RuntimeGuard` cho pressure classification, WOULD_* action recommendation, cooldown, duplicate suppression, escalation/deescalation hysteresis, retry exhaustion va lease/process reconciliation boundary.
- `RuntimeGuardActionExecutor` va `SimulatedRuntimeGuardActionExecutor` deterministic cho foundation/tests.
- Tests Phase 6 cho pressure boundaries, unknown/invalid/stale, safe mode boundary, destructive unavailable, cooldown, hysteresis, retry va lease/process integration.

### Changed

- Production default van `runtime_guard_mode=monitor_only`.
- Enforce trong Phase 6 chi goi simulated executor an toan; khong pause/terminate/kill-tree process that.
- Khong doi JobQueue scheduling, JobRunner final state/retry/pause/cancel, Thread Budget, Generate/Training execution, engine adapter hoac GPT-SoVITS runtime.

### Notes

- Khong goi `taskkill`, `os.kill`, `psutil.Process.kill` hoac terminate process production.
- Chua Phase 7/production Runtime Guard action.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 5: Process Supervisor va Kill-tree Foundation

### Added

- Process Supervisor foundation voi `ProcessIdentity`, `ProcessSupervisorObservation`, process states/actions va stable reason codes.
- Policy additive cho graceful shutdown, terminate, kill-tree timeout, identity requirement, orphan handling va observation TTL.
- `ProcessProvider` abstraction va `StaticProcessProvider` fake deterministic cho tests.
- `ProcessSupervisor` registry atomic, corrupt registry fail-safe, legacy/unknown field load va temp cleanup.
- Process tree discovery deterministic, sorted, cycle-safe va khong dua PID ngoai tree vao action.
- Shadow shutdown plan cho graceful stop, terminate va kill-tree voi simulated audit.
- Tests Phase 5 cho identity validation, PID reuse, command/executable/parent mismatch, permission/provider unknown, stale, orphan/restart, tree, mode boundary va persistence.

### Changed

- Production default van `process_supervisor_mode=monitor_only`.
- `enforce` trong Phase 5 chi la contract/gate fail-safe; khong production kill process.
- Khong doi JobQueue scheduling, JobRunner flow, Generate/Training execution, Runtime Guard hay Thread Budget.

### Notes

- Khong goi `taskkill`, `os.kill` hoac `psutil.Process.kill`.
- Chua production process provider/kill-tree executor.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 4: Lease Lifecycle v2 Enforcement

### Added

- Lease Lifecycle v2 enforcement path trong `ResourceLeaseManager`, gated boi `resource_lease_v2_mode=enforce`.
- Stable reason codes cho acquire, renew, release, expired, stale, duplicate, owner/process identity mismatch, store corrupt/unavailable va reconciliation.
- Enforce acquire idempotent cho cung job/owner/resource, deny duplicate/conflict/concurrency va fail-safe khi lease store corrupt/unavailable.
- Enforce renew/release voi job_id/owner validation, deterministic clock trong tests va expired lease reconciliation boundary.
- Reconcile enforce cho expired/stale/duplicate theo huong non-destructive unknown.
- Atomic lease store write schema_version 2 voi temp cleanup.
- Tests Phase 4 cho activation modes, acquire/renew/release, expiry/stale/reconcile, corrupt store va rollback invariants.

### Changed

- `enforce` la mode Phase 4 chinh; `enforced` cu duoc giu nhu legacy alias.
- `disabled` va `monitor_only` tiep tuc dung legacy/Phase 3 behavior, khong v2 mutate/block/reconcile.
- JobRunner truyen them job_id/owner khi release lease de enforce co the validate; legacy release van tuong thich.

### Notes

- Default production van `monitor_only`.
- Khong Process Supervisor, khong kill-tree, khong Runtime Guard action, khong Thread Budget enforcement.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 3: Lease Lifecycle v2 Monitor

### Added

- Lease lifecycle v2 foundation voi `ResourceLeaseV2`, `ResourceLeaseObservation`, stable shadow action va stable lease reason codes.
- `ResourceLeaseShadowEvaluator` deterministic, co injectable clock, tinh shadow acquire/renew/release/expiry/stale/reconciliation/duplicate/owner-process-policy mismatch.
- Policy additive fields `lease_renew_interval_seconds` va `stale_lease_handling_mode`, resolve qua `ResourcePolicyService`.
- `ResourceLeaseManager.shadow_observations()` va `shadow_observation_for_job()` de quan sat lease legacy ma khong mutate actual lease.
- Tests Phase 3 cho acquire, renew due/not due, release due, expiry, stale, duplicate, owner mismatch, job/process missing, process identity mismatch, policy fingerprint mismatch, corrupt store, unknown fields, legacy schema va monitor-only invariants.

### Changed

- Actual legacy lease path khong doi: acquire/renew/release/cleanup_stale van la behavior cu.
- Shadow observation khong goi `cleanup_stale()` va khong ghi de corrupt lease store.
- Resource lease v2 van monitor-only; khong block queue, khong doi Job state, khong doi scheduling, khong release/renew actual lease.

### Validation

- `.\.venv\Scripts\python.exe -m compileall src\models\resource_model.py src\services\resource_policy_service.py src\services\resource_lease_manager.py src\services\resource_lease_shadow_evaluator.py tests\test_resource_lease_phase3.py`: dat.
- `.\.venv\Scripts\python.exe -m pytest tests\test_resource_lease_phase3.py -q -p no:cacheprovider`: 16 passed.
- `.\.venv\Scripts\python.exe -m pytest tests\test_resource_policy_v2.py tests\test_resource_manager.py tests\test_resource_safety_phase2.py tests\test_resource_lease_phase3.py -q -p no:cacheprovider`: 52 passed.
- `.\.venv\Scripts\python.exe -m compileall src tests`: exit code 0; van co dong `Can't list 'tests\.pytest_tmp_avs01424_c6'` do thu muc tmp cu bi khoa.

### Notes

- Phase 3 chi shadow/monitor-only, chua enforcement.
- Chua Process Supervisor enforcement/kill-tree.
- Chua Runtime Guard, Thread Budget hoac stale lease cleanup policy moi.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 2: Snapshot Validation va Shadow Decision

### Added

- Snapshot validation cho RAM/GPU/VRAM/Disk voi status `valid`, `invalid`, `unknown`, `stale`.
- Snapshot freshness contract co `captured_at`, age calculation va TTL tu Resource Policy.
- Workload classification foundation: `light`, `cpu_heavy`, `gpu_inference`, `gpu_training`, `io_heavy`.
- Shadow Resource Decision v2 monitor-only voi structured observation: actual decision, shadow decision, reason codes, snapshot status, workload class, policy fingerprint va flags would_block/would_wait/confirmation_required.
- Stable reason codes Phase 2 cho RAM, GPU/VRAM, Disk, stale snapshot, CPU fallback confirmation va heavy job active.
- Tests simulation deterministic cho snapshot validation/freshness, unknown/invalid provider state, workload light/heavy va shadow decision.

### Changed

- `ResourceDecisionService.evaluate()` van tra actual legacy decision cho Queue, nhung gan them `shadow_observation` de quan sat.
- Actual scheduling/runtime behavior khong doi: khong block queue, khong doi job state, khong doi lease, khong doi CPU fallback/thread/batch/runtime guard/process supervisor.
- Shadow decision v2 dung `ResourcePolicyService.resolve()` va `ResolvedResourcePolicy`; actual legacy van dung `load()` projection tuong thich.

### Validation

- `.\.venv\Scripts\python.exe -m compileall src\models\resource_model.py src\services\resource_snapshot_service.py src\services\resource_decision_service.py tests\test_resource_safety_phase2.py tests\test_resource_manager.py`: dat.
- `.\.venv\Scripts\python.exe -m pytest tests\test_resource_safety_phase2.py tests\test_resource_manager.py tests\test_resource_policy_v2.py -q -p no:cacheprovider`: 36 passed.

### Notes

- Phase 2 chi monitor-only/shadow decision, chua enforcement.
- Chua Process Supervisor enforcement/kill-tree.
- Chua runtime pressure guard action.
- Chua thay doi Job Queue scheduling hoac ResourceLeaseManager lifecycle.
- Chua Train that, chua Generate that, khong tich hop GPT-SoVITS runtime moi.

## Resource Safety Hardening Phase 1: Policy v2, Feature Flags va Safe Resolution

### Added

- Resource Policy schema v2 theo huong additive tren model hien co.
- `ResolvedResourcePolicy` voi feature modes, safe reserves, RAM pressure thresholds, thread/batch/concurrency limits, CPU fallback policy, timeout values, provenance va fingerprint deterministic.
- Resource Policy migration v1 -> v2 co backup truoc migration save va idempotent.
- Validation cho invalid feature mode, unknown feature flag, negative reserve, invalid threshold order, invalid thread limit, invalid batch/concurrency, invalid timeout, invalid schema va global-only scope.
- Safe fallback khi primary policy loi: thu backup hop le, neu khong co thi dung built-in safe policy; enforcement modes bi disabled va observability chi monitor_only.
- Runtime override hop le chi tac dong resolved object, khong persist ngam.
- Tests Resource Policy v2 cho migration, fallback, fingerprint, validation, runtime override va khong doi runtime behavior legacy.

### Changed

- `ResourcePolicyService` tro thanh single facade cho policy load/save/resolve.
- Existing runtime consumers tiep tuc dung `load()` projection tuong thich trong Phase 1; policy v2 effective duoc lay qua `resolve()`.
- Khong bat enforcement moi, khong doi scheduling, thread count, batch runtime, CPU fallback runtime, lease lifecycle, Generate hoac Training runtime.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_resource_policy_v2.py tests\test_resource_manager.py -q`: 26 passed, co PytestCacheWarning do khong ghi duoc `.pytest_cache`.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src\models\resource_model.py src\services\resource_policy_service.py tests\test_resource_policy_v2.py`: dat.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: exit code 0; co dong `Can't list` cho pytest tmp cu bi khoa trong `tests`.
- Them `pytest.ini` de canonical pytest chi collect `tests/` chinh thuc va bo qua artifact `audit_bundle/`, `cache/`, thu muc an/pytest tmp.
- Xu ly dung artifact `.pytest_tmp` bi khoa quyen de canonical `--basetemp=.pytest_tmp` co the tao lai.
- On dinh `tests/test_reference_backup_restore.py` bang monkeypatch clock deterministic, khong dung sleep/delay.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest --basetemp=.pytest_tmp -q`: 186 passed, co PytestCacheWarning do khong ghi duoc `.pytest_cache`.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest --collect-only -q`: 186 tests collected.
- `git diff --check -- <Phase 1 files>`: exit code 0, chi co warning LF/CRLF Windows.

### Notes

- Chua Train that.
- Chua Generate that.
- Chua Process Supervisor enforcement/kill-tree.
- Chua runtime pressure guard action.
- Chua nang production capability Generate/Training len READY.

## AVS-014.16A: Foundation Cleanup & Consistency

### Changed

- Khoi tao `docs/PROJECT_STATUS.md` de phan anh dung capability hien tai thay vi de trong.
- Cleanup Generate foundation nhe: bo import khong dung, giam duplicated repository load khi tao/lay session.
- Cleanup API manifest rebuild de sanitize manifest dung contract thay vi dua qua session-result sanitizer.
- Cleanup AudioPage: bo marker PART/END FILE con sot va doan kiem tra hang doi rong khong the chay.
- Cleanup test Generate foundation: bo top-level self-call/print khi import test module.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: dat.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_event.py tests\test_global_events.py tests\test_generate_pipeline_foundation.py tests\test_local_api.py -q`: 26 passed.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest -q`: 168 passed.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe src\bootstrap.py`: target main_application, can_start_main_app true, limited_mode true dung theo capability blocked.
- UI smoke offscreen: MainWindow/Sidebar/9 pages va resize 1100x700, 1366x768, 1600x900, 1920x1080 dat.
- API smoke Generate foundation: readiness planning_ready_execution_unavailable, create session, manifest, resume inspect va manifest rebuild dat.
- `git diff --check`: dat; chi con warning LF/CRLF Windows.

### Notes

- Khong Train that.
- Khong Generate that.
- Khong tich hop GPT-SoVITS runtime.
- Khong sua du lieu that trong projects/workspace/voices.

## AVS-014.16: Generate Pipeline Foundation

### Added

- Generate Pipeline foundation domain models cho Request, Session, Source Snapshot, Document, Chapter, Unit, Attempt, Plan, Manifest, Registry, Settings va StateMachine.
- GenerateRepository ghi JSON atomic theo session va registry.
- GenerateTextStructureService doc pasted text/TXT/DOCX, normalize, detect chapter va split unit ma khong sua file goc.
- GenerateSessionService cho validation, create session, plan/manifest materialization, resume inspection va retry inspection.
- Generate request checksum/materialized_at, frozen plan snapshots/checksum, planned artifact records va basic WAV validation.
- No-loss reconstruction verifier cho Source Snapshot -> normalized text -> chapters/units -> reconstructed text.
- Frozen Plan immutable guard, read-back checksum va plan integrity check.
- Artifact lifecycle foundation: artifact registry, lineage, reservation, temp-to-final promotion, collision recheck va validation gate.
- Resume/Retry execution orchestration foundation voi production UNAVAILABLE va test-only WAV provider trong tests.
- Recovery foundation light scan, temp/orphan classification va manifest rebuild khong load engine/model.
- Job Queue worker `generate_prepare` voi ResourceRequirement CPU-light, khong dung GPU va khong goi engine synthesize.
- AppContext integration cho generate_repository, generate_text_structure_service va generate_session_service.
- Local API Generate foundation endpoints cho readiness, request validation, sessions, plan, chapters, units, attempts, artifacts, manifest, resume/retry va recovery.
- Feature readiness entries tach ro planning/reconstruction/frozen plan/artifact/recovery READY va production execution/output UNAVAILABLE.
- AudioPage co Generate Foundation controls toi thieu cho Validate Request, Tao Plan, Resume Inspect va Retry Inspect.
- Tests Generate Pipeline Foundation cho reconstruction, frozen plan, source deletion, output safety, artifact lifecycle, test-only provider, recovery, Job Queue, Local API va UI smoke.

### Changed

- Generate inference that van tach khoi foundation. Endpoint/worker moi khong tao WAV/MP3 gia va khong danh dau session completed khi chua co audio that.
- Local API readiness doi thanh `planning_ready_execution_unavailable` de tranh overclaim production Generate.
- Production Generate execution tiep tuc bi khoa neu khong co real handler; test-only provider khong anh huong readiness production.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest`
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_generate_architecture.py tests\test_generate_pipeline.py tests\test_local_api.py tests\test_job_system.py tests\test_resource_manager.py tests\test_generate_pipeline_foundation.py`
- UI smoke offscreen trang Tao Audio: foundation Validate/Plan controls khong crash va production execution disabled.

### Notes

- Chua Train that.
- Chua Generate that.
- Chua co Generate Session/Plan UI rieng.
- Chua co resume/retry execution, production artifact lifecycle va WAV/MP3 output that trong foundation endpoint.
- Khong sua GPT-SoVITS runtime.
- Khong sua du lieu that trong projects/workspace/voices.

## AVS-014.14: Job & Queue System

### Added

- JobModel va JobQueueSettings cho job identity, state, scope, priority, dependency, retry, progress, ETA, log, heartbeat va recovery.
- JobStateMachine voi transition validator.
- JobRepository persistent JSON trong `workspace/jobs`, atomic write va corrupt quarantine.
- JobQueueService cho enqueue/dequeue/list, idempotency, priority, dependency, pause/resume/cancel request.
- BaseJobWorker, JobExecutionContext, JobHandlerRegistry va JobRunner.
- Handler an toan: demo_progress, reference_verify, project_validate va project_backup adapter co guard.
- Per-job JobLogService.
- AppContext integration cho job_repository, job_queue_service, job_runner, job_handler_registry, job_log_service va job_recovery_service.
- Queue UI page va Dashboard job summary.
- Local API read-only endpoints `/api/v1/jobs`, `/api/v1/queue`, `/api/v1/jobs/{job_id}` va `/api/v1/jobs/{job_id}/logs`.
- Feature readiness entries cho Job/Queue system.
- Tai lieu Job system.

### Changed

- Queue Generate cu tren AudioPage duoc giu nguyen de tuong thich; Job system moi duoc them song song.
- Global progress/log co the nhan progress tu JobWorker thong qua AppEvents.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest`: 143 passed.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe src\bootstrap.py`: target main_application.
- UI smoke offscreen: MainWindow, 8 pages, resize 1920x1080, 1600x900, 1366x768, 1100x700, 900x600, 800x600.
- `git diff --check`: khong co whitespace error; chi co warning LF/CRLF Windows.

### Notes

- Chua Train that.
- Chua Generate that.
- Chua chay analyzer that.
- Worktree van dirty do du lieu that trong projects/workspace; khong restore/clean/stage/commit/push.

## AVS-014.13: Project & Workspace Manager

### Added

- ProjectConfig lifecycle fields: display_name, description, timestamps, status, archive_state, workspace/project root, source/import/duplicate metadata, favorite, health va active IDs.
- ProjectRegistry model/service cho registry, recent projects, archive/missing metadata.
- ProjectValidationService cho project.json, Project ID, required folders va registry mismatch.
- ProjectBackupService cho backup metadata/config co safety backup truoc restore/repair.
- ProjectPackageService cho export/import package nhe co manifest va path traversal guard.
- ProjectService facade cho create, open, close, switch, recent, rename, duplicate, archive, restore archive, export/import, backup/restore, validation va repair.
- Project Manager UI foundation trong ProjectPage.
- Local API read-only endpoints cho projects/current/project health/workspace.
- Tests Project lifecycle, registry/recent, archive, duplicate, export/import, backup/restore, validation/repair va API read-only.

### Changed

- Project moi uu tien folder ID-based dang `project_000001`.
- Project legacy folder theo ten van load duoc bang migration mem.
- Rename Project chi doi display_name, khong rename folder va khong doi Project ID.
- ProjectPage khong expose delete vinh vien; thao tac xoa cu duoc thay bang Archive.
- MainWindow title hien `AI Voice Studio — <Project Display Name>` hoac `Chua mo du an`.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest`: 121 passed.

### Notes

- Khong Train that.
- Khong Generate that.
- Khong sua GPT-SoVITS runtime.
- Full export/copy asset lon can xac nhan rieng truoc khi mo rong.

## AVS-014.11: Voice DNA Foundation + UI Layout Redesign

### Added

- StyleProfile model cho Reading Style Profile / Voice DNA voi ID rieng dang `style_000001`.
- StyleProfileRepository voi atomic write, backup, migration-safe structure va placeholder analysis files.
- StyleProfileService, StyleProfileIntegrityService, StyleProfileExtractionService va StyleProfileExportService.
- `.avstyle` package export/import voi manifest, checksums va path traversal protection.
- VoiceConfig `reading_style` va Variant style fields: `style_profile_id`, `style_mode`, `style_strength`.
- FeatureReadinessService entries cho style profile management, extraction, import/export, voice link va generation usage.
- Local API endpoints cho Style Profile va Voice style profile.
- UI component foundation va trang `Phong cach doc / Voice DNA`.
- Tai lieu `docs/VOICE_DNA_ARCHITECTURE.md`, `docs/STYLE_PROFILE_DATA_FORMAT.md`, `docs/STYLE_PROFILE_BACKUP_RESTORE.md`, `docs/UI_DESIGN_SYSTEM.md`.

### Changed

- Voice Catalog tra ve thong tin Style Profile an toan, khong leak path runtime/model/checkpoint/checksum.
- GenerationJobService nhan style fields nhung bao loi ro neu engine hien tai chua ho tro Style Profile that.
- Settings co section `Du lieu tham chieu giong doc`.

### Validation

- `python -m compileall src tests`
- `python tests/test_style_profile_foundation.py`
- `python tests/test_local_api.py`
- `python tests/test_bootstrap_feature_readiness.py`
- `python tests/test_generate_architecture.py`
- `python tests/test_settings_local_api.py`

### Notes

- Chua co prosody analyzer that nen extraction khong duoc danh dau ready gia.
- Chua Train that.
- Chua Generate that bang Style Profile.

## AVS-014.10: Bootstrap + Local API Foundation

### Added

- Bootstrap Launcher khong import PySide6 de may thieu dependency van mo duoc First-Run Setup guidance.
- RuntimeEnvironmentManager cho Python app, dependency, FFmpeg/FFprobe, NVIDIA/GPU va GPT-SoVITS Runtime Profile.
- FeatureReadinessService cho trang thai available/degraded/blocked dung chung UI/API.
- Local API MVP `/api/v1` bang Python stdlib HTTP server.
- API Settings group trong trang Cai dat.
- Voice Catalog, Variant Catalog va Generation Job service cho tich hop app video.
- Tai lieu `docs/BOOTSTRAP_FIRST_RUN.md`, `docs/LOCAL_API_V1.md` va `examples/video_app_client.py`.

### Changed

- Local API mac dinh bind `127.0.0.1`, yeu cau token cho moi endpoint tru health.
- Generation job API chi tao job/state/log/temp/output, khong Generate that khi Voice chua co model/reference hop le.
- Voice/Variant catalog chi tra ve thong tin an toan, khong leak path runtime/model/checkpoint/pretrained.

### Validation

- Compileall va script tests cho Bootstrap, Feature Readiness, Local API, Settings API group.

### Notes

- Chua them FastAPI/Uvicorn; OpenAPI tu dong chua co trong MVP.
- Chua Train that va chua Generate that.

## AVS-001 đến AVS-012

### Added

- Phân tích kiến trúc và lập roadmap.
- Chuẩn hóa AppContext, EngineManager, Project, Workspace, Voice, Runtime và Engine Config.
- GPT-SoVITS Generate end-to-end.
- Dataset validation, manifest, report, ZIP protection, workspace scan và segmentation.

### Changed

- Chuẩn hóa contract chính giữa model/config/service/json cho Project, Workspace và Voice.
- Tách cấu hình máy cá nhân khỏi source sau test generate thật.

### Validation

- Các test core/workspace/event/settings được dùng làm baseline.
- Generate thật đã được kiểm chứng ở AVS-009, sau đó dọn dữ liệu test ở AVS-010.

### Notes

- AVS-014 Train thật chưa bắt đầu.

## AVS-013: Audio Alignment Pipeline

### Added

- Pipeline chuẩn bị audio train từ dataset/segmentation.
- Output cache gồm clip, transcript, metadata.list, alignment manifest/report và errors.log.

### Changed

- Không sửa audio/text gốc.
- Chỉ xử lý trong cache.

### Validation

- Chạy thử giới hạn nhỏ trên workspace Thu Minh.

### Notes

- Pipeline cần Faster-Whisper runtime ổn định để có timestamp thật.

## AVS-013.5: Faster-Whisper Runtime Validation

### Added

- Runtime validation cho Faster-Whisper.
- Trạng thái package_missing, model_missing, cuda_unavailable, model_load_failed, ready.
- Hỗ trợ model local/cache, device và compute_type.

### Changed

- Không tải model âm thầm.
- Metadata language thống nhất `vi`.

### Validation

- Kiểm tra package/model/runtime.
- Mock alignment test và chạy thật giới hạn nhỏ.

### Notes

- Runtime thật đã dùng model `small` local cache.

## AVS-013.6: Quality-First Dataset Alignment

### Added

- AlignmentQualityConfig tập trung ngưỡng.
- Word timestamp từ Faster-Whisper.
- Split clip dài theo sentence/word timestamp, không cắt giữa từ.
- Source report, weak_source, progress payload.
- RuntimeProfile model/service nền tảng.

### Changed

- metadata.list chỉ chứa valid clip được phép train.
- Weak source mặc định không ghi vào metadata.
- Ratio fallback không được dùng cho valid.

### Validation

- `python -m compileall src tests`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- Chạy thật giới hạn 1 source trên workspace Thu Minh: 19 valid, 9 suspicious, 0 errors.
- ffprobe clip valid: pcm_s16le, mono, 32000 Hz, duration 5.16s.

### Notes

- Cần review suspicious và hoàn thiện Text ↔ MP3 Matching Rules trước AVS-014.

## AVS-013.7: Text ↔ MP3 Matching Rules

### Added

- Ghép Text ↔ MP3 theo số chương trước.
- Hỗ trợ một text ghép nhiều MP3 cùng chương theo thứ tự part.
- Test cho matching theo chương, không ghép chéo số, bỏ file test và file có chữ Trung.

### Changed

- DatasetService ghi thêm `match_rule`, `match_key`, `audio_part` vào item/manifest.
- File có dấu hiệu `test` không được ghép tự động.

### Validation

- `python -m compileall src/services/dataset_service.py tests/test_dataset_matching.py`
- `tests/test_dataset_matching.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`

### Notes

- Chưa dùng ASR để xác minh nội dung ở bước matching; ASR vẫn thuộc bước alignment/quality sau đó.
- Dataset Health là bước tiếp theo trước AVS-014.

## AVS-013.8: Dataset Health

### Added

- TextMatchingService cho luật ghép Text ↔ MP3.
- Dataset Health report gồm total_mp3, total_text, matched, unmatched, ignored_test, ignored_chinese, filename_content_mismatch, duplicate, missing_audio, missing_text, usable_percent.
- Issue report có file, reason và suggestion.
- Chặn trước Alignment nếu Dataset Health có lỗi chặn.

### Changed

- DatasetService dùng TextMatchingService để chuẩn hóa tên, lấy số chương và phát hiện file test gần giống.
- Dataset manifest/report nâng schema lên 2 và chứa health.
- DatasetSegmentationService truyền Dataset Health lên bước sau.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_workspace.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- Chạy Dataset Health trên workspace Thu Minh: total_mp3 68, total_text 160, matched 54, missing_text 14, ignored_test 22, ignored_chinese 137, duplicate 1, usable_percent 79.41.

### Notes

- Workspace Thu Minh còn Dataset Health blocking_errors, cần xử lý trước AVS-014.

## AVS-013.9: Dataset Workflow

### Added

- WorkflowConfig model cho Input Folder, Output Folder và Use Input Folder as Output.
- WorkflowService để tạo, validate và resolve output folder.
- Config mặc định cho workflow dùng input folder làm output.
- Test workflow config/service.

### Changed

- TextMatchingService được đơn giản hóa: bỏ kiểm tra tiếng Trung, chỉ bỏ file test/gần giống test và trích số chương.
- DatasetService bỏ phân loại Chinese.
- Dataset Health chuyển sang các trường: total_mp3, total_text, matched, missing_audio, missing_text, duplicate, invalid_filename, test_version, filename_content_mismatch, usable_percent.
- File không lấy được số chương trả `invalid_filename`.
- File test/gần giống test trả `test_version`.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- Chạy Dataset Health trên workspace Thu Minh: total_mp3 68, total_text 160, matched 68, duplicate 55, test_version 22, usable_percent 100.0.

### Notes

- Chưa Train.
- Chưa Generate.
- Workspace Thu Minh vẫn còn blocking_errors do duplicate, test_version, broken_file và empty_file.

## AVS-013.10: Dataset Repair

### Added

- DatasetRepairService cho detect, repair, skip và report các lỗi Dataset Health.
- DatasetRepairConfig và DatasetRepairIssue để chuẩn bị Auto Repair hoặc Manual Review.
- WorkflowConfig bổ sung `auto_repair` và `review_mode`.
- Dataset Health đếm thêm `empty_file`, `empty_content` và `broken_file`.

### Changed

- Duplicate được repair an toàn trong cache bằng cách copy bản trùng vào ignored, không sửa file gốc.
- Các lỗi không sửa an toàn như broken_file, empty_file, missing_audio, missing_text, filename_content_mismatch, test_version và invalid_filename được skip/report để review.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- Chạy Dataset Health + Repair trên workspace Thu Minh: repaired 55 duplicate, skipped 42 lỗi còn cần review.

### Notes

- Chưa Train.
- Chưa Generate.
- AVS-014 chỉ nên bắt đầu sau khi review xong các skipped errors còn lại.

## AVS-013.11: Dataset Review

### Added

- DatasetReviewService để tạo review_report.json trước Alignment/Train.
- DatasetReviewConfig và DatasetReviewItem.
- Review item gồm source_audio, source_text, reason, suggestion và status pending/approved/rejected/ignored.
- Hỗ trợ approve_all, reject_all, ignore_all và filter theo reason/code.

### Changed

- Dataset workflow cập nhật thành Scan → Health → Repair → Review → Alignment → Train.
- TrainAudioPrepService có thể nhận review_report; nếu không có review_report thì vẫn chặn Dataset Health như trước.

### Validation

- `python -m compileall src tests`
- `tests/test_dataset_matching.py`
- Chạy Dataset Health + Repair + Review trên workspace Thu Minh: 42 review items pending; approve_all làm train_allowed = True.

### Notes

- Chưa Train.
- Chưa Generate.
- AVS-014 chỉ nên bắt đầu sau khi người dùng chốt approve/reject/ignore cho review_report.

## AVS-014: GPT-SoVITS Training Validation

### Added

- TrainConfig tập trung cấu hình validation_only, smoke_test, metadata_path, runtime_profile_id và tham số train.
- TrainJobState để lưu run_id, checkpoint, model_output, report_path và resume state.
- TrainingService.prepare_train cho validation gate trước train.
- Train report gồm voice, runtime profile, Python/torch/device/GPU, metadata, clip count, duration, parameters, run state, warnings và errors.
- Progress payload cho training validation.
- Test training pipeline cho review, metadata, WAV format, runtime, pretrained model, validation_only, smoke_test mock, report, progress, run_id, no overwrite và resume state.

### Changed

- Train thật chưa chạy nếu chưa có xác nhận và chưa chốt tham số.
- Model output chuẩn bị theo voices/<voice_id>/model/<run_id>/.
- Runtime lấy từ Runtime Profile hiện tại, không hard-code đường dẫn GPT-SoVITS/Python/pretrained model.

### Validation

- `python -m compileall src tests`
- `tests/test_training_pipeline.py`
- `tests/test_dataset_matching.py`
- `tests/test_alignment_runtime.py`
- `tests/test_alignment_quality.py`
- `tests/test_runtime_profile.py`
- `tests/test_core.py`
- `tests/test_event.py`
- `tests/test_settings.py`
- `tests/test_workspace.py`
- Validation-only trên workspace Thu Minh: 19 clip, khoảng 140.04 giây, chưa ready vì review_report còn pending và chưa có Runtime Profile mặc định.

### Notes

- Chưa Train thật.
- Chưa Generate.
- Cần người dùng chốt Dataset Review, Runtime Profile và tham số train trước smoke_test/train thật.

## AVS-014.1: Runtime Profile và GPT-SoVITS Smoke Test

### Added

- DatasetReviewService có helper apply_decisions() và write_report() để chốt review report thực tế trước train.
- RuntimeProfileService có create_gpt_sovits_profile() và detect_gpt_sovits_runtime() để tạo profile GPT-SoVITS v2Pro từ runtime root thật.
- Runtime validation phát hiện thêm train scripts và pretrained models thật của GPT-SoVITS.
- TrainingService smoke test tối thiểu gọi runtime Python thật, đọc metadata/WAV, kiểm tra CUDA và ghi stdout/stderr/report/checkpoint smoke.

### Changed

- Smoke command dùng absolute path cho script/output/log để chạy an toàn khi cwd là runtime root.
- Relative audio path trong metadata được resolve theo app root khi smoke test, không sửa metadata.list gốc.
- Train report bổ sung runtime_validation, script_paths, pretrained_paths và smoke_test.

### Validation

- `python -m compileall src tests`
- `tests/test_training_pipeline.py`
- Dataset Review Thu Minh: approved 0, rejected 20, ignored 22, pending 0, train_allowed = True.
- Runtime validation READY: Python 3.9.13, torch 2.0.0+cu118, CUDA True, faster-whisper 1.1.1, GPU Quadro P1000.
- Validation-only Thu Minh: 19 clip, khoảng 140.04 giây, không lỗi.
- Smoke test run `avs0141_smoke_20260716_053444`: exit code 0, CUDA True, checkpoint smoke được tạo.
- ffprobe clip valid đầu tiên: pcm_s16le, mono, 32000 Hz, duration 5.16s.

### Notes

- Chưa full train GPT-SoVITS.
- Smoke test hiện tại là runtime/process smoke tối thiểu; chạy full `s1_train.py`/`s2_train.py` cần tham số train và dataset train format đầy đủ được chốt.

## AVS-014.2: Full Dataset Preparation + Progress Validation

### Added

- Runner full alignment Thu Minh có progress log, alignment_state resume và runner_result.
- Báo cáo kết quả full dataset preparation cho metadata train.

### Changed

- Không đưa suspicious vào metadata train.
- Không chạy lại source đã hoàn thành.
- Không xử lý hoặc commit dữ liệu project/workspace thật đang dirty.

### Validation

- Runner hoàn tất 68/68 source, stderr rỗng, errors = 0.
- `metadata.list`: 13 valid clips, tổng 93.98 giây, trung bình 7.23 giây.
- Suspicious: 76 clips.
- Source skipped toàn file: 2 source với `source_error_rate_exceeded`.
- ffprobe toàn bộ metadata: WAV tồn tại, đọc được, mono, pcm_s16le, 32000 Hz, transcript không rỗng, không trùng clip.
- `python -m compileall src tests`
- Script tests với `PYTHONPATH=src`: pass.
- UI smoke: MainWindow chạy được.

### Notes

- Chưa Train thật.
- Chưa Generate.
- Dataset valid hiện còn nhỏ; nên review/sửa suspicious nếu mục tiêu là train chất lượng cao.

## AVS-014.3: Suspicious Review & Recovery

### Added

- SuspiciousRecoveryService để xử lý lại suspicious trong cache riêng.
- Recovery report gồm recovered_valid, still_suspicious, rejected, recovery_method, old_similarity, new_similarity, source_file và reason.
- Test recovery cho gộp ASR segment, không reuse ASR segment, không tự approve dưới threshold và metadata valid-only.

### Changed

- Recovery không thay pipeline alignment chính.
- Recovery không hạ similarity threshold toàn cục dưới 90.
- Recovery không dùng ratio fallback cho valid.
- Metadata recovery được ghi riêng, không ghi đè baseline AVS-014.2.

### Validation

- Preview 1 source no_alignment_match: recovered_valid = 0.
- Preview 1 source similarity_too_low: recovered_valid = 0, best new_similarity mẫu đạt 79.21 nhưng vẫn dưới 90.
- Preview 1 source source_error_rate_exceeded: recovered_valid = 0.
- Metadata preview validate ffprobe đạt: 13 clips, không trùng, WAV đọc được, mono, pcm_s16le, 32000 Hz.
- `python -m compileall src tests`
- Script tests với `PYTHONPATH=src`: pass.
- UI smoke: MainWindow chạy được.

### Notes

- Không chạy full suspicious recovery vì preview không tốt.
- Dataset cuối vẫn 13 valid clips / 93.98 giây, dưới 10 phút.
- Chưa Train thật.
- Chưa Generate.

## AVS-014.4: Full Dataset Expansion + Voice Architecture Foundation

### Added

- WorkflowConfig ho tro rieng audio_folder, text_folder, output_folder, use_input_folder_as_output, selected_voice_id va runtime_profile_id.
- ProjectConfig luu lua chon dataset cuoi theo Project: audio/text/output folder, use_input_as_output, Voice va Runtime Profile.
- DatasetService.scan_folders() cho nguon MP3 va Text/DOCX tach rieng.
- DatasetSegmentationService va TrainAudioPrepService co entrypoint prepare_from_folders().
- FullDatasetPreparationService gom workflow Scan -> Health -> Repair -> Review -> Alignment -> Metadata Validation.
- Voice architecture contract cho Voice identity, Variant, Preset, Reference Style, Text Profile va Generate Request.

### Changed

- API cu scan(folder) va prepare(source, ...) duoc giu tuong thich.
- Global progress payload alignment bo sung valid, suspicious va errors.
- Dataset cu AVS-014.2/014.3 duoc giu lam cache lich su, khong ghi de.

### Validation

- Scan nguon workspace Thu Minh moi: total_mp3 198, total_text 202, matched 183, missing_audio 4, missing_text 15, test_version 1, broken_file 14, blocking_errors 34.
- Alignment chua chay vi Review con 34 pending va train_allowed = false.

### Notes

- Chua Train that.
- Chua Generate.
- Can review/resolve 34 blocking items truoc khi chay Alignment toan bo nguon moi.

## AVS-014.5: Workspace Compatibility + Automatic Review

### Added

- Workflow source_mode cho Same Folder Mode va Separate Folder Mode.
- WorkflowService helper create_same_folder_config(), create_separate_folder_config() va detect_legacy_workspace().
- DatasetReviewService.auto_review() voi rule an toan: ignored/rejected theo code, khong dung Approve All.
- FullDatasetPreparationService tu dong auto review khi review_mode = auto.
- TrainAudioPrepService ho tro max_new_sources de resume theo batch ma khong ghi trung metadata.

### Changed

- ProjectConfig luu them last_source_mode.
- Same Folder Mode tuong thich workspace/<Voice Name>/ hien tai, audio_folder va text_folder cung tro vao mot thu muc.
- AudioService doc stderr/stdout ffprobe/ffmpeg bang utf-8 errors=replace de tranh loi decode Windows.

### Validation

- Auto Review Thu Minh: total 34, pending 0, rejected 14, ignored 20, train_allowed true.
- Alignment da chay resume mot phan: 12/183 source, 155 valid clips, 50 suspicious, 0 errors, 946.32 giay valid.
- Metadata hien tai validate ffprobe dat: 155 clips, khong duplicate, WAV doc duoc, mono, pcm_s16le, 32000 Hz, transcript khong rong.

### Notes

- Full Alignment toan bo 183 source chua hoan tat vi thoi gian runtime du kien nhieu gio.
- Co the tiep tuc chay resume tu alignment_state.json, khong xu ly lai source da hoan thanh va khong ghi trung metadata.
- Chua Train that.
- Chua Generate.

## AVS-014.6: Generate Architecture Foundation

### Added

- GenerateSelectionConfig, GenerateRequest, GenerateResult, VariantDecision, VariantTimeline, StyleDecision, StyleTimeline, GenerateProgress, SpeedProfile va TempWorkspace.
- GeneratePlanningService de validate Standard Mode, AI Style Mode, Variant scope, Style scope, speed va timeline boundary.
- TempWorkspaceService de tao temp/generate|train|alignment/<job_id> va cleanup/keep theo trang thai job.
- ProjectConfig/ProjectService luu lua chon Generate cuoi theo Project.
- Test generate architecture cho Standard, AI Style, all/ticked scope, no selection, fallback scope, boundary, speed, temp workspace va project memory.

### Changed

- Chua thay doi GenerateService cu va chua goi engine generate that.
- Moi Voice co default_variant_id va default_style_id de fallback khong hard-code theo logic engine.
- Custom speed chi cho phep 0.80 den 1.20; preset speed van la che do dac biet.
- Cleanup policy duoc chot: success xoa temp, pause/error giu temp, cancel hoi nguoi dung, resume dung temp cu.
- Fallback Variant/Style chon candidate confidence cao nhat trong allowed scope neu default khong duoc phep.
- Temp file khong duoc de trong output folder.

### Validation

- `python -m compileall src tests`
- `tests/test_generate_architecture.py`

### Notes

- Chua Train that.
- Chua Generate.
- UI Generate multi-select chua hoan thien; Sprint tiep theo la AVS-014.7 Generate UI hoan chinh va Generate that.

## AVS-014.7: Generate UI + Generate Pipeline

### Added

- GenerateOptionsPanel cho AudioPage: Standard Mode, AI Style Mode, Voice, Variant, All Variants, Style scope, All Styles, Speed, Output, WAV/MP3 va MP3 bitrate.
- GenerateAudioProfile tap trung pause, crossfade, retry_count, output format va MP3 bitrate.
- ContextAnalysisService de chia text thanh segment/context va tao candidate score cho AI Style Mode.
- GeneratePlanningService.build_plan() de tao GeneratePlan/GenerateChunk tu VariantTimeline va StyleTimeline.
- GeneratePipelineService de validate request, generate tung chunk, retry, merge, report va emit global progress.
- AudioMergeService de merge chunk bang ffmpeg va export WAV/MP3.
- Test generate pipeline cho model missing, Standard Mode, AI Style scope, MP3 output, resume chunk da xong, retry failure va khong tao final output gia.

### Changed

- GenerateService co entrypoint generate_request() moi, giu queue API cu.
- ProjectConfig/ProjectService luu lua chon Generate cuoi theo Project: preset/reference/text profile, input/output, output format va bitrate.
- GPTSoVITSEngine dung default_variant_id cua Voice config khi co.
- Chunk loi sau retry_count = 1 se dung toan job, giu temp/state/log va ghi report ro chunk_id/text/error.
- Temp generate nam trong temp/generate/<job_id>, output chi chua final artifact/report.

### Validation

- `python -m compileall src tests`
- Toan bo `tests/test_*.py` voi `PYTHONPATH=src`: pass.
- `git diff --check`: khong co whitespace error, chi co canh bao LF/CRLF cua Git tren Windows.
- UI smoke ngoai sandbox: MainWindow dung duoc va mo `AudioPage`.

### Notes

- Chua Train that.
- Chua Voice Morph.
- Generate that can Voice co gpt_model, sovits_model, reference_audio va reference_text hop le.
- Crossfade/pause da co config tap trung; natural silence detection va crossfade boundary safety can tiep tuc tinh chinh o buoc audio quality.

## AVS-014.8: Full Alignment Completion + Real Training Preparation

### Added

- Dataset Quality Report cho full dataset Thu Minh.
- Reference Audio candidates duoc chon tu clip valid similarity cao.
- Metadata final duoc rebuild tu `alignment_state.json` sau khi resume hoan tat.

### Changed

- TrainAudioPrepService ghi metadata.list bang atomic write.
- Resume state flush metadata.list dinh ky theo state hien tai de giam lech giua checkpoint va metadata.

### Validation

- Resume Full Alignment tu checkpoint `cache/avs0145_full_dataset_thu_minh/alignment/alignment_state.json`.
- Alignment hoan tat 183/183 source.
- Metadata final: 2329 clip, tong thoi luong 13232.40 giay, similarity min/avg/max = 90.00 / 95.62 / 100.00.
- Metadata validation dat: khong duplicate, WAV ton tai/doc duoc, mono, pcm_s16le, 32000 Hz, transcript khong rong.
- Train validation_only dat voi Runtime Profile `gpt_sovits_v2pro_default`: Python 3.9.13, torch 2.0.0+cu118, CUDA, Quadro P1000 4096 MiB.
- `python -m compileall src tests` dat.
- `git diff --check` khong co whitespace error; chi co canh bao LF/CRLF tren Windows.

### Notes

- Chua Train that.
- Chua Generate.
- `pytest` va `PySide6` dang thieu trong Python 3.12 hien tai nen chua chay duoc pytest/UI smoke bang interpreter nay.
- Can nguoi dung chot Reference Audio va tham so Train that truoc khi goi `s1_train.py`/`s2_train.py`.

## AVS-014.9: Runtime Training Profile + Pre-flight Train

### Added

- RuntimeTrainingProfile va HardwareInfo model.
- RuntimeTrainingProfileService de detect hardware, chon Auto/Compatibility/Performance/Custom va tao app-managed runtime copy.
- SettingsPage co khu Runtime & Training voi Profile, Auto Detect Hardware, hardware/runtime/training fields va cac nut Detect Again, Validate Runtime, Reset to Recommended.
- RuntimeTrainingHelpService gom noi dung huong dan tieng Viet, tooltip, canh bao de hieu va huong dan doi may.
- Dialog "Huong dan Runtime & Training" trong Settings, co nut sao chep huong dan.
- Settings Runtime & Training co handler that cho detect hardware, validate runtime, reset recommended, xem cau hinh thuc te va copy report.
- ProjectConfig/ProjectService luu cau hinh Runtime Training Profile theo Project.
- Test cho Auto detect Quadro P1000, Performance mock, Custom roundtrip, Project memory va app-managed runtime copy.
- Test cho noi dung tieng Viet, giai thich profile, tham so, canh bao va hardware summary khong hard-code GPU.
- Test source-level cho Runtime & Training button wiring de tranh nut placeholder khi chua co PySide6.

### Changed

- Runtime goc GPT-SoVITS khong bi sua.
- Neu SoVITS runtime hard-code `num_workers=5`, app-managed copy chi doi ban copy sang `num_workers=0`.
- Kien truc Voice/Variant tiep tuc giu mot model chinh cho Voice 0001, khong train model rieng cho Variant.
- Cac nut/nhan trong Runtime & Training duoc Viet hoa de nguoi dung pho thong de hieu hon.

### Validation

- `python -m compileall src tests` dat.
- `python tests/test_runtime_training_help.py` dat.
- `python tests/test_runtime_training_profile.py` dat.
- `python tests/test_runtime_profile.py` dat.
- `python tests/test_training_pipeline.py` dat.
- Auto tren may hien tai chon Compatibility: batch_size 1, num_workers 0, compute cuda.
- App-managed runtime copy: `voices/0001/model/avs0149_preflight_runtime_20260717_053711/runtime_copy`, compile copy dat.
- Train validation_only: `avs0149_profile_validation_20260717_053737`, status `validation_ready`, 2329 clip, 13232.40 giay, CUDA/Quadro P1000.
- Interpreter ung dung hien tai `C:\Program Files\Python312\python.exe` thieu `PySide6` va `pytest`; UI smoke/pytest chua chay duoc bang interpreter nay.
- Pre-flight moi tao run directory `voices/0001/model/avs0149_thu_minh_train_20260717_061215`, validation_only dat `validation_ready`, app-managed runtime copy compile dat.
- GPT command preview duoc ghi tai `voices/0001/model/avs0149_thu_minh_train_20260717_061215/reports/gpt_command_preview.json`, nhung `ready_to_run=false` vi config copy thieu key bat buoc cho `s1_train.py`.

### Notes

- Chua Train that.
- Chua Generate.
- `python -m pytest` va UI smoke bang Python 3.12 hien tai van bi chan vi thieu `pytest`/`PySide6`.
- Truoc khi goi GPT stage can tao/ghep du config train semantic/phoneme/output/half weights cho `s1_train.py`.

## AVS-014.12: Training Workflow Clarification + Reference Data Architecture

### Added

- `TrainingReferenceConfig` va `SpeakerReference` model.
- `TrainingReferenceService`, `TrainingReferenceResolver`, `ReferenceAudioValidationService` va `AudioTextPairService`.
- TrainingPage moi co scroll foundation va ba reference mode loai tru nhau.
- Voice rename validation giu nguyen Voice ID.
- Style Profile rename validation giu nguyen Style Profile ID.
- Feature readiness cho training reference, speaker reference, rename va scroll/responsive.
- Test moi cho config/reference resolver/audio-text/audio validation/rename/scroll.
- Tai lieu ve data ownership, speaker reference, naming/identity va scroll/responsive.

### Changed

- VoiceConfig them `speaker_reference` va `training_reference` theo huong migration-safe, khong xoa `reference_audio`/`reference_text`.
- TrainingPage khong goi train that truc tiep; train that bi khoa trong sprint nay.
- Style Profile creation tu TrainingPage chi tao draft/pending va goi extraction state blocked, khong tao Voice DNA gia.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests` dat.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest` dat: 118 passed.

### Notes

- Chua Train that.
- Chua Generate that.
- Chua chay Voice DNA analyzer that.
# AVS-014.13.1

- Added Reference Vault foundation for managed reference audio/text/manifest assets.
- Added ReferenceAsset, ReferenceRegistry and persistent audio-text manifest models.
- Added ReferenceVaultService and ReferenceRegistryService with atomic import, checksum verification and deduplication.
- Extended SpeakerReference, VoiceConfig, TrainingReferenceConfig and StyleProfile with migration-safe stable asset ID fields.
- Extended TrainingReferenceResolver to prefer managed asset IDs while keeping legacy path fallback.
- Extended Project backup/export/import/validation with optional reference vault support.
- Added reference persistence tests.
# AVS-014.15

- Added Intelligent Resource Manager foundation.
- Added resource models for hardware, snapshots, requirements, decisions, policies and leases.
- Added safe hardware detection for CPU/RAM/Disk/FFmpeg/NVIDIA GPU/VRAM.
- Added resource snapshot, policy, decision, lease and monitor services.
- Integrated `waiting_resource` state and resource fields into JobModel.
- Integrated Resource Manager into JobQueueService scheduling and JobRunner lease release.
- Added Resource Monitor page, Dashboard resource card, JobsPage resource details and Settings resource policy summary.
- Added read-only Local API resource endpoints.
- Added resource readiness entries and Resource Manager tests.
- No Train, Generate, analyzer or GPT-SoVITS runtime mutation was performed.

---
