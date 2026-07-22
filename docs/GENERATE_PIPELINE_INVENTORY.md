# Generate Pipeline Inventory

Sprint: AVS-015 Sprint 1  
Phạm vi: khảo sát và chuẩn hóa mô tả luồng Generate hiện tại.  
Loại thay đổi: tài liệu kỹ thuật; không thay đổi pipeline, runtime, UI hoặc capability production.

## 1. Kết luận điều hành

Repository hiện có **hai đường Generate song song**:

1. **Generate Session pipeline** là đường contract mới, có Session/Plan/Unit/Attempt/Artifact, Job Queue, Runtime Doctor, resource requirement, provider GPT-SoVITS và API.
2. **Legacy Generate pipeline** là đường UI cũ từ `AudioPage` qua `GenerateService` / `GeneratePipelineService`, có QueueWorker riêng và gọi engine manager theo đường cũ.

Đường Session pipeline đã có orchestration và production binding có điều kiện, nhưng không được xem là production audio generation `READY` chỉ vì source hoặc controlled tests tồn tại. Production execution chỉ có thể được enqueue khi Runtime Doctor thỏa gate; result chỉ là thành công khi artifact đã được validate và promote đúng lineage. Hiện không có bằng chứng real end-to-end production smoke/listening review trong phạm vi khảo sát này để nâng Generate execution, Preview, WAV output hoặc MP3 output lên `READY`.

Đường legacy vẫn là đường UI mà nút Generate hiện gọi để tạo audio. Foundation controls trong cùng `AudioPage` chỉ validate, tạo Session/Plan và inspect resume/retry; chúng chưa là UI consumer hoàn chỉnh cho enqueue Unit, Job state và Artifact result của Session pipeline.

## 2. Pipeline Diagram

### 2.1 Generate Session pipeline hiện hành

```text
UI Foundation controls / Local API
        |
        v
GenerateSessionService
  - validate request
  - create immutable GenerateSession
  - snapshot source
  - normalize / structure / split
  - freeze GeneratePlan
  - create planned Artifact records
        |
        +--> GenerateRepository
        |      workspace/generate/sessions/<session_id>/
        |      session/request/document/plan/manifest/artifacts persistence
        |
        v
LocalApiService enqueue / JobQueueService
        |
        v
JobRunner + GenerateUnitJobWorker
  - immutable session_id + unit_id payload
  - ResourceRequirement: GPU, no implicit CPU fallback
        |
        v
GenerateSessionService.execute_unit_with_provider
        |
        v
GPTSoVITSGenerateProvider
  - resolve persisted session/plan/unit/attempt/artifact
  - resolve production reference binding snapshot
  - validate runtime/profile, voice and model binding
        |
        v
EngineManager
        |
        v
GPTSoVITSEngine -> GPTSoVITSAdapter -> Runtime / inference_cli.py
        |
        v
temporary unit output in managed session temp path
        |
        v
Artifact reservation -> WAV validation -> promote to final path
        |
        v
persist Attempt / Unit / Artifact state and Job result
        |
        +--> Local API read endpoints
        +--> future/full Session UI result consumer (not yet wired)
```

### 2.2 Legacy parallel pipeline

```text
AudioPage.generate_current / AudioPage.generate_queue
        |
        v
GenerateService.generate_request / QueueWorker
        |
        v
GeneratePipelineService
        |
        v
EngineManager -> legacy engine path
        |
        v
legacy output path / merge service / UI status
```

Đường này không materialize immutable Generate Session/Plan/Unit/Attempt/Artifact theo contract mới trước khi thực thi. Nó phải được coi là đường legacy song song, không phải completion của AVS-015 Session pipeline.

## 3. Component Inventory

