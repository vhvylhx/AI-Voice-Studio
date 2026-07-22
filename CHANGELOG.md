# Changelog
## AVS-016 Sprint 8: Round01 Deep Review Integration & Round02

### Added

- Added Sprint 8 reference manifest adjustment from Round01 deep review evidence.
- Added preflight integrity for reference transcript plausibility: chars/s, syllables/s and preview/reference duration ratio.
- Added preview-input transcript normalization with source text provenance and normalized text checksum.
- Added pair manifest audit fields for conditioning reference, benchmark voice/profile, model revision, seed, inference parameters and AI/Benchmark comparison reason.
- Added boundary-fragment/ellipsis flags and scoring penalty in Reference Selection.
- Added subset preview generation support so unaffected Round02 previews can carry forward while affected pairs regenerate only.

### Validation

- `pair_002` old reference `000070_005_002` removed due 5.8s reference vs 233-char transcript outlier.
- Replacement candidate: `000015_022_001` from Top50.
- Round02 output: `cache/avs016_sprint6_preview_generation_voice_0001/Round02/`, status READY, 20 Pair / 40 WAV.
- Regenerated affected pairs: `pair_002`, `pair_005`, `pair_010`, `pair_012`, `pair_017`; 30 previews carried forward with audit.

### Notes

- No Train, LoRA, Runtime Binding, Production Inference, commit or push was performed.
- Ranking/review evidence is not human approval for Training.
## AVS-016 Sprint 4: Reference Selection Engine

### Added

- Added `ReferenceSelectionService` for metadata-list authority scanning instead of using candidate cache as authority.
- Added alignment manifest/report and dataset-health evidence filtering for duplicate, suspicious, invalid, AI-generated, music-heavy and multi-speaker clips.
- Added quality ranking with audio metrics, transcript quality, pitch distribution and AVS-014.24 calibration-aware weighting.
- Added Top50 ranking and diversified frozen Top20 selection by source/chapter coverage.
- Added `evaluation_holdout_manifest.json` with `exclude_from_future_training=true` for frozen holdout references.
- Added regression coverage in `tests/test_reference_selection_service.py` for authority scan, filtering, ranking, diversification, frozen Top20 and holdout manifest output.

### Notes

- This is a Reference Selection Engine foundation. It does not bind production Generate/Engine/Runtime and does not change production inference readiness.
- No implementation or test changes were made during documentation recovery.
## AVS-016 Sprint 3: Voice Preview Generation

### Added

- Added isolated diagnostic preview orchestration to `VoicePreviewBenchmarkService` for versioned `Round01`, `Round02`, ... output.
- Each valid benchmark Pair receives `same_preview_v1.wav` and `new_preview_v1.wav` through an explicitly injected diagnostic generator; no source-audio copy or post-processing is performed by the service.
- Added fail-closed WAV validation: parseable PCM16, mono, runtime sample rate, positive duration, and non-silent samples.
- Added manifest evidence only after successful validation: preview path, SHA-256 checksum, duration, generation timestamp, runtime profile, and generation status.
- Added regression coverage for 20 same previews, 20 new previews, round versioning, no-overwrite, manifest update, and invalid WAV rejection.

### Notes

- This is an isolated diagnostic benchmark foundation only. It does not bind Production Generate, Engine, Adapter, or Runtime and does not change production readiness.
- No training, fine-tuning, preprocessing, inference-algorithm change, scoring, similarity metric, blind review, UI review, auto approval, commit, or push was performed.
- A real 40-preview Round was not run: no approved frozen benchmark manifest exists for exactly 20 immutable reference Pairs and their benchmark transcripts. The service remains fail-closed and does not infer or substitute benchmark inputs.
- `ROADMAP.md` currently identifies Voice Preview under a different Sprint code; the historical roadmap identifier was not changed without explicit approval.

## AVS-014.24 Sprint C5: Production Binding Foundation

### Added

