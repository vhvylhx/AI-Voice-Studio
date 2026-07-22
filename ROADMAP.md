# AI Voice Studio Roadmap

> Nguyên tắc:
>
> Luôn ưu tiên tạo ra phiên bản sử dụng được trước (MVP), sau đó mới mở rộng tính năng.

---

# MVP (v0.1)

## Mục tiêu

Có thể clone một giọng và tạo Audio bằng GPT-SoVITS.

---

# Core

- [x] AppContext
- [x] EngineManager
- [x] RuntimeService
- [x] Event Bus
- [x] Config
- [ ] Settings hoàn chỉnh

---

# Project

- [x] Khởi tạo Project
- [x] Cấu trúc thư mục
- [x] Project Schema
- [x] Migration project.json
- [x] Workspace
- [ ] Project UI hoàn chỉnh

---

# Engine

- [x] GPT-SoVITS Adapter
- [x] Runtime Detect
- [x] Engine Config
- [x] Runtime Validation
- [x] Generate End-to-End
- [x] Generate MP3
- [x] Train Validation Pipeline
- [ ] Train GPT-SoVITS
- [ ] Preview

---

# Reader

- [x] Đọc DOCX
- [x] Đọc TXT
- [ ] Dán văn bản
- [ ] EPUB
- [ ] PDF

---

# Voice

- [x] Voice Schema
- [x] Voice ID cố định
- [x] Migration voice.json
- [x] Variant Schema
- [ ] Train Voice
- [ ] Preview Voice
- [ ] Voice Library

---

# Dataset

- [x] Dataset Validation
- [x] Dataset Manifest
- [x] Dataset Report
- [x] ZIP Protection
- [x] Workspace Scan
- [x] Segmentation
- [x] Audio Metadata
- [x] ffprobe
- [x] Audio Alignment Pipeline
- [x] Faster-Whisper model local
- [x] Audio Slice
- [x] GPT-SoVITS Metadata
- [x] Quality-First Alignment
- [x] Text ↔ MP3 Matching Rules
- [x] Dataset Health
- [x] Dataset Workflow
- [x] Dataset Repair
- [x] Dataset Review

---

# Generate

- [x] Generate Architecture Foundation
- [x] Generate WAV
- [x] Generate MP3
- [ ] Batch Generate
- [ ] Queue
- [x] Resume
- [x] Retry

---

# Runtime

- [x] Python
- [x] FFmpeg
- [x] CUDA
- [x] NVIDIA GPU
- [x] GPT-SoVITS Detect
- [x] Runtime Profile Schema

---

# UI

- [x] Main Window
- [x] Project
- [x] Workspace
- [x] Voice
- [x] Training
- [ ] Runtime
- [x] Generate
- [ ] Settings
- [ ] Queue

---

# API

- [ ] Generate API
- [ ] Runtime API
- [ ] Voice API
- [ ] Queue API

---

# Subtitle

- [ ] Whisper
- [ ] Faster-Whisper
- [ ] Subtitle Editor
- [ ] SRT
- [ ] ASS

---

# Video Dubbing

- [ ] Timeline
- [ ] Subtitle Sync
- [ ] Replace Audio
- [ ] Export Video

---

# Multi Engine

- [ ] XTTS
- [ ] Fish Speech
- [ ] CosyVoice
- [ ] Plugin System

---

# Tài liệu duy trì ngữ cảnh

- [x] AGENTS.md
- [x] ROADMAP.md
- [x] Architecture.md
- [x] CURRENT_SPRINT.md
- [x] DECISIONS.md
- [x] CHANGELOG.md

---

# Ưu tiên tiếp theo

- [x] Text ↔ MP3 Matching Rules
- [x] Dataset Health
- [x] Dataset Workflow
- [x] Dataset Repair
- [x] Dataset Review
- [x] Training Validation
- [ ] Job Resume
- [ ] Progress UI
- [ ] AVS-014 GPT-SoVITS Training

---

# Tiến độ Sprint

## Hoàn thành

- [x] AVS-001 Phân tích kiến trúc và lập kế hoạch
- [x] AVS-002 AppContext + EngineManager
- [x] AVS-003 Project Schema
- [x] AVS-004 Workspace
- [x] AVS-005 Voice Schema
- [x] AVS-006 Runtime
- [x] AVS-007 GPT-SoVITS Generate
- [x] AVS-008 Engine Config
- [x] AVS-009 Generate End-to-End
- [x] AVS-010 Cleanup
- [x] AVS-011 Dataset
- [x] AVS-012 Dataset Segmentation
- [x] AVS-013 Audio Alignment Pipeline
- [x] AVS-013.5 Faster-Whisper Runtime Validation
- [x] AVS-013.6 Quality-First Dataset Alignment
- [x] AVS-013.7 Text ↔ MP3 Matching Rules
- [x] AVS-013.8 Dataset Health
- [x] AVS-013.9 Dataset Workflow
- [x] AVS-013.10 Dataset Repair
- [x] AVS-013.11 Dataset Review