| Layer | Component / source | Input | Output | Owner | Dependency | Blocking condition / trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| UI legacy | `src/pages/audio_page.py` (`generate_current`, `generate_queue`) | Current project/voice, widget request, selected files | UI status/progress; legacy generate call | `AudioPage` | `GenerateService`, legacy queue/worker | Voice chưa chọn; legacy result lỗi. Không phải Session execution UI. |
| UI foundation | `src/pages/audio_page.py` (`foundation_payload`, validate/plan/inspect handlers) | Current project/voice and widget fields | Validation, Session ID, plan count, resume/retry inspection text | `AudioPage` | `AppContext.generate_session_service`, engine capability router | Chỉ tạo/inspect foundation data; không enqueue Unit, không consume Job/Artifact result. |
| Local API | `src/services/local_api_service.py` | Authenticated local API request, immutable IDs, expected fingerprints | Safe Session/Plan/Unit/Attempt/Artifact/Job response | `LocalApiService` | `GenerateSessionService`, runtime profile, job queue | Runtime Doctor not ready returns actionable unavailable/blocked response for execution; paths are redacted. |
| Request validation | `src/services/generate_session_service.py` | Request mapping: project/voice/variant/style/reference/text or text file/output/language | Validation report / issues | `GenerateSessionService` | Request validator, language routing, persistence rules | Missing/invalid IDs, source, output policy, route/binding validation failure. |
| Session creation | `src/services/generate_session_service.py` | Validated Generate Request | `GenerateSessionRecord`, source snapshot, document, frozen plan, manifest | `GenerateSessionService` | Repository, text structure service, artifact service | Request validation / source read / reconstruction / freeze failure. |
| Immutable text planning | `src/services/generate_text_structure_service.py` and Generate models | Source snapshot | Normalized document, chapters, units with immutable IDs and separators | Text structure service | Text/source reader; DOCX dependency where relevant | Source unavailable; DOCX support dependency absent; reconstruction verification failure. |
| Persistence | `src/repositories/generate_repository.py` | Session records and mutable runtime state | Atomic session JSON and registry under `workspace/generate/` | Generate repository | Managed workspace filesystem | Session/plan integrity and persistence failures. Repository does not own workflow semantics. |
| Artifact lifecycle | `src/services/generate_artifact_service.py` | Planned artifact, attempt, managed temp output | Reservation; validated and promoted final artifact or classified failure | Artifact service | Path policy, `wave` basic WAV validation, repository | Collision/reservation failure, temp absent, invalid WAV, lineage mismatch, promotion failure. Existing output is not silently overwritten. |
| Runtime readiness | `src/services/runtime_profile_service.py` | Runtime profile plus required Generate gates | Runtime Doctor evidence/status | Runtime profile service | runtime profile config, executable/script/assets/FFmpeg/FFprobe checks | Missing/invalid runtime profile, script, assets, environment or required tool causes `UNAVAILABLE`/`BLOCKED`; discovery alone is not execution proof. |
| Reference binding | `src/services/production_reference_binding_service.py`; `production_reference_binding_snapshot_service.py` | Persisted voice/reference/style identifiers and frozen request/plan context | Production binding / immutable binding snapshot or blocker | Binding services | Voice/reference persistence and ownership validation | Missing/incompatible model/reference/binding, invalid lineage or unresolvable immutable IDs. |
| Execution provider | `src/services/gpt_sovits_generate_provider.py` | Persisted session/unit/artifact plus managed temp path | Engine invocation or provider error | `GPTSoVITSGenerateProvider` | Session service, production binding, engine manager | Runtime gate, voice-model, binding, engine selection or engine result failure. Provider does not make an Artifact valid by itself. |
| Job scheduling | `src/services/job_queue_service.py`, `job_runner.py`, `job_worker.py` | Job payload with `project_id`, `session_id`, `unit_id`, voice ID | Persisted job state/result/logs | Job Queue / Runner / Worker | Job repository, handler registry, resource manager, service | Dependency, cancellation/pause/timeout, handler missing, resource preflight or lease failure. |
| Prepare job | `GeneratePrepareJobWorker` in `src/services/job_worker.py` | Request snapshot | Session/manifest creation result | Job worker | Generate Session service | CPU-light; no GPU requirement; only planning/persistence, no audio generation. |
| Unit execution job | `GenerateUnitJobWorker` in `src/services/job_worker.py` | Immutable `session_id`, `unit_id`, `project_id`, voice ID | Provider result and persisted runtime state | Job worker | Generate session service, GPT-SoVITS provider, resource manager | GPU requirement; CPU fallback disabled; Runtime Doctor and provider gates must pass. |
| Engine selection | `src/core/engine_manager.py` | Normalized engine request | Engine result / error | Engine manager | Registered engine and capability selection | No compatible engine/route, runtime unavailable, engine failure. |
| Engine / adapter | `src/engines/gpt_sovits_engine.py`, `src/engines/gpt_sovits_adapter.py`, `src/engines/adapter/*` | GPT-SoVITS execution request | Runtime command/result | GPT-SoVITS engine and adapter | Runtime adapter, configured runtime assets and CLI | Runtime unavailable, invalid command/assets, CLI execution failure, output missing/invalid. |
| Controlled smoke | `src/services/controlled_runtime_smoke_test_service.py`, related tests | Controlled evaluation input | Evidence/report only | Controlled smoke service | Controlled runner/profile | Controlled/calibration success is not a production execution readiness upgrade. |
| Legacy service | `src/services/generate_service.py`, `generate_pipeline_service.py` | Legacy `GenerateRequest`, UI state/voice/project | Legacy pipeline result/output | Legacy Generate service | Legacy engine manager/merge service | Not the immutable Session contract; mock tests must not establish production readiness. |