- Added `ProductionReferenceBindingService` as the sole Service-level resolution path for an approved production reference winner.
- Added fail-closed readiness gates requiring `READY` Reference Selection, Generalization, and Production Readiness before a `ProductionReferenceWinnerBinding` is returned.
- Added validation for registered consumers, direct-artifact-access bypass attempts, winner/available-variant consistency, artifact integrity, and immutable winner identity.
- Added regression tests for all readiness gates, invalid/missing winners, inconsistent artifacts, and consumer bypass rejection.

### Notes

- C5 does not bind a Generate, Engine, Adapter, Runtime, or other production consumer.
- No production inference, WAV/MP3 generation, preview, publish, training, fine-tune, commit, or push was performed.
- Existing production generation behavior and Generate/WAV/MP3 readiness remain unchanged.

## AVS-014.24 Sprint C2.5: Reference Selection Manual Review Workflow

### Added

- Hoan thien diagnostic Reference Selection review artifact voi `reviewer`, `review_date` va `notes`.
- Review chi `REVIEW_COMPLETED` khi `review_completed=true`, co dung mot `winner_reference_variant` ton tai trong `available_reference_variants`.
- Loader fail-closed voi `ReferenceSelectionPendingError` cho review pending hoac invalid.
- Them regression coverage cho completed-status literal, metadata bat buoc, winner null/khong ton tai/ngoai available variants va multiple winners.

### Notes

- Khong production Voice binding, production inference, training, fine-tune, WAV/MP3 artifact, commit hay push.
- Manual-review utility READY; production readiness khong thay doi.

## AVS-014.23: GPT-SoVITS Voice 0001 Training Readiness

### Added

- Added a fresh AVS-014.23 preprocessing readiness plan artifact under `cache/training/voice_0001/gpt_sovits/`.
- Added a fresh validation-only train report under `cache/train_validation/avs01423_validation_only_0001/`.

### Validation

- Resolved Voice `0001` through the current Voice service contract without using display name as identity.
- Verified final training metadata `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`: 2329 rows, 2329 unique WAV files, 13232.40 seconds, all language `vi`, no duplicate path, no missing WAV, no empty transcript.
- Audited local GPT-SoVITS v2Pro source: `prepare_datasets/1-get-text.py`, `text/cleaner.py`, `s1_train.py`, `s2_train.py`, `s1longer.yaml`, `s2v2Pro.json`.
- Confirmed current upstream preprocessing supports `en`, `ja`, `jp`, `ko`, `yue`, `zh`, not `vi`.
- Confirmed machine baseline for audit: available RAM above 10 GB, disk F above 60 GB, Quadro P1000 free VRAM above 3 GB, no GPU compute process.
- `TrainingService.prepare_train(validation_only=True)` returned `validation_failed` with `preprocessing_not_ready`.

### Notes

- No preprocessing stage, SoVITS train, GPT train, checkpoint creation, canary generation, production Generate, Publish, commit or push was performed.
- Full GPT-SoVITS Training remains `BLOCKED_PENDING_USER_APPROVAL` and technically blocked by Vietnamese frontend compatibility.
- Status: `GPT_SOVITS_TRAINING_READINESS_BLOCKED`.

## AVS-014.22 Update: VieNeu Codec Import & Safe CPU Canary

### Added

- Added codec selection and low-resource safety profile contracts for VieNeu diagnostics.
- Added codec completeness and RAM threshold helpers.
- Added tests for codec contract, partial/size-mismatch codec readiness and low-resource RAM decisions.
- Added manual listening package for `vieneu_cpu_canary_20260719_012122`.

### Changed

- VieNeu canary gate now tracks model and codec separately.
- Documentation now records technical canary PASS while keeping production integration BLOCKED pending manual review.

### Validation

- Audited `vieneu==3.2.3` source contract for codec repo, required files, loader path, ONNX providers and sample rate.
- Verified codec repo `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX`, immutable commit `ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae`, license `apache-2.0`.
- Downloaded/promoted 7 codec files atomically under `cache/engines/vieneu_tts/75ff82a/codecs/`.
- Validated codec ONNX files load with `CPUExecutionProvider`.
- Offline resolution test PASS with local model/codec paths and blocked implicit Hugging Face fetch.
- Resource preflight PASS: available RAM above 8 GB and no GPU compute process.
- Safe CPU canary PASS with three real WAV outputs in diagnostics, 48 kHz mono pcm_s16le.