---

## Đang thực hiện

- [ ] AVS-014 GPT-SoVITS Training validation và tham số train

---

## Tiếp theo

- [ ] Chốt tham số Train thật
- [ ] AVS-015 Voice Preview
- [ ] AVS-016 Batch Generate
- [ ] AVS-017 API
- [ ] AVS-018 Subtitle
- [ ] AVS-019 Video Dubbing

---

# Cập nhật AVS-014.1

- [x] Runtime Profile mặc định cho GPT-SoVITS v2Pro.
- [x] Runtime validation thật: Python, torch, CUDA/GPU, faster-whisper, scripts và pretrained models.
- [x] Dataset Review Thu Minh được chốt an toàn trước train: rejected/ignored file lỗi, không đưa file lỗi vào train.
- [x] Validation-only Thu Minh: 19 clip, khoảng 140.04 giây.
- [x] GPT-SoVITS smoke test tối thiểu: gọi runtime Python thật, đọc metadata/WAV, kiểm tra CUDA và tạo smoke checkpoint.
- [ ] Full train GPT-SoVITS sau khi chốt tham số train thật.

---

# Cập nhật AVS-014.2

- [x] Full Dataset Preparation Thu Minh chạy hoàn tất 68/68 source bằng runner có resume state.
- [x] Global progress/log ghi được progress đến 100% và trạng thái done.
- [x] `metadata.list` đã validate bằng ffprobe: 13 valid clips, 93.98 giây, mono, pcm_s16le, 32000 Hz.
- [x] Suspicious được giữ ngoài metadata: 76 clips.
- [x] Source bị bỏ toàn file được report: 2 source với `source_error_rate_exceeded`.
- [x] Compile, script tests và UI smoke đạt.
- [ ] Chốt hướng xử lý dataset nhỏ: train thử với 13 clip hoặc review/sửa suspicious để tăng dữ liệu valid.
- [ ] Full train GPT-SoVITS sau khi chốt tham số train thật.

---

# Cập nhật AVS-014.3

- [x] Suspicious Recovery Service tách riêng khỏi alignment pipeline chính.
- [x] Recovery giữ similarity threshold 90, không ratio fallback cho valid.
- [x] Recovery thử sequential ASR window quanh timestamp dự kiến, gộp 2-3 ASR segment và tách text theo dấu câu.
- [x] Recovery report ghi old/new similarity, method, reason và source file.
- [x] Preview 3 nhóm suspicious đã chạy: no_alignment_match, similarity_too_low, source_error_rate_exceeded.
- [x] Không chạy full recovery vì preview không cứu thêm clip hợp lệ.
- [ ] Manual review hoặc chuẩn hóa lại text/audio nguồn để tăng valid clips.
- [ ] Full train GPT-SoVITS sau khi có đủ dataset valid và chốt tham số train thật.

---

# Cap nhat AVS-014.4

- [x] Workflow Dataset ho tro MP3 folder rieng va Text/DOCX folder rieng.
- [x] Project luu lua chon dataset cuoi: audio_folder, text_folder, output_folder, use_input_as_output, Voice va Runtime Profile.
- [x] Dataset scan/matching ho tro hai thu muc rieng va van giu luat chapter_number.
- [x] FullDatasetPreparationService gom Scan -> Health -> Repair -> Review -> Alignment -> Metadata Validation.
- [x] Voice Architecture Foundation: Voice identity, Variant, Preset, Reference Style, Text Profile va Generate Request contract.
- [ ] Resolve 34 blocking items cua nguon Thu Minh moi truoc khi chay Alignment toan bo.
- [ ] Chay Alignment toan bo nguon moi sau khi Review cho phep.
- [ ] Full train GPT-SoVITS sau khi co du valid clips va nguoi dung xac nhan tham so train.

---

# Cap nhat AVS-014.5

