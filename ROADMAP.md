# AI Voice Studio Roadmap

# Cap nhat AVS-016 Sprint 8 Round01 Deep Review Integration

- [x] Read Round01 Deep Review evidence from workbook/csv/report inputs without editing review inputs.
- [x] Block `pair_002` by transcript/reference plausibility root cause and remove old reference `000070_005_002` from adjusted Top20/Holdout.
- [x] Replace with valid next Top50 candidate `000015_022_001`.
- [x] Normalize preview-input transcript while preserving provenance source text.
- [x] Flag/penalize boundary-fragment and ellipsis transcript candidates.
- [x] Add preflight integrity and manifest audit fields for Round02.
- [x] Generate Round02 diagnostic artifact with 20 Pair / 40 WAV, regenerating only affected pairs.
- [ ] Human listening review for Round02 before any Training approval.
- [ ] Production Preview binding/inference consumer.

Status: AVS016_ROUND02_DIAGNOSTIC_READY; production Generate/Preview/Train readiness khong thay doi.

---

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
- [x] GPT-SoVITS Preprocessing Pipeline foundation
- [ ] GPT-SoVITS Preprocessing artifacts real PASS
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

# Reference Selection Review

- [x] Manual review artifact validation: completed status, exactly one available winner, reviewer metadata, fail-closed loader.
- [x] Production Reference Binding Foundation: fail-closed Service gate cho approved winner; chua bind Generate/Engine/Runtime consumer.
- [ ] Production Voice binding từ reference winner.
- [ ] Production inference validation từ selected reference.

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

- [x] Language Capability Catalog foundation
- [x] Voice Engine Binding theo language foundation
- [x] Language Detection heuristic foundation
- [x] Engine Capability Router foundation
- [x] GPT-SoVITS routing foundation cho zh/en/ja/ko/yue
- [x] Vietnamese engine static evaluation va primary candidate proposal
- [x] VieNeu-TTS controlled import/canary gate foundation
- [ ] Vietnamese-capable engine production integration
- [ ] Vietnamese engine local canary PASS
- [ ] Per-language Real Smoke PASS
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
- [x] AVS-014.17 GPT-SoVITS Runtime Integration da bat dau sau khi AVS-014.16A nghiem thu xong.

---

# Cap nhat AVS-014.17 GPT-SoVITS Runtime Integration for Generate

- [x] Runtime Doctor cho Generate bang Runtime Profile.
- [x] Local API `GET /api/v1/generate/runtime/doctor`.
- [x] Production provider noi Generate Unit voi EngineManager/GPT-SoVITS.
- [x] Job Queue worker `generate_unit` co ResourceRequirement GPU.
- [x] Endpoint enqueue Generate Unit qua Job Queue.
- [x] Failure path mark attempt/unit/artifact failed.
- [x] WAV production path runtime-gated qua artifact lifecycle.
- [x] AVS-014.17B Runtime Doctor tach 3 lop Environment / Selected Assets / Real Inference.
- [x] Chan false-positive: `generate_execution` khong READY chi vi runtime root/Python/script/FFmpeg/model file ton tai.
- [x] Them fingerprint va stale smoke handling cho Real GPT-SoVITS Smoke.
- [x] Real Smoke gate voi Voice Thu Minh `0001` / Variant `default`: BLOCKED dung cach vi thieu 4 asset bat buoc.
- [ ] Real GPT-SoVITS Generate smoke test voi Voice model hop le.
- [ ] MP3 production output qua Generate foundation.
- [ ] Nang Generate production readiness len READY sau khi runtime/voice smoke test dat.

---

# Cap nhat AVS-014.18 Voice Publish Automation & Post-Training Style Variants

- [x] VoiceConfig co `display_name` migration-safe tach khoi folder name.
- [x] Voice resolver theo `voice_id` cho service/catalog/runtime validation.
- [x] Rename display name theo `voice_id` khong rename folder/model/checkpoint/reference.
- [x] Voice Publish Service validate existing GPT/SoVITS/reference/language/runtime profile va yeu cau explicit confirmation truoc khi ghi Voice.
- [x] Checkpoint discovery liet ke candidate `.ckpt`/`.pth`, khong blind pick khi co nhieu candidate.
- [x] Publish fingerprint khong phu thuoc display name.
- [x] StyleProfile schema mo rong cho post-training style/prompt/parameter profile.
- [x] Variant binding voi Style Profile la generate profile, khong tao model/checkpoint rieng.
- [x] Local API foundation cho Voice detail, rename display name, publish validate/publish va checkpoint discover.
- [ ] Publish Voice Thu Minh that sau khi nguoi dung chon checkpoint/reference hop le.
- [ ] Real GPT-SoVITS Smoke PASS voi fingerprint moi.
- [ ] Nang Generate production readiness len READY sau khi publish va Real Smoke dat.