### Notes

- No Train, production Generate, Publish, production Voice binding, GPU use, commit or push was performed.
- A first diagnostic attempt `vieneu_cpu_canary_20260719_011817` is superseded because PowerShell codepage corrupted Vietnamese input text; final PASS run is `vieneu_cpu_canary_20260719_012122`.

## AVS-014.22 Update: Fix Hugging Face SSL Gate Safely

### Added

- Added `truststore==0.10.4` to the isolated VieNeu runtime install plan so Hugging Face HTTPS can use the Windows certificate trust bridge without disabling SSL verification.
- Added managed model manifest for the downloaded VieNeu model files.

### Changed

- SSL gate now uses a verified `truststore` SSL context for Hugging Face metadata/download calls instead of relying on the isolated runtime certifi bundle.

### Validation

- Confirmed system time: `2026-07-19T01:02:33+07:00`.
- Confirmed isolated runtime OpenSSL: `OpenSSL 3.0.16 11 Feb 2025`.
- Confirmed certifi: `2026.6.17`, path inside isolated runtime.
- Confirmed Python/certifi HTTPS failed with `CERTIFICATE_VERIFY_FAILED`.
- Confirmed Python/truststore HTTPS passed for `https://huggingface.co`.
- Resolved `pnnbao-ump/VieNeu-TTS-v3-Turbo` revision `75ff82a` to immutable commit `75ff82a72f54d55ed389e1eeb12041d3c4bac7d4`.
- Verified model license metadata: `apache-2.0`.
- Downloaded and atomically promoted 11 required VieNeu model files, total expected size `236470190` bytes.

### Notes

- No `verify=False`, `--trusted-host`, `HF_HUB_DISABLE_SSL_VERIFY`, `CURL_CA_BUNDLE=""`, global Windows certificate store change, Train, production Generate, canary WAV, commit or push was performed.
- VieNeu package source also requires the MOSS ONNX codec repo for inference; this update did not download that separate dependency without explicit scope.

## AVS-014.22 Update: VieNeu Isolated CPU Runtime with CPU Torch Frontend

### Added

- Added runtime manifest contract for isolated VieNeu CPU runtime.
- Added CPU-only runtime policy helpers for torch CUDA, ONNX providers and forbidden GPU package checks.
- Added experimental canary-only adapter capability report; it is not registered as a production provider.
- Added tests for CPU-only torch install plan, GPU hard block, CPU runtime manifest and canary-only adapter scope.

### Changed

- Corrected VieNeu source contract to `CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND`.
- Replaced the old absolute blocker `cpu_onnx_ref_audio_requires_torchaudio_frontend_in_vieneu_3_2_3` with requirement `cpu_torch_frontend_required_for_fresh_reference_enrollment`.
- The managed install plan now uses CPU-only `torch==2.8.0` and `torchaudio==2.8.0` from the PyTorch CPU index and blocks GPU runtime requests.

### Validation

- Created isolated runtime under `cache/engines/vieneu_tts/75ff82a/runtime/.venv/`.
- Installed `torch==2.8.0+cpu`, `torchaudio==2.8.0+cpu`, `onnxruntime==1.27.0`, `vieneu==3.2.3`.
- Verified `torch.cuda.is_available()==False` and ONNX providers do not include `CUDAExecutionProvider`.
- Reference Thu Minh Voice 0001 candidate validates as 6.50s, mono, pcm_s16le, 32000 Hz; VieNeu canary requires diagnostics resample copy.
- Hugging Face model revision/license/file validation is BLOCKED by SSL `CERTIFICATE_VERIFY_FAILED`; no model download or WAV canary was executed.

### Notes

- No Train, production Generate, Publish, GPT-SoVITS runtime modification, commit or push was performed.
- Production Vietnamese engine integration and real Generate remain BLOCKED until model validation/download and CPU canary WAV pass.

## AVS-014.22: VieNeu-TTS Controlled Import & Vietnamese Local Canary Gate

### Added