- [x] Same Folder Mode cho workspace/<Voice Name>/ hien tai.
- [x] Separate Folder Mode tiep tuc ho tro audio/text folder rieng.
- [x] Project cu co the tu nhan workspace/<voice_name> lam audio_folder va text_folder.
- [x] Auto Review an toan cho Dataset Health blocking items.
- [x] Auto Review Thu Minh dat pending = 0, train_allowed = true, khong dung Approve All.
- [x] Resume alignment khong ghi trung metadata.
- [ ] Full Alignment toan bo 183 source Thu Minh.
- [ ] Metadata final sau khi Full Alignment hoan tat.
- [ ] De xuat tham so Train that sau khi co dataset final.

---

# Cap nhat AVS-014.6

- [x] Generate Architecture Foundation cho Standard Mode va AI Style Mode.
- [x] Contract GenerateSelectionConfig, GenerateRequest, GenerateResult, VariantTimeline, StyleTimeline, GenerateProgress, SpeedProfile va TempWorkspace.
- [x] Standard Mode chi dung dung Voice va Variant nguoi dung chon.
- [x] AI Style Mode chi duoc chon Variant/Style trong scope nguoi dung cho phep.
- [x] Timeline chi doi Variant/Style tai boundary an toan, khong doi giua tu hoac giua cau.
- [x] Speed presets duoc validate; custom speed can nguong config truoc khi dung.
- [x] Temp workspace nam ngoai output, cleanup khi success va giu lai khi error/stop de resume.
- [x] Default Variant contract: moi Voice co `default`.
- [x] Default Style contract: moi Voice co `default_style_id`.
- [x] Custom speed safe range: 0.80 den 1.20.
- [x] Cleanup policy cho success, pause, cancel, error va resume.
- [x] UI Generate day du cho Variant/Style multi-select.
- [x] AVS-014.7 Generate UI va Generate Pipeline.
- [ ] Generate that voi Voice model hop le.

---

# Cap nhat AVS-014.8

- [x] Resume Full Alignment Thu Minh tu checkpoint hien co.
- [x] Hoan tat 183/183 source hop le, khong chay lai tu dau va khong ghi trung metadata.
- [x] Rebuild metadata final tu `alignment_state.json`: 2329 clip trainable.
- [x] Validate metadata final bang ffprobe: khong duplicate, WAV doc duoc, mono, pcm_s16le, 32000 Hz, transcript khong rong.
- [x] Sinh Dataset Quality Report va Reference Audio candidates.
- [x] Train validation_only dat voi Runtime Profile GPT-SoVITS v2Pro hien tai.
- [ ] Nguoi dung nghe/chot Reference Audio cuoi.
- [ ] Nguoi dung chot tham so Train that.
- [ ] Chay Train GPT-SoVITS that sau khi duoc xac nhan.

---

# Cap nhat AVS-014.9

- [x] Runtime Training Profile model/service.
- [x] Settings UI co khu Runtime & Training.
- [x] Huong dan tieng Viet trong Runtime & Training.
- [x] Tooltip tieng Viet cho profile, tham so va nut thao tac.
- [x] Dialog huong dan chi tiet va sao chep noi dung.
- [x] Canh bao Runtime/CUDA/VRAM/pretrained bang tieng Viet de hieu.
- [x] Auto/Compatibility/Performance/Custom profile modes.
- [x] Auto Detect Hardware cho GPU/VRAM/CUDA/CPU/RAM/Python/Runtime Profile.
- [x] Auto tren Quadro P1000 4 GB chon Compatibility: batch_size 1, num_workers 0, CUDA, v2Pro.
- [x] App-managed runtime copy khong sua runtime goc.
- [x] Pre-flight AVS-014.9 validation_ready voi 2329 clip.
- [x] Runtime & Training buttons co handler that: detect hardware, validate runtime, reset recommended, xem config va copy report.
- [x] Run directory train that da duoc chuan bi: `voices/0001/model/avs0149_thu_minh_train_20260717_061215`.
- [x] GPT command preview da tao nhung bi chan truoc train vi config copy thieu `output_dir`, `train_semantic_path`, `train_phoneme_path`, `half_weights_save_dir`, `exp_name`.
- [ ] Nguoi dung xac nhan train that.
- [ ] Chay GPT stage va SoVITS stage that.

---

# Cap nhat AVS-014.7