---

# Cap nhat AVS-014.19 GPT-SoVITS Real Training Execution Audit

- [x] Audit run `avs0149_thu_minh_train_20260717_061215`.
- [x] Dataset metadata gate PASS: 2329 trainable clips, 13232.40 giay, WAV mono/pcm_s16le/32000 Hz, language `vi`.
- [x] Runtime/hardware preflight nhe PASS: GPT-SoVITS v2Pro runtime READY, CUDA available tren Quadro P1000 4 GB, disk F con khoang 121 GB.
- [ ] Tao preprocessing artifacts chuan GPT-SoVITS: `2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`.
- [ ] Map du 5 key bat buoc cho GPT config: `output_dir`, `train_semantic_path`, `train_phoneme_path`, `half_weights_save_dir`, `exp_name`.
- [ ] Training production lifecycle qua Job Queue/Resource Manager/Training Worker cho s1/s2 train.
- [ ] Real GPT-SoVITS Train cho Voice 0001.
- [ ] Validate GPT `.ckpt` va SoVITS `.pth` cung mot Training Run de Publish review.

Training execution status: TRAINING_BLOCKED vi thieu preprocessing artifacts va production training orchestration.

# Cap nhat AVS-014.19A GPT-SoVITS Dataset Preprocessing Pipeline

- [x] Preprocessing Run/Plan/Stage model.
- [x] Frozen preprocessing plan fingerprint theo voice_id, metadata checksum, runtime fingerprint, scripts va pretrained.
- [x] Dataset input validation cho metadata.list: duplicate, path scope, WAV ffprobe, mono, pcm_s16le, 32000 Hz, transcript va language.
- [x] Runtime script discovery cho `1-get-text.py`, `2-get-hubert-wav32k.py`, `2-get-sv.py`, `3-get-semantic.py`.
- [x] Process runner dung command list, cwd/env ro rang, stdout/stderr log va timeout.
- [x] Artifact validation cho `2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`; v2Pro ghi nhan them `5-wav32k` va `7-sv_cn`.
- [x] Training preflight doc preprocessing manifest va phan biet READY/BLOCKED/STALE/MISSING.
- [ ] Real preprocessing artifacts PASS cho Voice 0001.

Preprocessing status: PREPROCESSING_BLOCKED vi runtime GPT-SoVITS v2Pro hien tai khong ho tro metadata language `vi` trong `1-get-text.py`/cleaner upstream. Khong chay script that de tranh artifact rong hoac READY gia.

---

# Cap nhat AVS-014.19A1 Vietnamese Text Frontend Compatibility

- [x] Audit upstream `prepare_datasets/1-get-text.py`.
- [x] Audit upstream `text/cleaner.py`, `text/symbols*.py`, GPT `AR/data/dataset.py` va inference language path.
- [x] Xac nhan runtime hien tai khong co Vietnamese cleaner/phoneme frontend hop le.
- [x] Giu gate `PREPROCESS_CONFIG_INVALID` cho metadata language `vi`.
- [x] Khong fake map `vi` sang `zh`, `en`, `auto`, `all_zh`, `yue` hoac language khac.
- [x] Khong build mapper va khong chay canary preprocessing khi compatibility khong duoc chung minh.
- [ ] Chon runtime/upstream patch/engine co ho tro Vietnamese frontend that.

Status: VI_UNSUPPORTED_BY_CURRENT_RUNTIME. Real preprocessing artifacts cho Voice 0001 van BLOCKED.

---

# Cap nhat AVS-014.20 Multi-Engine Language Capability & Routing Foundation