- Added controlled VieNeu-TTS import/canary contracts and service for a single locked candidate: `pnnbao-ump/VieNeu-TTS-v3-Turbo`, package `vieneu==3.2.3`.
- Added managed target plan under `cache/engines/vieneu_tts/<revision>/` and diagnostics output under `diagnostics/vietnamese_engine_evaluation/<run_id>/`.
- Added reference validation for the Thu Minh Voice 0001 canary candidate without editing source audio/text.
- Added blocked canary report generation that does not unlock production readiness.
- Added tests for managed cache path, explicit download gate, CPU/ONNX cloning blocker, reference validation, blocked readiness effect and diagnostics report write safety.
- Added source-level contract audit for `vieneu==3.2.3` CPU/ONNX `ref_audio` behavior.
- Added regression tests proving the old GPU-required blocker is removed while strict torch-free fresh reference cloning remains blocked.

### Changed

- Updated Vietnamese engine static download plan target from `models/vietnamese/...` to `cache/engines/vieneu_tts/<revision>/`.
- Corrected VieNeu local canary gate: CPU/ONNX `ref_audio` is supported and GPU is not required, but `vieneu==3.2.3` fresh reference enrollment imports `torch` through the speaker fbank frontend, so strict torch-free canary is still blocked.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: passed.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_avs01422_vieneu_controlled_import.py tests\test_avs01421_vietnamese_engine_evaluation.py -q`: 31 passed.

### Notes

- No VieNeu package/model download was performed.
- No Train, Generate, Publish, Real Smoke or GPT-SoVITS runtime modification was performed.
- VieNeu package wheel `vieneu==3.2.3` was downloaded into `cache/audit/vieneu_3_2_3/` for source audit only; no model was downloaded.
- Local canary is BLOCKED in the strict CPU/ONNX torch-free profile because fresh `ref_audio` enrollment imports `torch` via `speaker/onnx_extractor.py` and `speaker/fbank.py`.
- Production Vietnamese engine integration and Generate readiness remain BLOCKED until a local model, explicit runtime profile and local canary/Real Smoke PASS exist.

## AVS-014.21: Vietnamese Engine Evaluation & Language Selection

### Added

- Added real Voice language checkbox UI for `vi`, `zh`, `en`, `ja`, `ko`, `yue` with `Tat ca` scope behavior and per-language readiness labels.
- Added empty-language guard in VoiceService while keeping legacy Voice migration default to `vi`.
- Added Generate language mode foundation: auto detect, fixed language and multilingual route preview.
- Added VietnameseEngineEvaluationService and evaluation records for VieNeu-TTS, F5-TTS Vietnamese and viXTTS.
- Added license audit, download plan, low-resource safety profile, local canary plan and static scorecard contracts.
- Added Local API endpoints for Vietnamese engine evaluation, download plans and low-resource profile.
- Added AVS-014.21 tests for UI language behavior, routing preview, license/download/canary gates, API endpoints and no-readiness-unlock rules.

### Changed

- Voice Detail now saves language selection by `voice_id`, not display name/folder name.
- Generate Options Panel now carries selected language into GenerateSelectionConfig foundation payload.
- VieNeu-TTS is documented as the primary Vietnamese candidate proposal; F5-TTS Vietnamese and viXTTS remain non-default due license/review blockers.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: passed.
- Targeted pytest for AVS-014.21 and language/API foundation: 41 passed.

### Notes

- No Train, Generate, Real Smoke, model download or GPT-SoVITS upstream modification was performed.
- Vietnamese production integration remains BLOCKED until local model, user-approved download/import and local canary/Real Smoke PASS exist.
- Generate production readiness was not raised.

## AVS-014.20: Multi-Engine Language Capability & Routing Foundation

### Added

- Added Language Catalog foundation for `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- Added migration-safe Voice language fields: `default_language`, `preferred_language`, `language_selection_mode`, `enabled_languages` and `engine_bindings`.
- Added heuristic LanguageDetectionService and mixed-language segment planning foundation.
- Added EngineCapabilityRouter with per-language readiness, blockers and fingerprint isolation.
- Added Generate Unit language route snapshot fields for future production routing.
- Added Local API foundation endpoints for languages, language detection, language plan, enabled languages, engine bindings and voice language capabilities.
- Added tests for catalog, migration, all checkbox behavior, Vietnamese no-fallback, GPT-SoVITS mapping, detection, router, fingerprint, API and frozen Generate route fields.