## 4. Runtime Flow and State Ownership

### 4.1 Planning flow

1. UI foundation controls or Local API submit a request to `GenerateSessionService`.
2. Service validates immutable identity fields, source and output policy.
3. Service snapshots source rather than modifying original TXT/DOCX/input.
4. Text is normalized and structured into chapters/units.
5. A plan is frozen only after reconstruction verification; frozen semantic content cannot be changed through resume/retry.
6. Planned artifact records are persisted with immutable lineage.
7. The result is a Session ready for inspection/planned execution, not an audio success.

**Planning owner:** `GenerateSessionService`.  
**Persistence owner:** `GenerateRepository`.  
**Planning capability:** `READY` for supported validation/session/plan contracts, subject to input validation.

### 4.2 Unit execution flow

1. API execution endpoint checks runtime readiness before enqueueing, rather than invoking engine synchronously.
2. A `generate_unit` job carries persisted immutable identity context.
3. Job Runner evaluates the registered GPU `ResourceRequirement`; implicit CPU fallback is disabled.
4. `GenerateUnitJobWorker` calls the Session service execution method.
5. Session service creates/updates Attempt state and reserves the planned Artifact.
6. `GPTSoVITSGenerateProvider` resolves persisted context and production reference binding.
7. Provider invokes `EngineManager`, which delegates to GPT-SoVITS Engine/Adapter/Runtime.
8. Runtime is expected to produce a managed temporary output.
9. Artifact service validates the temporary WAV and promotes it only if reservation, output path, validation and lineage gates pass.
10. Only then are Attempt and Unit marked completed with a valid Artifact; Job state alone is insufficient proof.

**Execution owner:** Job Worker + `GenerateSessionService`.  
**Engine owner:** Engine Manager / Engine / Adapter / Runtime.  
**Artifact success owner:** Artifact lifecycle service plus persisted Session state.

### 4.3 Resume and retry flow

- Inspect operations read frozen persisted state and return an inspection fingerprint.
- Execution requires the caller to supply the expected fingerprint, preventing stale action.
- Resume/retry do not normalize, detect chapters, split, change frozen settings, change selection or change Unit ID.
- Retry creates a new Attempt under the existing Unit contract.
- If provider/runtime is unavailable, action returns truthful `UNAVAILABLE`; it must not synthesize a fake artifact or mark the Unit complete.

## 5. Dependency Graph