- [x] Generate UI tren AudioPage cho Standard Mode va AI Style Mode.
- [x] Variant/Style scope: Variant, All Variants, Style, All Styles.
- [x] ContextAnalysisService tao segment/context va candidate score cho AI Style Mode.
- [x] GeneratePlanningService tao GeneratePlan va chunk tu VariantTimeline/StyleTimeline.
- [x] GeneratePipelineService validate Voice/model/reference/output, generate tung chunk, retry va merge.
- [x] Retry mac dinh = 1; neu chunk van loi thi dung job, giu temp/state/log va khong tao final output gia.
- [x] Temp generate nam ngoai output va co resume chunk da xong.
- [x] WAV va MP3 output; MP3 mac dinh 192 kbps, ho tro 128/192/256/320 kbps.
- [x] Project luu lua chon Generate cuoi gom input/output, format va bitrate.
- [x] Report va progress payload cho Generate job.
- [ ] Kiem tra Generate that voi Voice model hop le.
- [ ] Tinh chinh DSP nang cao cho natural pause detection va crossfade boundary safety.

---

# Cap nhat AVS-014.10

- [x] Kien truc ba lop: Bootstrap Launcher, Main App va Local API.
- [x] Bootstrap Launcher chay duoc khi thieu PySide6 va khong import UI som.
- [x] First-Run Setup status/report cho dependency, runtime va tinh nang bi chan.
- [x] RuntimeEnvironmentManager phat hien Python app, dependency, FFmpeg/FFprobe, NVIDIA/GPU va Runtime Profile.
- [x] FeatureReadinessService tra ve available/degraded/blocked de UI/API dung chung.
- [x] Main App co nen tang Limited Mode thong qua Feature Readiness; app_shell bi chan neu thieu PySide6.
- [x] Local API `/api/v1` MVP cho health, readiness, capabilities, voices, variants, catalog va generation jobs.
- [x] API auth bang token, health khong can token, mac dinh bind localhost `127.0.0.1`.
- [x] Settings UI co nhom API & Tich hop: enable, auto-start, host, port, token, URL va thao tac API.
- [x] Voice Catalog/Variant Catalog khong leak duong dan model/runtime/checkpoint.
- [x] Generation Job tao state/log/temp/output rieng, khong Generate that khi Voice chua ready.
- [x] Tai lieu Local API va Bootstrap First-Run.
- [ ] FastAPI/OpenAPI tu dong neu sau nay chot them dependency.
- [ ] Video App tich hop that qua Local API khi Voice model da ready.

---

# Cap nhat AVS-014.11

- [x] Voice DNA / Reading Style Profile foundation.
- [x] StyleProfile schema voi ID rieng `style_000001`.
- [x] StyleProfileRepository, StyleProfileService, Integrity, Extraction placeholder va Export/Import `.avstyle`.
- [x] VoiceConfig migration-safe cho `reading_style`.
- [x] Variant style fields: `style_profile_id`, `style_mode`, `style_strength`.
- [x] Local API endpoints cho Style Profile.
- [x] Feature Readiness cho style profile management/extraction/import/export/voice link/generation usage.
- [x] Trang UI `Phong cach doc / Voice DNA` va section Settings cho du lieu tham chieu giong doc.
- [x] Tai lieu Voice DNA, Style Profile format, backup/restore va UI design system.
- [ ] Prosody analyzer that.
- [ ] Generate engine ap dung Style Profile that vao audio.
- [ ] UI smoke voi interpreter co PySide6.

---

# Cap nhat AVS-014.12

- [x] Training Reference architecture foundation.
- [x] Training Dataset / Voice DNA / Speaker Reference ownership separation.
- [x] TrainingPage scroll foundation.
- [x] Ba reference mode trong TrainingPage.
- [x] Voice rename validation va ID invariant.
- [x] Style Profile rename validation va ID invariant.
- [x] Migration-safe VoiceConfig cho `speaker_reference` va `training_reference`.
- [x] Test cho TrainingReferenceConfig, AudioTextPairService, TrainingReferenceResolver, ReferenceAudioValidation, Voice rename, Style Profile rename va scroll foundation.
- [ ] Prosody analyzer that.
- [ ] Generate engine ap dung Style Profile that.
- [ ] Train GPT-SoVITS that sau khi chot config/runtime.

---

# Cap nhat AVS-014.13