### Changed

- Voice Catalog now exposes safe enabled-language metadata and language capabilities URL.
- StyleProfile compatibility now includes supported/preferred/unsupported languages and language-specific instructions.
- Voice Detail UI shows enabled language foundation fields.

### Validation

- Targeted AVS-014.20 tests passed.

### Notes

- No Train, Generate, Real Smoke, model download or GPT-SoVITS upstream modification was performed.
- Vietnamese Engine remains `BLOCKED_PENDING_ENGINE_SELECTION`.
- GPT-SoVITS Multilingual remains `BLOCKED_PENDING_TRAINED_ASSETS_AND_SMOKE`.
- Real Generate remains `BLOCKED`.

## AVS-014.19A1: Vietnamese Text Frontend Compatibility

### Validation

- Audited real GPT-SoVITS v2Pro runtime language path: `prepare_datasets/1-get-text.py`, `text/cleaner.py`, `text/symbols*.py`, GPT `AR/data/dataset.py` and inference language handling.
- Confirmed current runtime supports preprocessing/inference language contracts for zh/ja/en/ko/yue style paths, not `vi`.
- Kept preprocessing blocked by `PREPROCESS_CONFIG_INVALID`; no fake `vi` alias and no canary preprocessing was run.

### Notes

- No Train, Generate, Publish, Real Smoke or upstream GPT-SoVITS modification was performed.
- Status: VI_UNSUPPORTED_BY_CURRENT_RUNTIME until a real Vietnamese frontend/runtime patch is supplied.

## AVS-014.19A: GPT-SoVITS Dataset Preprocessing Pipeline

### Added

- Added preprocessing run/plan/stage domain model for GPT-SoVITS training artifacts.
- Added TrainingPreprocessingService with run-owned cache output, frozen plan fingerprint, normalized metadata copy, subprocess command construction, stdout/stderr logs, artifact validation, resource lease support and manifest generation.
- Added TrainingConfig `preprocessing_manifest_path` and TrainingService read-only gate for preprocessing manifest READY/BLOCKED/STALE/MISSING.
- Added RuntimeProfileService detection for GPT-SoVITS v2Pro speaker-vector preprocessing script `2-get-sv.py`.
- Added preprocessing tests for voice_id/run-owned output, metadata fingerprint, unsupported language gate, duplicate metadata, mock stage artifacts, training manifest gate, stale state, missing scripts and CUDA OOM failure code.

### Validation

- Real pre-flight for Voice `0001` / metadata `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`: dataset validation passed with 2329 clips and 13232.40 seconds.
- Real runtime script audit found upstream `1-get-text.py` supports only en/ja/jp/ko/yue/zh language keys for preprocessing; metadata language is `vi`.
- Real preprocessing was not started because `PREPROCESS_CONFIG_INVALID` blocks before artifact generation.

### Notes

- No Train, Generate, Publish or Real Smoke was run.
- No GPT-SoVITS upstream file was modified.
- No production Voice/checkpoint/reference file was edited.
- Preprocessing status is `PREPROCESSING_BLOCKED` until a GPT-SoVITS runtime/script with valid Vietnamese text cleaner/phoneme support is selected or explicitly provided.

## AVS-014.18: Voice Publish Automation & Post-Training Style Variants

### Added

- VoiceConfig `display_name` va publish metadata migration-safe.
- VoiceService resolver theo `voice_id` va `rename_display_name()` khong rename folder.
- VoicePublishService de validate/discover/publish existing GPT/SoVITS/reference assets vao Voice khi co explicit confirmation.
- StyleProfile schema cho post-training style profile: intended use, classification, parameters, prompt instructions, reference requirements, compatibility, readiness, blockers va warnings.
- Variant binding service voi Style Profile theo huong generate profile, khong tao model/checkpoint rieng.
- Local API routes cho Voice display rename va Voice publish validation/publish/discovery.
- Tests AVS-014.18 cho identity, rename safety, legacy folder, publish confirmation, checkpoint discovery, fingerprint, style profile, variant binding va API.