```text
Generate UI/API
  ├─> GenerateSessionService
  │     ├─> Generate request validation
  │     ├─> Generate text/source/structure services
  │     ├─> GenerateRepository
  │     ├─> GenerateArtifactService
  │     └─> (execution only) GPTSoVITSGenerateProvider
  │             ├─> ProductionReferenceBindingService
  │             ├─> ProductionReferenceBindingSnapshotService
  │             ├─> Voice/Reference persistence
  │             └─> EngineManager
  │                   └─> GPTSoVITSEngine
  │                         └─> GPTSoVITSAdapter
  │                               └─> Runtime / inference_cli.py
  │
  ├─> RuntimeProfileService / Runtime Doctor
  │     └─> runtime profile, assets, command environment, FFmpeg/FFprobe gates
  │
  └─> JobQueueService
        ├─> JobRepository / JobLogService
        ├─> JobHandlerRegistry
        │     ├─> GeneratePrepareJobWorker
        │     └─> GenerateUnitJobWorker
        └─> Resource Manager / GPU lease policy
```

External/environmental dependencies:

- Valid selected runtime profile and discovery evidence.
- Required GPT-SoVITS runtime command/script and compatible assets.
- Valid persisted Voice, selected model and production reference binding.
- A compatible language route. Vietnamese must remain blocked where GPT-SoVITS does not have a validated Vietnamese cleaner/phoneme/inference contract.
- GPU/resource telemetry and lease policy for Unit execution.
- Managed writable session workspace and collision-free final artifact destination.
- Valid WAV output for the currently implemented artifact promotion path.
- FFmpeg/FFprobe where Runtime Doctor/output processing requires them.

## 6. Current Capability Matrix

| Capability | Current status | Evidence / boundary |
| --- | --- | --- |
| Generate request validation | `READY` | Session service and API/UI validation path exist; failures are reported as issues. |
| Source snapshot and original-file preservation | `READY` | Source is read and materialized in session workspace; foundation tests cover source immutability. |
| Normalize, chapter/unit planning and frozen plan | `READY` | Immutable checksums and reconstruction guard are implemented and tested. |
| Session/plan/unit/attempt/artifact persistence | `READY` | Repository persists session state under managed workspace with registry and atomic write strategy. |
| Artifact reservation and basic WAV validation | `READY` | Reservation, temp-to-final promotion and `wave`-based validation are implemented; only basic WAV validation is claimed. |
| Generate prepare Job | `READY` | Registered CPU-light plan-only worker; does not call engine or produce audio. |
| Local API read/planning endpoints | `READY` | Session/plan/unit/attempt/artifact/manifest/inspection endpoints are present with safe path presentation. |
| Runtime Doctor reporting | `READY` as reporting contract | It reports actual profile gate status; this does **not** mean current local runtime is ready. |
| Production Generate Unit Job path | `DEGRADED` | Worker, GPU requirement, provider and engine route exist, but execution remains conditional on real runtime/resource/binding gates and lacks real production E2E evidence in this inventory. |
| GPT-SoVITS provider binding path | `DEGRADED` | Production binding and provider classes exist; compatibility and real runtime validation remain gates. |
| Real GPT-SoVITS inference | `UNAVAILABLE` unless all runtime gates pass; not verified `READY` | No real production execution proof is established by controlled/mock tests or source inspection. |
| Preview Audio | `UNAVAILABLE` | No production preview result consumer/validated preview execution is evidenced. |
| Validated WAV output in production | `DEGRADED` | Lifecycle/validation path exists; no real production runtime smoke proves output capability. |
| MP3 output through Session pipeline | `UNAVAILABLE` | Foundation documentation explicitly notes MP3 is not wired in this path; legacy pipeline tests do not upgrade it. |
| Full audio quality validation/listening review | `UNAVAILABLE` | Basic WAV readability is not acoustic/quality validation; no real listening acceptance evidence. |
| Resume/retry inspection | `READY` | Frozen-state inspection and fingerprint protection are implemented. |
| Resume/retry production execution | `DEGRADED` | Orchestration exists but requires the same real runtime/provider/resource evidence as Unit execution. |
| Session pipeline UI execution and result lifecycle | `DEGRADED` | Foundation UI can validate/create/inspect only; it does not enqueue/monitor/consume Session Unit execution. |
| Legacy UI direct Generate | `LEGACY / not readiness evidence` | It remains callable from `AudioPage`; it is outside the immutable Session pipeline and must not be treated as AVS-015 completion. |
| Mock/controlled provider execution | `TEST_ONLY` | Tests write controlled valid WAV output; this proves orchestration behavior only, never production capability. |
| Vietnamese GPT-SoVITS Generate | `BLOCKED` until validated runtime contract exists | Project rule forbids mapping `vi` to another language token to bypass compatibility gate. |