- [x] Language catalog cho `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- [x] VoiceConfig migration-safe cho `default_language`, `preferred_language`, `language_selection_mode`, `enabled_languages` va `engine_bindings`.
- [x] Voice cu mac dinh chi bat `vi`; khong auto-bind GPT-SoVITS cho tieng Viet.
- [x] All checkbox behavior: bat du 6 language qua service, khong mo rong scope ngam.
- [x] GPT-SoVITS mapping foundation: zh/all_zh, en/en, ja/all_ja, ko/all_ko, yue/all_yue.
- [x] Language detection heuristic va mixed-language segment planning foundation.
- [x] Generate Unit co route snapshot per language/engine/fingerprint/blockers.
- [x] Local API foundation cho languages, detection, language plan, enabled languages va voice language capabilities.
- [ ] Chon Vietnamese-capable engine that cho `vi`.
- [ ] Cau hinh trained assets/smoke PASS rieng cho tung GPT-SoVITS language neu dung zh/en/ja/ko/yue.

Status: MULTI_ENGINE_LANGUAGE_FOUNDATION_READY; Vietnamese Engine BLOCKED_PENDING_ENGINE_SELECTION; GPT-SoVITS Multilingual BLOCKED_PENDING_TRAINED_ASSETS_AND_SMOKE; Real Generate BLOCKED.

---

# Cap nhat AVS-014.21 Vietnamese Engine Evaluation & Language Selection

- [x] Voice language UI dung checkbox that cho `Tat ca`, `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- [x] Trang Voice khong luu enabled_languages rong va thao tac theo `voice_id`.
- [x] Generate UI co che do auto/fixed/multilingual language routing foundation.
- [x] Static evaluation cho VieNeu-TTS, F5-TTS Vietnamese va viXTTS.
- [x] Tach evidence/license/scorecard/download plan/canary plan, khong fake production readiness.
- [x] Low-resource policy cho may VRAM thap: GPU concurrency 1, batch size 1, lazy load, khong background benchmark.
- [ ] Download/import VieNeu-TTS sau khi nguoi dung xac nhan.
- [ ] Local canary VieNeu-TTS PASS tren may hien tai.
- [ ] Binding Vietnamese engine/model/reference vao Voice va Real Smoke PASS.

Status: VI_ENGINE_EVALUATION_READY; Vietnamese production integration van BLOCKED cho den khi co model local va canary PASS.

---

# Cap nhat AVS-014.22

- [x] Delta audit cho VieNeu-TTS candidate truoc download/import.
- [x] Controlled import/canary model va service.
- [x] Download/import plan chi dung mot candidate VieNeu: `pnnbao-ump/VieNeu-TTS-v3-Turbo`.
- [x] Target cache chuan: `cache/engines/vieneu_tts/<revision>/`.
- [x] Diagnostics root chuan: `diagnostics/vietnamese_engine_evaluation/<canary_run_id>/`.
- [x] Validate reference Thu Minh Voice 0001 candidate.
- [x] Chan false-positive readiness khi canary bi BLOCKED.
- [x] Sua contract VieNeu sang `CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND`.
- [x] Tao isolated CPU runtime voi CPU-only `torch`/`torchaudio`, `onnxruntime` va `vieneu==3.2.3`.
- [x] Verify CPU policy: CUDA false, khong co `CUDAExecutionProvider`, khong dung GPU fallback.
- [x] Fix SSL gate an toan bang `truststore` trong isolated runtime, khong disable verify.
- [x] Verify/download VieNeu-TTS local model revision `75ff82a72f54d55ed389e1eeb12041d3c4bac7d4`.
- [x] Xu ly codec dependency MOSS revision `ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae`.
- [x] Local canary VieNeu-TTS PASS bang CPU_ONNX toi da 3 cau.
- [x] Manual listening package co WAV that.
- [ ] Manual listening review cua nguoi dung.
- [ ] Production integration/binding sau manual review.

Status: VIENEU_CPU_CANARY_READY_FOR_MANUAL_REVIEW; production readiness khong thay doi.

---

# Cap nhat AVS-014.23

- [x] Audit GPT-SoVITS Train readiness cho Voice `0001`.
- [x] Resolve Voice theo `voice_id`, khong dung display name/folder name lam khoa.
- [x] Xac minh dataset final: 2329 trainable clips, 13232.40 giay, language `vi`, WAV mono/pcm_s16le/32000 Hz, transcript khong rong.
- [x] Xac minh Runtime Profile `gpt_sovits_v2pro_default`: GPT-SoVITS v2Pro, Python runtime, torch/CUDA, GPU Quadro P1000, scripts va pretrained files.
- [x] Xac minh machine safety baseline o muc audit: RAM/disk/GPU du nguong nhe, khong co GPU compute process; power status khong doc duoc nen ghi warning.
- [x] Tao preprocessing readiness plan moi trong `cache/training/voice_0001/gpt_sovits/`.
- [x] Training validation-only fail dung cach voi `preprocessing_not_ready`.
- [ ] Real GPT-SoVITS preprocessing artifacts PASS cho language `vi`.
- [ ] Safe Smoke Train SoVITS/GPT that.
- [ ] Checkpoint smoke load validation.
- [ ] Canary generation tu checkpoint smoke.
- [ ] Full Train GPT-SoVITS sau khi user approve.