### Changed

- Voice Catalog hien `display_name` theo config va giu `folder_name` de tuong thich legacy.
- Audio/Voice UI hien display name nhung van giu folder name cho path legacy.
- Generate Runtime Validation resolve Voice qua `voice_id` khi service ho tro resolver.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: dat.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_avs01418_voice_publish.py -q`: 9 passed.
- Targeted pytest Voice/Style/API/Runtime validation: 42 passed.

### Notes

- Khong Train that.
- Khong Generate that.
- Khong chay Real GPT-SoVITS Smoke.
- Khong sua GPT-SoVITS runtime hoac du lieu that trong `voices/`, `projects/`, `workspace/`, `outputs`.
- Generate production readiness van khong READY neu chua publish assets hop le va chua co Real Smoke PASS.

## AVS-014.17B: Runtime Validation & Real Smoke Guard

### Added

- Generate Runtime Validation Service tach 3 lop readiness: Environment, Selected Voice/Variant/Reference assets va Real Inference verification.
- Fingerprint cho Real GPT-SoVITS Smoke dua tren Runtime Profile, inference CLI, Voice, Variant va model/reference asset snapshot.
- Stale smoke handling: smoke report khong khop fingerprint hoac output WAV khong hop le se khong mo production readiness.
- Tests cho environment-only false-positive, missing selection, matching fingerprint PASS, stale smoke va Local API readiness.

### Changed

- Local API `/api/v1/generate/runtime/doctor` tra ve 3 lop readiness va van giu top-level `doctor_status/profile/report/guidance` de tuong thich.
- Local API `/api/v1/generate/readiness` khong con bao `generate_execution`/`wav_output` READY khi chi co Runtime Doctor READY.
- Endpoint enqueue Generate Unit production bi chan theo capability `generate_execution`, khong chi theo environment doctor.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: dat.
- Targeted pytest: `tests\test_generate_runtime_validation.py`, `tests\test_generate_pipeline_foundation.py`, `tests\test_runtime_profile.py`: 26 passed.
- Full pytest: 176 passed.
- Bootstrap: target main_application, limited mode dung voi capability blocked.
- API smoke Generate readiness: Environment READY, Selected Assets BLOCKED, Real Inference BLOCKED, `generate_execution` BLOCKED.

### Notes

- Khong Train that.
- Khong Generate that.
- Real GPT-SoVITS Smoke chua chay vi Voice Thu Minh `0001` thieu `gpt_model`, `sovits_model`, `reference_audio`, `reference_text` va chua co explicit enable.
- Real Smoke end-to-end voi Voice Thu Minh `0001` / Variant `default` da dung o asset gate; khong tao Session/Job inference, khong goi runtime va khong nang readiness.

## AVS-014.17: GPT-SoVITS Runtime Integration for Generate

### Added

- Runtime Doctor cho Generate dựa trên Runtime Profile hiện tại: kiểm tra runtime root, Python runtime, torch, faster-whisper, GPT-SoVITS scripts, pretrained models, FFmpeg và FFprobe.
- Local API endpoint `GET /api/v1/generate/runtime/doctor`.
- Production provider `GPTSoVITSGenerateProvider` nối Generate Session/Unit với EngineManager và GPT-SoVITS Engine/Adapter.
- Job Queue worker `generate_unit` với ResourceRequirement GPU, không CPU fallback mặc định.
- Local API endpoint `POST /api/v1/generate/sessions/{session_id}/units/{unit_id}/execute` để enqueue Generate Unit qua Job Queue.
- Failure hardening cho `GenerateSessionService.execute_unit_with_provider()`: provider/engine lỗi sẽ ghi attempt, unit và artifact thành `failed` để Retry/Resume không kẹt state.
- Timeout subprocess cho `GPTSoVITSAdapter.generate()` mặc định 3600 giây.

### Changed

- Generate readiness không còn báo thiếu production handler tuyệt đối; trạng thái hiện là runtime-gated: READY chỉ khi Runtime Doctor đạt và Voice model hợp lệ.
- Capability table chuyển Generate execution/WAV output sang DEGRADED khi có handler nhưng chưa có runtime/voice/smoke test đạt.
- Runtime Profile detection tách `inference_cli.py` khỏi `inference_webui.py`; Generate production chỉ chạy khi CLI script xác minh tồn tại.

### Validation

- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m compileall src tests`: đạt.
- `F:\AI-Voice-Studio\.venv\Scripts\python.exe -m pytest tests\test_generate_pipeline_foundation.py tests\test_runtime_profile.py tests\test_local_api.py`: 29 passed.