## 7. Mock, Test-only and TODO Boundaries

### Mock / test-only

- `tests/test_generate_pipeline.py` uses `MockEngineManager` and `MockMergeService`; it writes test bytes and validates legacy orchestration only.
- `tests/test_generate_pipeline_foundation.py` injects a provider that writes a controlled valid WAV for artifact lifecycle tests.
- Controlled runtime smoke/calibration services and tests are evidence mechanisms; they are not production Generate execution.
- Any successful test provider result does not change production readiness, runtime status or UI claim.

### Missing or incomplete production capability

1. **Single production UI path:** the visible Audio Page must not continue treating legacy direct execution and Session planning as if they were one completed workflow.
2. **Session UI execution orchestration:** Session UI does not presently enqueue Unit Jobs, render queue state, show blocked/runtime evidence, or surface validated Artifact results.
3. **Verified real runtime integration:** valid GPT-SoVITS assets, CLI contract, environment and a real output smoke are required before a production readiness promotion.
4. **Production artifact acceptance evidence:** temp output and process exit are not sufficient; a real artifact needs validation, lineage and persisted state.
5. **MP3 integration:** Session artifact lifecycle is WAV-oriented; MP3 output is not implemented/validated in the Session path.
6. **Preview workflow:** no independent production preview capability is evidenced.
7. **Audio quality gate:** basic container validation does not validate audible quality, speaker/reference correctness, language intelligibility or user acceptance.
8. **Vietnamese language compatibility:** remains blocked until a genuine GPT-SoVITS Vietnamese frontend/inference contract is integrated and validated.

## 8. Architecture Findings Requiring Decision

### A. Parallel UI execution paths

**Issue:** `AudioPage` owns both legacy direct Generate actions and Session foundation actions. The legacy actions call `GenerateService` directly; foundation controls create and inspect Session data but do not execute it.

**Impact:** Users and maintainers can observe different lifecycle semantics, cancellation/progress models, output handling and capability signals depending on which UI control is used. The standard required flow (`UI -> Page/Controller -> Service -> Job Queue -> Engine Manager -> Adapter -> Runtime`) is not uniformly represented by the legacy path.

**Recommendation:** Before connecting the Session workflow to user-facing execution, decide whether future UI work will:
- migrate the existing user-facing Generate action to Session/Job orchestration, then retire legacy execution through an explicit migration plan; or
- retain legacy Generate as a separately labeled compatibility workflow with explicit capability boundaries.

This is an architecture/workflow decision. It is intentionally not implemented in this inventory Sprint.

### B. Two queue systems with distinct contracts

**Issue:** Legacy `AppContext.queue_service` / `QueueWorker` and persisted Job Queue/Runner both participate in Generate-related work.

**Impact:** Job identity, recovery, resource leases, cancellation and artifact success semantics can diverge.

**Recommendation:** Define an approved convergence/compatibility strategy before changing UI routing. Do not silently replace one queue with the other.

### C. Production readiness must remain evidence-driven

**Issue:** Source contains a production provider path and controlled runtime smoke infrastructure, but source presence and controlled test success cannot establish a usable local production runtime.

**Impact:** Reporting `READY` early would violate capability truth and can cause false user expectations or artifact risk.

**Recommendation:** Retain `DEGRADED`/`UNAVAILABLE` until an approved controlled real-runtime smoke policy, real asset/profile validation, output validation and manual listening acceptance are complete.

## 9. Recommended Sprint Breakdown

The sequence below is a recommendation only; it does not open or modify a Sprint.

### Sprint A — Contract and UX decision gate

- Approve the authoritative user-facing Generate workflow: Session/Job pipeline, legacy compatibility pipeline, or formally staged migration.
- Define which UI action becomes the Session pipeline entrypoint.
- Define success presentation at Job, Unit and Artifact levels.
- Define explicit migration/deprecation policy for legacy queue/output behavior.