Status: GPT_SOVITS_TRAINING_READINESS_BLOCKED vi runtime GPT-SoVITS v2Pro hien tai khong ho tro Vietnamese text/phoneme frontend `vi`.

---

# Cap nhat AVS-016 Sprint 3 Voice Preview Generation

- [x] Voice Preview Benchmark diagnostic foundation.
- [x] `VoicePreviewBenchmarkService` tao Round versioned `Round01`, `Round02`, ... va khong ghi de Round da ton tai.
- [x] Moi Benchmark Pair tao contract cho `same_preview_v1.wav` va `new_preview_v1.wav`.
- [x] Preview generation chay isolated diagnostic runner duoc truyen explicit, khong bind Production Generate/Engine/Runtime.
- [x] WAV preview validation: doc duoc, PCM16, mono, sample rate runtime, duration duong va khong toan im lang.
- [x] Pair manifest chi ghi evidence preview sau khi WAV validation PASS: path, checksum SHA-256, duration, timestamp, runtime profile va validation.
- [x] Regression tests cho 20 same previews, 20 new previews, no-overwrite, Round versioning, manifest update va invalid WAV rejection.
- [ ] Real 40-preview Round: BLOCKED den khi co frozen benchmark manifest gom dung 20 Pair da duoc phe duyet, immutable reference identity va benchmark transcript.
- [ ] Production Voice Preview/Generate binding: chua thuc hien trong Sprint nay.

Status: AVS016_PREVIEW_DIAGNOSTIC_FOUNDATION_READY; REAL_PREVIEW_ROUND_BLOCKED_PENDING_FROZEN_BENCHMARK_INPUT; production readiness khong thay doi.

---

# Cap nhat AVS-016 Sprint 4 Reference Selection Engine

- [x] Full `metadata.list` authority scan, khong dung candidate cache lam authority.
- [x] Alignment va Dataset Health evidence filtering cho duplicate/suspicious/invalid/AI-generated/music-heavy/multiple-speakers.
- [x] Quality ranking dua tren audio metrics, transcript quality va pitch distribution.
- [x] AVS-014.24 calibration-aware weighting.
- [x] Top50 ranking.
- [x] Diversified Top20 selection theo source/chapter coverage.
- [x] Frozen Top20 voi `freeze_status=frozen` va `exclude_from_future_training=true`.
- [x] `evaluation_holdout_manifest.json` cho evaluation holdout.
- [x] Regression tests cho Reference Selection Engine.
- [ ] Production Reference binding/inference consumer sau khi gate AVS-014.24 va production consumer duoc noi.

Status: AVS016_REFERENCE_SELECTION_ENGINE_READY; production binding/inference readiness khong thay doi.

# Cap nhat AVS-016 Sprint 5 Production Reference Selection Execution

- [x] Chay complete Reference Selection Engine tren production Voice `0001` dataset.
- [x] Doc `metadata.list` lam authority: 2329 clip scanned.
- [x] Load alignment manifest/report, dataset health report va transcript/quality evidence hien co.
- [x] Tinh quality score voi audio metrics, transcript quality, pitch distribution va calibration-aware weighting AVS-014.24.
- [x] Generate Top50 candidates.
- [x] Diversify va freeze Top20.
- [x] Generate `evaluation_holdout_manifest.json`.
- [x] Dam bao moi selected clip co `exclude_from_future_training=true`.
- [x] Tao `selection_report.json` voi accepted/rejected statistics, diversity summary va calibration summary.
- [ ] Production Reference binding/inference consumer sau Sprint 5.

Status: AVS016_PRODUCTION_REFERENCE_SELECTION_READY; production Generate/Preview/Train readiness khong thay doi.
# Cap nhat AVS-016 Sprint 6 Preview Generation

- [x] Dung Frozen Top20 Sprint 5 lam input bat bien.
- [x] Sinh 20 AI Preview WAV va 20 Benchmark Preview WAV trong `cache/avs016_sprint6_preview_generation_voice_0001/Round01/`.
- [x] Ghi `preview_manifest.json`, per-pair manifest va `preview_report.json`.
- [x] Validate transcript identity, output count va WAV format mono PCM16 48 kHz.
- [ ] Manual listening review/cham diem chat luong preview.
- [ ] Production Preview binding/inference consumer.

Status: AVS016_PREVIEW_GENERATION_ARTIFACTS_READY; production Generate/Preview readiness khong thay doi.