### Notes

- Không Train thật.
- Không Generate thật trong validation mặc định.
- Không sửa GPT-SoVITS runtime.
- MP3 production qua Generate foundation vẫn UNAVAILABLE.

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

# AVS-014.19

- Audited real GPT-SoVITS training readiness for Voice `0001`.
- Verified current dataset metadata gate: 2329 trainable clips, 13232.40 seconds, no duplicate audio path, WAV readable as mono/pcm_s16le/32000 Hz, transcript non-empty, language `vi`.
- Verified Runtime Profile `gpt_sovits_v2pro_default`: GPT-SoVITS v2Pro scripts and pretrained models exist; runtime Python torch CUDA works.
- Verified light hardware preflight: Quadro P1000 4 GB detected, controlled CUDA allocation OK, F: drive has about 121 GB free.
- Did not start real train because config/orchestration gates are not ready.
- Blockers: missing GPT-SoVITS preprocessing artifacts (`2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`), missing mapping for required `s1_train.py` config keys, and no production Training Job Worker/Frozen Training Plan lifecycle for real s1/s2 training.
- No source code, runtime upstream, Voice config, dataset source, Generate, Publish, commit or push was performed.

## AVS-016 Sprint 5: Production Reference Selection Execution

### Added

- Ran `ReferenceSelectionService` on the production Voice `0001` dataset using `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list` as the authority.
- Added production output artifacts under `cache/avs016_sprint5_reference_selection_voice_0001/`: `reference_selection_manifest.json`, `evaluation_holdout_manifest.json`, and `selection_report.json`.
- Added selection report statistics for accepted/rejected clips, Top50, frozen Top20, diversity summary, score summary, duration summary, and calibration summary.
- Added regression coverage for production-style `cache/...` metadata paths and selection report output.

### Changed

- `ReferenceSelectionService` now resolves production cache-relative audio paths from the app root when metadata-relative resolution does not exist.
- Diversity now uses alignment provenance `source_audio` when available, so production Top20 coverage is based on source MP3/chapter rather than the shared clip cache folder.
- Audio metric analysis was optimized to run the complete 2329-clip production selection without changing the public selection output contract.

### Validation

- Production run scanned 2329 clips, accepted 2329, rejected 0, produced Top50 50 and frozen Top20 20.
- Top20 diversity: 20 source MP3 and 20 chapter.
- All Top20 and evaluation holdout items have `exclude_from_future_training=true`.

### Notes

- No Preview, 40 WAV generation, fine-tune, LoRA, training, runtime inference binding, production voice generation, commit or push was performed.
- Generate/Preview/Train production readiness is unchanged.
## AVS-016 Sprint 6: Preview Generation

### Added

- Added AVS-016 Sprint 6 Top20 preview generation flow to `VoicePreviewBenchmarkService`.
- Added versioned Round creation from the frozen Sprint 5 Top20 manifest without changing Top20.
- Added exact 20 `ai_preview` WAV and 20 `benchmark_preview` WAV generation with matching transcript hash per Pair.
- Added `preview_manifest.json`, per-pair manifests and `preview_report.json`.
- Added regression coverage for Sprint 6 manifest/report generation and transcript identity validation.

### Validation

- Real output generated under `cache/avs016_sprint6_preview_generation_voice_0001/Round01/`.
- Artifact validation PASS: 20 Pair, 40 WAV, 20 AI Preview, 20 Benchmark Preview, mono PCM16 48 kHz, transcript identity PASS.

### Notes

- No Top20 mutation, Train, LoRA, Runtime Binding or Production Inference was performed.
- Preview generation used isolated VieNeu CPU/ONNX diagnostic runtime only; production Generate readiness is unchanged.