**Exit criteria:** architecture decision is recorded; no implicit UI reroute.

### Sprint B — Session pipeline UI orchestration

- Wire approved UI controller/page actions to Session validation, creation and `generate_prepare`/`generate_unit` Jobs only through services.
- Render queued/running/blocked/failed/completed Unit and Job state with immutable IDs/correlation guards.
- Surface runtime/resource/language blockers in Vietnamese.
- Render only validated Artifact completion; do not equate Job completion with audio success.

**Exit criteria:** UI is responsive, no direct engine/runtime call, no duplicate execution, and production blockers are visible.

### Sprint C — Runtime integration validation

- Validate the selected GPT-SoVITS runtime profile, CLI contract, assets, environment, GPU policy and resource telemetry on controlled fixtures.
- Execute an approved real runtime smoke with managed temporary data only.
- Keep Vietnamese blocked unless the actual compatible language frontend/inference contract has passed validation.
- Persist traceable evidence without exposing secrets or unsafe local paths.

**Exit criteria:** runtime readiness can be reported from real evidence, not mock/controlled-provider results alone.

### Sprint D — Artifact/output completion

- Complete approved real WAV output validation and lineage evidence.
- Design and implement MP3 conversion only when output policy, FFmpeg dependency, temp/final promotion and validation contracts are approved.
- Add preview only as an independently gated capability.
- Add acoustic/manual listening acceptance criteria.

**Exit criteria:** each output capability has its own truthful readiness state and no silent overwrite path.

### Sprint E — Legacy convergence

- Implement only the approved migration/compatibility decision from Sprint A.
- Preserve immutable IDs and frozen lineage.
- Remove or retain legacy code only through a separately approved change; do not refactor it opportunistically.

**Exit criteria:** one clearly documented user-facing workflow, or explicitly supported separate workflows with non-overlapping claims.

## 10. Evidence Reviewed

### Primary source

- `src/pages/audio_page.py`
- `src/services/generate_session_service.py`
- `src/services/generate_pipeline_service.py`
- `src/services/generate_service.py`
- `src/services/gpt_sovits_generate_provider.py`
- `src/services/production_reference_binding_service.py`
- `src/services/production_reference_binding_snapshot_service.py`
- `src/services/runtime_profile_service.py`
- `src/services/local_api_service.py`
- `src/services/job_worker.py`
- `src/core/app_context.py`
- `src/core/engine_manager.py`
- `src/engines/gpt_sovits_engine.py`
- `src/engines/gpt_sovits_adapter.py`
- `src/engines/adapter/base_adapter.py`
- `src/engines/adapter/runtime.py`
- Generate models/repository/artifact and Job/Resource dependencies reached by these call paths.

### Tests

- `tests/test_generate_pipeline.py`
- `tests/test_generate_pipeline_foundation.py`
- `tests/test_generate_architecture.py`
- `tests/test_generate_runtime_validation.py`
- `tests/test_avs01424_production_consumer_integration.py`
- `tests/test_avs01424_controlled_runtime_smoke_test.py`
- `tests/test_production_reference_binding_service.py`

### Existing technical documents

- `docs/GENERATE_PIPELINE_FOUNDATION.md`
- `docs/Architecture.md`
- current project status, roadmap, sprint and change log documents read at task start.

## 11. Non-goals and Data Safety

This Sprint inventory did not:

- generate audio;
- call inference, training, fine-tune or publish;
- alter source/runtime/UI/pipeline architecture;
- modify project, workspace, voice, output, backup, export, Reference Vault or user dataset data;
- create fake production audio, model, checkpoint or Artifact;
- execute Git write operations.

The inventory intentionally distinguishes `READY`, `DEGRADED`, `UNAVAILABLE`, `BLOCKED`, `TEST_ONLY`, and legacy compatibility boundaries. A Job success, command exit code, file existence, mock provider success or runtime discovery is not represented as a valid production Artifact or production-ready Generate capability.