- [x] Project identity tach Project ID va display name.
- [x] Project moi dung folder ID-based, Project legacy name-based van load duoc.
- [x] ProjectConfig migration-safe cho lifecycle/metadata/workspace/health.
- [x] Project Registry foundation.
- [x] Recent Projects foundation.
- [x] Create/Open/Close/Switch Project.
- [x] Rename Project display-name-only.
- [x] Duplicate Project config-safe.
- [x] Archive va Restore Archive.
- [x] Export/Import Project package nhe co manifest va path traversal guard.
- [x] Backup/Restore Project co safety backup.
- [x] Project Validation va Repair an toan.
- [x] AppContext co Project registry/validation/backup/package service.
- [x] Project Manager UI foundation.
- [x] Local API read-only cho Project/Workspace.
- [x] Tests Project Manager lifecycle/API.
- [ ] Full Project Manager polish.
- [ ] Full export package gom selected assets sau khi co xac nhan dung luong.
# AVS-014.13.1 Reference Data Vault & Persistence Hardening

- [x] Delta audit Reference persistence.
- [x] ReferenceAsset model.
- [x] ReferenceRegistry model/service.
- [x] ReferenceVaultService managed copy/checksum/dedupe.
- [x] Audio-text pair persistent manifest.
- [x] Speaker Reference migration-safe asset IDs.
- [x] Training Reference migration-safe asset IDs.
- [x] Style Profile draft source asset IDs.
- [x] Project backup/export/import hooks cho reference.
- [x] Project validation hook cho reference integrity.
- [x] Tests reference vault/pair/persistence/backup-export-import.
- [ ] UI full dialog cho Reference Vault/Relink/Complete Backup.

---

# Cap nhat AVS-014.14 Job & Queue System

- [x] Job identity va Job model migration-safe.
- [x] Job state machine.
- [x] Job repository persistent JSON voi atomic write va corrupt quarantine.
- [x] Persistent Queue voi priority, idempotency va dependency.
- [x] Job runner/worker contract voi cooperative pause/resume/cancel.
- [x] Progress, ETA va per-job log.
- [x] Retry va recovery sau startup/shutdown.
- [x] AppContext integration.
- [x] Queue UI foundation.
- [x] Dashboard job summary.
- [x] Local API read-only cho jobs/queue/logs.
- [x] Tests Job system.
- [ ] Chuyen tung workflow nang sang Job Queue o cac sprint sau.
- [ ] Analyzer thật cho Voice DNA.
# Cap nhat AVS-014.15 Intelligent Resource Manager

- [x] Resource models.
- [x] Hardware detection an toan.
- [x] Resource snapshots.
- [x] Resource requirements cho Job Worker.
- [x] Resource decisions ready/waiting/unsupported.
- [x] Resource policies tap trung.
- [x] Resource leases persistent.
- [x] Job state `waiting_resource`.
- [x] Queue scheduling dua tren Resource Manager.
- [x] Release stale/resource leases.
- [x] Resource Monitor UI.
- [x] JobsPage va Dashboard integration.
- [x] Settings hien Resource Policy.
- [x] Local API read-only cho resources.
- [x] Tests Resource Manager.
- [ ] Gan ResourceRequirement chi tiet cho tung workflow nang khi migrate sang Job Queue.
- [ ] UI editor day du cho Resource Policy.
- [ ] Auto-pause/slowdown theo pressure chi bat khi co quyet dinh rieng.

---

# Cap nhat AVS-014.16 Generate Pipeline Foundation

- [x] Delta audit Generate source hien tai: UI/pipeline cu da co, nhung thieu persistence/session/registry/manifest foundation.
- [x] Them Generate domain model cho Request, Session, Source Snapshot, Document, Chapter, Unit, Attempt, Plan, Manifest, Registry, Settings va StateMachine.
- [x] Them GenerateRepository luu JSON atomic theo session va registry.
- [x] Them GenerateTextStructureService doc pasted text/TXT/DOCX, normalize, detect chapter va split unit khong sua file goc.
- [x] Them GenerateSessionService tao validation report, source snapshot, normalized text, plan, manifest, resume/retry inspection.
- [x] Them request checksum/materialized_at, frozen plan snapshot/checksum, planned artifact records va basic WAV validation.
- [x] Them no-loss reconstruction verifier giu title/intro/outro va chan freeze neu reconstruction fail.
- [x] Them frozen plan immutable guard va plan integrity check.
- [x] Them artifact lifecycle foundation: registry, lineage, reservation, temp-to-final promotion, validation gate va history.
- [x] Them resume/retry execution orchestration foundation voi production UNAVAILABLE va test-only provider trong tests.
- [x] Them recovery foundation: startup light scan, manifest rebuild va temp/orphan classification khong load engine.
- [x] Tich hop Job Queue bang worker `generate_prepare` CPU-light, khong goi engine va khong tao audio gia.
- [x] Tich hop AppContext, FeatureReadinessService va Local API foundation endpoints cho Generate sessions/plan/units/attempts/artifacts/resume/retry/recovery/manifest/readiness.
- [x] Them UI foundation controls tren trang Tao Audio cho Validate/Plan/Resume Inspect/Retry Inspect va execution disabled khi production handler unavailable.
- [x] Them tests Generate Pipeline Foundation cho reconstruction, frozen plan, artifact lifecycle, test-only provider, recovery, API routes, Job Queue va UI smoke.
- [ ] Generate Session/Plan detail UI polish rieng.
- [ ] WAV/MP3 production output va real GPT-SoVITS handler van thuoc sprint sau.
- [ ] Generate inference that van thuoc sprint sau, chi chay khi Voice/model/runtime hop le va nguoi dung xac nhan.

---

# Cap nhat AVS-014.16A Foundation Cleanup & Consistency

- [x] Khong them tinh nang moi; chi cleanup/stabilize foundation.
- [x] Dong bo `docs/PROJECT_STATUS.md` voi source hien tai va readiness that.
- [x] Kiem tra duplicate/dead code/placeholder/hardcode/data safety o muc static audit.
- [x] Giu Generate execution, Preview Audio, WAV output va MP3 output o trang thai UNAVAILABLE khi chua co production handler.
- [ ] AVS-014.17 GPT-SoVITS Runtime Integration chi bat dau sau khi AVS-014.16A nghiem thu xong.

---

# Cap nhat Resource Safety Hardening Phase 1

- [x] Resource Policy schema v2 foundation.
- [x] Feature modes doc lap: disabled, monitor_only, enforced.
- [x] Safe defaults theo design freeze cho resolved policy: RAM/VRAM reserve, RAM pressure thresholds, thread/batch/concurrency, CPU fallback va timeout.
- [x] Migration additive v1 -> v2, idempotent va tao backup truoc migration save.
- [x] Safe resolution thanh `ResolvedResourcePolicy` voi fingerprint deterministic.
- [x] Fallback khi primary policy loi: thu backup hop le, neu khong co thi dung built-in safe policy; corrupt primary khong bi ghi de.
- [x] Runtime override hop le chi tac dong resolved object, khong persist ngam.
- [x] Existing runtime/scheduling consumers van dung projection tuong thich Phase 1; chua bat enforcement moi.
- [ ] Resource Decision v2 enforcement thuoc Phase 2 neu duoc phe duyet rieng.
- [ ] Process Supervisor enforcement/kill-tree thuoc Phase sau neu duoc phe duyet rieng.

---

# Cap nhat Resource Safety Hardening Phase 2

- [x] Snapshot validation cho RAM/GPU/VRAM/Disk voi valid/invalid/unknown/stale.
- [x] Snapshot freshness co captured_at, age va TTL tu Resource Policy.
- [x] Unknown/invalid provider state khong fail-open trong shadow decision.
- [x] Workload classification foundation: light, cpu_heavy, gpu_inference, gpu_training, io_heavy.
- [x] Resource Decision v2 shadow/monitor-only voi structured observation.
- [x] Stable reason codes Phase 2 co tests deterministic.
- [x] Actual legacy decision khong doi va Queue scheduling khong doi.
- [ ] Resource Decision v2 enforcement chua bat, can phe duyet rieng.
- [ ] Process Supervisor enforcement/kill-tree thuoc Phase sau neu duoc phe duyet rieng.

---

# Cap nhat Resource Safety Hardening Phase 3

- [x] Lease Lifecycle v2 foundation voi `ResourceLeaseV2` va `ResourceLeaseObservation`.
- [x] Shadow evaluator monitor-only cho acquire/renew/release/expiry/stale/reconciliation/duplicate.
- [x] Stable lease reason codes co tests deterministic.
- [x] Policy additive fields cho `lease_renew_interval_seconds` va `stale_lease_handling_mode`.
- [x] ResourceLeaseManager co observation path khong mutate actual lease legacy.
- [x] Corrupt/legacy/unknown lease store observation khong crash va khong ghi de.
- [x] Resource Lease v2 enforcement gated theo policy `resource_lease_v2_mode=enforce`.
- [x] Acquire/renew/release/reconcile v2 co owner/job validation, fail-safe corrupt store, atomic persistence va reason codes on dinh.
- [x] Process Supervisor va kill-tree foundation monitor-only/simulated cho identity, registry, tree discovery, shadow shutdown plan va audit.
- [ ] Production kill-tree, Runtime Guard action va Thread Budget enforcement thuoc Phase sau neu duoc phe duyet rieng.

---
