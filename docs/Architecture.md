# AI Voice Studio - Architecture

## Mục tiêu

AI Voice Studio là phần mềm Desktop quản lý toàn bộ quy trình tạo Audiobook AI.

Kiến trúc phải:

- Không phụ thuộc Engine.
- Có thể mở rộng nhiều AI Engine.
- Có thể mở rộng nhiều Plugin.
- Dễ bảo trì.
- Dễ mở rộng lâu dài.

---

# Kiến trúc tổng thể

UI

↓

Pages

↓

Services

↓

EngineManager

↓

Engine

↓

Adapter

↓

AI Runtime

↓

Output

---

# Core

Core không phụ thuộc UI.

Bao gồm:

- AppContext
- EngineManager
- Config
- Logger
- Event Bus
- Runtime
- Paths

---

# Services

Toàn bộ nghiệp vụ nằm trong Services.

Hiện có:

- ProjectService
- WorkspaceService
- VoiceService
- DatasetService
- DatasetRepairService
- DatasetReviewService
- DatasetSegmentationService
- AlignmentService
- TrainAudioPrepService
- RuntimeService
- EngineService
- TrainingService
- GenerateService
- GeneratePlanningService
- GeneratePipelineService
- ContextAnalysisService
- AudioMergeService
- TempWorkspaceService
- QueueService
- LogService

Service không thao tác trực tiếp giao diện.

---

# Repository

Repository chỉ làm nhiệm vụ đọc và ghi dữ liệu.

Không xử lý nghiệp vụ.

Ví dụ:

- project.json
- voice.json
- settings.json
- engines.json

---

# Pages

Mỗi Page chỉ hiển thị dữ liệu.

Không xử lý logic.

Hiện có:

- Dashboard
- Workspace
- Project
- Voice
- Training
- Runtime
- Queue
- Settings

---

# Widgets

Widget dùng lại nhiều nơi.

Ví dụ:

- InfoCard
- VoiceCard
- ProgressBar
- RuntimeCard
- StatusWidget

---

# Engine

Mỗi Engine phải implement BaseEngine.

Ví dụ:

- GPT-SoVITS
- XTTS
- Fish Speech
- CosyVoice

Engine được quản lý bởi EngineManager.

UI không biết Engine cụ thể.

---

# Adapter

Adapter chịu trách nhiệm giao tiếp với Runtime.

Ví dụ:

GPTSoVITSAdapter

↓

Runtime Python

↓

GPT-SoVITS CLI

↓

Output

---

# Runtime

Runtime chịu trách nhiệm:

- Python
- FFmpeg
- CUDA
- GPU
- GPT-SoVITS

RuntimeService quản lý toàn bộ trạng thái Runtime.

---

# Project

Một Project chứa:

- Workspace
- Voice
- Settings
- Cache
- Export

---

# Workspace

Workspace chứa Dataset.

Ví dụ:

workspace/

└── Thu Minh/

├── 001.docx

├── 001.mp3

├── 002.docx

├── 002.mp3

↓

Dataset

↓

Segmentation

↓

Training

---

# Voice

voices/

└── Thu Minh/

├── voice.json

├── dataset/

├── model/

├── variants/

├── preview.wav

├── export/

└── logs/

Voice sử dụng:

- Voice ID cố định.
- Đổi tên không đổi ID.
- Chuẩn bị nhiều Variant.

---

# Dataset Pipeline

Workspace

↓

Validation

↓

Manifest

↓

Dataset Health

↓

Dataset Repair

↓

Dataset Review

↓

Segmentation

↓

Alignment

↓

Audio Clip

↓

Metadata

↓

Train Validation

↓

Training

Không sửa file gốc.

Mọi dữ liệu sinh ra đều nằm trong cache.

Dataset Repair:

- Không sửa file gốc.
- Chỉ repair lỗi an toàn trong cache/workspace output.
- Duplicate được xử lý bằng cách giữ bản tốt nhất đã được DatasetService chọn và đưa bản trùng vào ignored.
- Broken file, empty file, missing_audio, missing_text, filename_content_mismatch, test_version và invalid_filename mặc định bị skip/report để người dùng review.
- Report sau repair gồm before, repaired, skipped, after và final_usable_percent.
- Workflow chuẩn bị hai chế độ Auto Repair và Manual Review cho UI Sprint sau.

Dataset Review:

- Không sửa file gốc.
- Sinh review_report.json trong cache/workspace output.
- Review item gồm source_audio, source_text, reason, suggestion và status.
- Status hợp lệ: pending, approved, rejected, ignored.
- UI sau này có thể Approve All, Reject All, Ignore All và filter theo reason/code.
- Dataset chỉ được đi tiếp khi blocking_errors = 0 hoặc toàn bộ blocking_errors đã được review.

Train Validation:

- Chỉ dùng metadata.list hợp lệ do Alignment sinh ra.
- Không train suspicious, weak_source chưa duyệt, rejected, ignored, unmatched hoặc filename_content_mismatch.
- Kiểm tra review_report cho phép train trước khi gọi Runtime.
- Kiểm tra metadata.list tồn tại, không rỗng, transcript không rỗng.
- Mọi WAV trong metadata phải đọc được bằng ffprobe, mono, pcm_s16le, 32000 Hz.
- Runtime lấy từ Runtime Profile hiện tại, không hard-code runtime_path, Python path hoặc pretrained model path.
- TrainConfig gom toàn bộ tham số train, không rải hard-code.
- Mỗi lần train tạo run_id riêng và output nằm trong voices/<voice_id>/model/<run_id>/.
- TrainJobState lưu trạng thái job, checkpoint gần nhất và resume flag; không tự resume nếu người dùng chưa xác nhận.
- validation_only chỉ kiểm tra điều kiện và ghi train_report.json, không train.
- smoke_test chỉ chạy thử tối thiểu khi đã được cấu hình/xác nhận, không thay thế train thật.

Audio Alignment dùng Faster-Whisper để lấy timestamp thật.

TrainAudioPrepService chỉ đưa clip vào tập hợp lệ khi:

- ASR chạy thành công.
- Transcript ASR match text gốc đạt ngưỡng tin cậy.
- Audio clip được cắt theo timestamp ASR thật.
- Audio clip được chuẩn hóa WAV mono theo sample rate train.
- Faster-Whisper package tồn tại trong Python runtime được chọn.
- Faster-Whisper model local tồn tại trong engine cache hoặc HuggingFace cache.

Chia theo tỷ lệ ký tự chỉ là fallback, mặc định tắt.

Clip không đủ chắc chắn phải nằm trong report nghi ngờ, không đưa vào metadata train.

Faster-Whisper runtime validation trả trạng thái rõ ràng:

- package_missing
- model_missing
- cuda_unavailable
- model_load_failed
- ready

Không tự tải model âm thầm.

Mặc định MVP:

- language: vi
- model: small
- device: cuda nếu RuntimeService xác nhận CUDA khả dụng, nếu không thì cpu
- compute_type: tự chọn loại load được với runtime/model hiện có

metadata.list dùng format GPT-SoVITS:

audio_path|speaker|vi|text

AVS-013.6 Quality-First Alignment:

- Ngưỡng alignment được gom trong AlignmentQualityConfig.
- Mặc định similarity_threshold = 90, min_clip_duration = 2.0, max_clip_duration = 10.0, target_clip_duration = 6.0, max_source_error_rate = 0.35, min_valid_segments_per_source = 3, sample_rate = 32000, language = vi.
- Clip dài phải chia tiếp từ timestamp ASR thật, ưu tiên ranh giới câu, sau đó mới chia theo word timestamp.
- Không cắt giữa từ. Ranh giới clip con phải bắt đầu/kết thúc ở word timestamp.
- Mỗi clip con phải được kiểm tra lại similarity, duration, timestamp, transcript, ffprobe, WAV mono, pcm_s16le, 32000 Hz.
- metadata.list chỉ chứa clip valid và được phép train.
- Source file có tỷ lệ suspicious/error vượt ngưỡng sẽ dừng riêng source đó, không dừng toàn batch.
- Source có ít hơn min_valid_segments_per_source được đánh dấu weak_source. Mặc định weak_source không ghi vào metadata train.
- TrainAudioPrepService chỉ phát progress payload cho UI dùng sau, không chứa logic UI.

Runtime Profile:

- RuntimeProfile chuẩn bị cho nhiều cấu hình GPT-SoVITS runtime.
- Một profile chứa profile_id, display_name, engine_version, runtime_path, python_path, hardware_profile, minimum_vram, recommended_vram, status, is_default, pretrained_model_path, compatibility_notes.
- RuntimeProfileService lưu path portable nếu tài nguyên nằm trong app root, và giữ absolute path cho tài nguyên ngoài app.
- Đổi default runtime không được xóa, di chuyển hoặc sửa Voice model cũ.
- Validation runtime dựa trên Python runtime, torch, CUDA/GPU, faster-whisper package, pretrained model path và script GPT-SoVITS thực tế, không hard-code theo tên thư mục.

---

# Generate Pipeline

Text

↓

Normalize

↓

Generate Request

↓

Engine

↓

Adapter

↓

GPT-SoVITS

↓

Audio

↓

Export

---

## AVS-014.6 Generate Architecture

Generate co hai mode:

- Standard Mode: nguoi dung chon mot Voice va mot Variant. Service khong tu doi Variant/Style.
- AI Style Mode: nguoi dung chon mot Voice, Variant scope va Style scope. AI chi duoc chon trong scope da tick hoac all scope.

Generate contract gom:

- GenerateSelectionConfig: mode, voice_id, selected_variant_id, variant scope, style scope, default fallback va speed.
- GenerateRequest: text/text_file/output_file va selection.
- VariantDecision va VariantTimeline: segment_index, text, variant_id, confidence, reason.
- StyleDecision va StyleTimeline: segment_index, text, style_id, confidence, reason.
- GenerateProgress: stage, current_item, total_items, percent, elapsed, ETA, message, level.
- SpeedProfile: presets, custom speed config va method priority.
- TempWorkspace: job_id, kind, root, work_dir va cleanup policy.

AI Style rules:

- Neu khong co Variant hoac Style hop le trong scope thi generate bi chan.
- Fallback chi dung default Variant/Style neu default nam trong allowed scope.
- Neu default khong nam trong scope, service chi chon candidate co confidence cao nhat trong allowed scope, khong vuot scope.
- Neu van khong co candidate hop le, Generate dung.
- Variant/Style timeline chi doi tai boundary an toan: sentence, paragraph, dialogue, scene hoac pause.
- Khong doi Variant/Style giua tu, giua ten rieng hoac giua cau.
- Adjacent chunks co cung Variant/Style duoc merge.

Voice / Variant / Style rules:

- Moi Voice co default_variant_id, mac dinh la `default`.
- Moi Voice co default_style_id, khong hard-code ten Style.
- Voice chi giu Dataset, Model, Runtime, Preview va Metadata.
- Voice khong luu Emotion, Style, Speed hoac Preset.
- Variant khong phai model.
- Variant chi la Generate Profile, Prompt, Style, Speed, Emotion va Parameter.
- Variant khong chua checkpoint, dataset hoac weight.
- Style khong phai Voice.
- Style mo ta cam xuc, cach doc, pacing va expression.
- Style co the dung cho nhieu Voice.

Generate Engine rules:

- Engine chi nhan GenerateRequest va tra GenerateAudio.
- Engine khong quan ly Voice, Variant, Style, Project hoac Workflow.

Speed rules:

- Speed la tham so Generate, khong tao model moi.
- Preset speed: 0.5, 0.75, 1.0, 1.1, 1.2, 1.3, 1.5.
- Custom speed chi hop le trong khoang 0.80 den 1.20.
- Preset la che do dac biet va co the nam ngoai khoang custom.
- Xu ly speed uu tien native engine, sau do high quality time-stretch, cuoi cung moi FFmpeg fallback.
- Khong duoc lam meo pitch khi doi speed.

Temp workspace:

- Temp cho generate/train/alignment nam trong temp/<kind>/<job_id>.
- Output folder chi de final MP3/WAV va optional report.
- SUCCESS xoa toan bo temp.
- PAUSE giu temp, state va progress.
- CANCEL hoi nguoi dung giu hay xoa temp.
- ERROR giu temp, log va state.
- RESUME dung temp cu, khong tao job moi va khong generate lai chunk da hoan thanh.
- Khong ghi temp file vao output folder.

---

## AVS-014.7 Generate UI va Generate Pipeline

Generate UI:

- AudioPage co GenerateOptionsPanel cho Standard Mode va AI Style Mode.
- Standard Mode cho nguoi dung chon mot Variant cu the.
- AI Style Mode cho nguoi dung chon Variant scope va Style scope, hoac All Variants/All Styles.
- UI co Speed, Output Folder, Output Name, Output Format va MP3 bitrate.
- UI chi tao GenerateRequest va goi GenerateService; khong quan ly Engine internals.

Generate pipeline:

- GenerateRequest duoc validate truoc khi generate.
- Voice phai co gpt_model, sovits_model, reference_audio va reference_text hop le.
- ContextAnalysisService chia text thanh segment/context va tao candidate score.
- GeneratePlanningService tao VariantTimeline, StyleTimeline va GeneratePlan.
- GeneratePipelineService generate tung chunk qua EngineManager, retry theo GenerateAudioProfile va merge bang AudioMergeService.
- metadata/report cua job ghi ro chunk, timeline, output, warnings va errors.
- Global progress payload gom stage, current_item, total_items, percent, elapsed, ETA, message va level.

Output va temp:

- Temp generate nam trong temp/generate/<job_id>.
- Output folder chi chua final WAV/MP3 va report.
- Success xoa temp.
- Error giu temp/state/log de resume/debug.
- Resume khong generate lai chunk da co temp output.

Audio profile:

- MP3 bitrate mac dinh 192 kbps.
- Bitrate hop le: 128, 192, 256, 320 kbps.
- Pause mac dinh: comma 120ms, sentence/question/exclamation 300ms, dialogue 250ms, paragraph 500ms, scene 800ms.
- Crossfade mac dinh 20ms.
- retry_count mac dinh 1.
- Neu chunk van loi sau retry thi dung toan job, khong xuat final artifact gia thanh cong.
- Crossfade/pause la config tap trung; natural silence detection va boundary safety duoc tinh chinh tiep o buoc audio quality.

---

## AVS-014.16 Generate Pipeline Foundation

Generate Pipeline foundation tach lop chuan bi khoi inference that.

Chuoi foundation:

Text Source

â†“

Source Snapshot

â†“

Normalize

â†“

Structure Detection

â†“

Document / Chapter / Unit

â†“

Generate Plan

â†“

Manifest / Registry

â†“

Job Queue Prepare

Thanh phan:

- Generate domain model: Request, Session, SourceSnapshot, Document, Chapter, Unit, Attempt, Plan, Manifest, RegistryEntry va Settings.
- GenerateRepository: doc/ghi JSON atomic theo session va registry.
- GenerateTextStructureService: doc pasted text/TXT/DOCX, normalize, detect chapter va split unit; khong sua file goc.
- GenerateSessionService: validation, create session, no-loss reconstruction verifier, request checksum/materialized_at, frozen plan guard, plan/manifest materialization, resume/retry inspection va orchestration foundation.
- GenerateArtifactRecord: planned/reserved/valid unit audio artifact, lineage, reservation va basic WAV validation.
- GeneratePrepareJobWorker: worker Job Queue CPU-light chi chuan bi plan/manifest, khong goi engine synthesize.
- Local API Generate foundation endpoints: readiness, validate request, sessions, plan, chapters, units, attempts, artifacts, manifest, resume/retry va recovery.

Quy tac:

- Session/manifest khong duoc danh dau completed neu chua co output audio that.
- Foundation khong tao WAV/MP3 gia.
- API foundation khong leak runtime/model/checkpoint path.
- Source goc chi doc; snapshot/normalized text nam trong session folder.
- ResourceRequirement cho prepare job la CPU-light, khong GPU.
- Readiness foundation phai phan biet ro planning READY voi execution/output UNAVAILABLE.
- Resume/retry trong AVS-014.16 co orchestration foundation; production execution van UNAVAILABLE neu chua co real handler/provider.
- Test-only WAV provider chi dang ky trong tests de chung minh artifact validation gate, khong xuat hien trong production readiness.
- Generate UI foundation toi thieu nam tren AudioPage; session detail polish rieng, MP3 production output va full audio validation bang ffprobe/codec policy thuoc sprint sau.

---

# API

Một API duy nhất.

Generate Request gồm:

- Voice ID
- Variant
- Speed
- Emotion
- Style
- Similarity
- Pitch
- Volume
- Text

Không tạo API riêng cho từng Voice.

---

# Project Memory

Project Memory là bộ tài liệu giúp đóng/mở lại dự án, đổi máy hoặc đổi phiên Codex mà vẫn giữ đúng ngữ cảnh.

- AGENTS.md: quy tắc làm việc.
- ROADMAP.md: tiến độ dài hạn.
- CURRENT_SPRINT.md: trạng thái ngắn hạn và task tiếp theo.
- docs/DECISIONS.md: quyết định kiến trúc dài hạn.
- CHANGELOG.md: lịch sử thay đổi theo Sprint.
- Git: checkpoint code.

Quy trình khôi phục ngữ cảnh:

Codex mới

↓

Đọc tài liệu dự án

↓

Đọc file liên quan task

↓

Kiểm tra Git status

↓

Tiếp tục Sprint

---

# Quy tắc

- UI không gọi Repository.
- UI chỉ gọi Service.
- Service mới gọi Repository.
- Repository không xử lý nghiệp vụ.
- Core không phụ thuộc UI.
- Engine không phụ thuộc UI.
- Không sửa TXT/DOCX gốc.
- Voice ID không đổi.
- Speed là tham số Generate.
- Một API dùng cho toàn bộ Voice.
- Mọi xử lý dữ liệu phải tạo trong cache.

---

## AVS-014.1 Runtime/Training Smoke Test

- Runtime Profile mặc định có thể trỏ tới GPT-SoVITS runtime ngoài app bằng absolute path đã validate tồn tại.
- Runtime validation phải phát hiện thực tế Python runtime, torch, CUDA/GPU, faster-whisper, GPT-SoVITS scripts và pretrained models; không suy đoán theo tên thư mục.
- Smoke test tối thiểu chạy bằng Python runtime của Runtime Profile, cwd là runtime root.
- Smoke test không sửa metadata.list; nếu metadata chứa audio path tương đối thì resolve theo app root.
- Smoke test ghi stdout/stderr, smoke_output.json, smoke checkpoint và command thực tế vào train report.
- Smoke test chỉ xác nhận runtime/process tối thiểu; full `s1_train.py`/`s2_train.py` vẫn cần dataset train format đầy đủ và tham số train được người dùng chốt.

---

## AVS-014.2 Full Dataset Preparation

- Full Dataset Preparation chạy như một job có progress log, alignment_state và runner_result trong cache.
- Job phải resume từ alignment_state nếu bị dừng, không xử lý lại source đã hoàn thành và không ghi trùng metadata.
- `metadata.list` chỉ chứa valid clip đã qua alignment quality gate.
- Suspicious/error clip nằm trong report, không được dùng train.
- Sau khi runner hoàn tất, metadata phải được validate lại bằng ffprobe:
  - WAV tồn tại.
  - ffprobe đọc được.
  - mono.
  - pcm_s16le.
  - 32000 Hz.
  - transcript không rỗng.
  - không trùng clip.
- Full train GPT-SoVITS chỉ được chạy sau khi người dùng chốt tham số train thật.

---

## AVS-014.3 Suspicious Recovery

- Suspicious Recovery là bước riêng sau Full Dataset Preparation, không thay thế pipeline alignment chính.
- Recovery đọc baseline alignment_state/alignment_report và ghi output vào cache riêng để giữ rollback an toàn.
- Recovery chỉ được đưa clip vào valid khi vẫn đạt quality gate hiện tại:
  - similarity >= 90.
  - timestamp hợp lệ.
  - duration trong ngưỡng.
  - transcript không rỗng.
  - WAV mono, pcm_s16le, 32000 Hz.
- Recovery không dùng ratio fallback cho valid và không hạ threshold toàn cục.
- Với no_alignment_match, recovery chỉ tìm tuần tự quanh vị trí dự kiến, không tìm tự do toàn chương và không ghép ngược thứ tự.
- Với similarity_too_low, recovery ghi lại original_text, asr_text, old_similarity và new_similarity để manual review; không tự approve dưới 90.
- Với source_error_rate_exceeded, recovery review từng segment còn lại; source vẫn được xem là yếu trong report nếu tỷ lệ lỗi cao.
- Full recovery chỉ nên chạy sau preview nhỏ có kết quả tốt.

---

## AVS-014.4 Full Dataset Expansion

- Dataset Workflow co the nhan rieng audio_folder, text_folder va output_folder.
- use_input_folder_as_output van duoc giu cho job don gian; khi audio/text tach rieng thi output_folder la cache/output rieng cua job.
- ProjectConfig luu lua chon cuoi theo Project de mo lai app van giu dung audio folder, text folder, output folder, Voice va Runtime Profile.
- DatasetService.scan_folders() chi tao cap ban dau theo so chuong. Ten file khong duoc dung de tu doi sang chuong khac.
- Alignment van la buoc xac minh noi dung that cua MP3 va Text. Neu noi dung khong khop thi report filename_content_mismatch/suspicious, khong dua vao metadata train.
- FullDatasetPreparationService la service orchestration cho Scan -> Health -> Repair -> Review -> Alignment -> Metadata Validation. Service khong viet logic UI.
- Dataset cu AVS-014.2/014.3 duoc giu trong cache lich su va khong bi ghi de.

## AVS-014.4 Voice / Variant Architecture Foundation

- Voice la danh tinh nguoi noi, gom VoiceID, ten, Dataset, Model, Preview va Metadata.
- Voice khong nen la noi luu Emotion, Style, Speed, Pitch, Volume hoac Preset trong kien truc dai han.
- Mot Voice chi co mot model chinh. Khong train model moi chi de doi toc do, cam xuc, gioi tinh gia lap, tuoi gia lap hoac style doc.
- Variant khong phai model, khong chua dataset va khong chua weight. Variant chi mo ta cach Voice noi.
- Preset chua tham so ky thuat Generate nhu Speed, Pitch, Volume, Similarity, Temperature, TopK, TopP, Pause, Silence, Seed va tham so engine.
- Reference Style la audio tham chieu; mot Variant co the dung 0, 1 hoac nhieu reference audio.
- Text Profile quy dinh xu ly van ban: ngat cau, pause, doc so, ngay thang, tien, URL, email va ky hieu.
- Generate Request duy nhat gom VoiceID, VariantID, PresetID, ReferenceStyleID, TextProfileID, Engine va Text.
- Engine chi sinh audio. Engine khong quan ly Voice, Variant, Preset, Reference Style hoac Text Profile.
- Engine Profile chiu trach nhiem map tham so chung sang tham so rieng cua tung Engine.

---

## AVS-014.5 Workspace Compatibility

- Dataset Workflow ho tro hai source mode:
  - same_folder: audio_folder va text_folder cung tro vao workspace/<Voice Name>/.
  - separate_folders: audio_folder va text_folder la hai thu muc rieng.
- same_folder la che do mac dinh cho Project/Voice cu de khong bat nguoi dung tach lai du lieu.
- App khong di chuyen, khong doi ten va khong sua file goc trong workspace.
- UI sau nay chi can hien mot folder picker khi source_mode = same_folder, va hien MP3/Text picker rieng khi source_mode = separate_folders.

## AVS-014.5 Automatic Review

- Auto Review khong dung Approve All.
- test_version, missing_audio, missing_text va invalid_filename duoc ignored: khong train nhung khong chan toan batch.
- broken_file, empty_file, empty_content va filename_content_mismatch duoc rejected: khong train.
- Dataset item hop le da duoc DatasetService tao truoc do; file ignored/rejected khong nam trong items dua vao Alignment.
- Alignment resume luu completed_sources trong alignment_state.json va metadata.list chi ghi valid clips khong trung.

## AVS-014.8 Full Alignment Completion

- Full Alignment co the resume tu `alignment_state.json` va tiep tuc source con lai, khong tao job moi neu checkpoint hien co hop le.
- `alignment_state.json` la source of truth cho valid/suspicious/errors sau khi job dai hoan tat.
- Khi finalize, `metadata.list` phai duoc rebuild tu toan bo valid clips trong state, khong duoc tin metadata cu neu so dong lech state.
- Ghi metadata bang atomic write de tranh file hong neu process bi dung giua chung.
- Metadata final chi chua clip trainable:
  - metadata_enabled = true.
  - khong suspicious.
  - khong rejected/ignored.
  - khong duplicate audio path.
- Dataset Quality Report truoc Train gom summary, duration distribution, similarity distribution, top/bottom clips, skipped sources, high-error sources va metadata validation.
- Reference Audio candidates duoc de xuat tu clip valid co similarity cao, duration phu hop va transcript ro; nguoi dung van phai nghe/chot reference cuoi.
- Train validation_only la bat buoc truoc khi goi `s1_train.py`/`s2_train.py`.

## AVS-014.9 Runtime Training Profile

Runtime Training Profile nam trong Settings va la lop cau hinh truoc Train.

Profile modes:

- Auto: mac dinh, app detect hardware/runtime va chon cau hinh an toan.
- Compatibility: uu tien on dinh, VRAM thap, batch_size 1, num_workers 0.
- Performance: chi chon cau hinh cao hon khi VRAM/CPU/RAM/runtime validation du.
- Custom: nguoi dung tu chinh runtime profile, compute, batch size, workers, VRAM profile, epochs, save interval, pretrained va resume policy.

Auto Detect Hardware:

- Phat hien GPU, VRAM, CUDA, CPU threads, RAM, Python runtime va Runtime Profile.
- Khong chi dua vao ten GPU; uu tien VRAM, runtime compatibility va validation that.
- Neu phan cung/runtime thay doi, Auto co the tinh lai profile; Custom cu van duoc luu theo Project.

App-managed runtime copy:

- Khong sua runtime GPT-SoVITS goc.
- Neu runtime goc khong ho tro tham so can dung truc tiep, app tao copy trong `voices/<voice_id>/model/<run_id>/runtime_copy/`.
- GPT copy config `s1longer.yaml` va chi thay batch_size, num_workers, epochs, save interval theo profile.
- SoVITS copy `s2v2Pro.json` va `s2_train.py`; neu script hard-code worker thi chi sua ban copy, khong sua runtime goc.
- Ban copy phai compile truoc khi train va ghi report checksum/diff summary.

Voice/Variant:

- AVS-014.9 chi train mot model chinh cho Voice 0001.
- Variant khong chua checkpoint, dataset hoac weight.
- Khong train model rieng cho Variant, style, emotion, tuoi/gioi tinh gia lap.
- VoiceID -> mot model chinh -> khong gioi han Variant/Preset/Reference Style.

Runtime & Training Help UI:

- Huong dan Runtime & Training duoc tach vao RuntimeTrainingHelpService de UI va test dung chung.
- SettingsPage chi hien thi noi dung, tooltip va dialog huong dan; logic detect/profile van nam trong service.
- Noi dung huong dan phai bang tieng Viet, giai thich cong dung, khi nen dung, khi khong nen dung, anh huong den toc do, do on dinh va VRAM/RAM.
- Canh bao cho CUDA, Runtime, VRAM/OOM va pretrained model phai hien thi cau de hieu truoc, ma loi chi la chi tiet ky thuat.
- Hardware Summary sinh tu du lieu detection/runtime profile hien tai, khong hard-code ten GPU cu the.
- Huong dan doi may nam trong dialog chi tiet va co the sao chep de nguoi dung luu lai.

GPT stage command readiness:

- `s1_train.py` runtime that chi nhan `-c/--config_file`; tham so train phai nam trong YAML copy do app quan ly.
- `metadata.list` final cua Alignment la dau vao trainable cua app, nhung truoc khi goi GPT stage can co artifact/config ma GPT-SoVITS yeu cau nhu `train_semantic_path`, `train_phoneme_path`, `output_dir`, `half_weights_save_dir` va `exp_name`.
- Neu config copy thieu cac key tren, command preview duoc phep tao de review nhung khong duoc danh dau ready-to-run va khong duoc bat dau Train that.

---

## AVS-014.10 Bootstrap, Readiness va Local API

AI Voice Studio co ba lop runtime rieng:

1. Bootstrap Launcher.
2. Main Desktop App.
3. Local API `/api/v1`.

### Bootstrap Launcher

- Bootstrap la entrypoint an toan cho ban desktop/phat hanh sau nay.
- Bootstrap khong import PySide6 som.
- Bootstrap dung BootstrapService de kiem tra OS, Python, dependency, quyen ghi, dung luong dia va Feature Readiness.
- Neu app_shell san sang, Bootstrap co the mo Main App.
- Neu thieu dependency UI hoac runtime quan trong, Bootstrap dua ra First-Run Setup status/report thay vi de app crash bang stack trace tho.

### Runtime Environment Manager

RuntimeEnvironmentManager la lop detect moi truong dung chung:

- Python dang chay app.
- Package du an: PySide6, python-docx, faster-whisper, pytest.
- FFmpeg/FFprobe.
- NVIDIA/GPU thong qua nvidia-smi neu co.
- GPT-SoVITS Runtime Profile hien tai.

Service nay chi phat hien va report; khong tu cai dependency, khong tu sua runtime GPT-SoVITS.

### Feature Readiness

FeatureReadinessService gom trang thai tinh nang theo ba muc:

- available: san sang dung.
- degraded: app van mo duoc nhung tinh nang bi gioi han.
- blocked: tinh nang khong du dieu kien chay.

Main App va Local API dung chung status nay de hien che do gioi han, khong moi noi tu detect rieng.

### Local API

Local API MVP dung Python stdlib HTTP server thong qua LocalApiService.

Ly do:

- Khong them dependency khi Python chuan da du cho API localhost MVP.
- API missing khong duoc lam chet Bootstrap/Main App.
- Sau nay neu chuyen sang FastAPI, contract service van giu tuong thich.

Local API mac dinh:

- host: `127.0.0.1`.
- token required: tat ca endpoint tru `/api/v1/health`.
- CORS rong khong duoc bat mac dinh.
- Job output chi nam trong output do app quan ly.

Endpoint nhom chinh:

- Health: `/api/v1/health`.
- Readiness/Capabilities: `/api/v1/readiness`, `/api/v1/capabilities`.
- Voice Catalog: `/api/v1/voices`, `/api/v1/voices/{voice_id}`, `/api/v1/voices/{voice_id}/variants`, `/api/v1/voice-catalog`.
- Generation Job: tao job, xem status, cancel va lay result.

Local API chi goi service chinh thuc:

- VoiceCatalogService.
- GenerationJobService.
- FeatureReadinessService.

API khong goi truc tiep runtime folder, script GPT-SoVITS hoac checkpoint.

### Voice/Variant Catalog qua API

Voice Catalog tra ve thong tin an toan:

- voice_id.
- display_name.
- status/readiness.
- variants.
- missing fields neu Voice chua san sang.

Khong tra ve:

- duong dan GPT model.
- duong dan SoVITS model.
- duong dan runtime/pretrained/checkpoint.

Variant Catalog giu dung kien truc da chot: Variant la Generate Profile/Prompt/Style/Speed/Emotion/Parameter, khong phai model.

### Generation Job qua API

GenerationJobService quan ly job API trong `workspace/api_jobs/<job_id>/`:

- request.json.
- state.json.
- logs/.
- temp/.
- output/.

Trang thai job:

- queued.
- preparing.
- generating.
- post_processing.
- completed.
- failed.
- cancelled.
- interrupted.

Trong MVP nay, job chi duoc tao queued khi Voice da ready. Neu Voice thieu model/reference, job failed ro ly do va khong tao audio gia thanh cong.

### Security

- Token khong ghi vao log job.
- Health endpoint khong can token de app video kiem tra server song.
- Tat ca API con lai can Bearer token hoac `X-AVS-API-Key`.
- Khong expose duong dan nhay cam runtime/model/checkpoint.
- Path traversal khong duoc chap nhan cho output/result.

### Settings API

SettingsPage co nhom `API & Tich hop` de:

- bat/tat Local API.
- chon host/port.
- bat/tat auto start.
- xem/sao chep token.
- tao token moi.
- sao chep URL Voice Catalog.
- kiem tra ket noi.

UI chi dieu khien service/config, khong chua logic API routing.

---

## AVS-014.11 Voice DNA / Reading Style Profile

### Muc tieu

Voice DNA trong sprint nay la foundation cho du lieu tham chieu phong cach doc, khong phai model moi va khong thay the Voice/Speaker Profile.

### Tach lop du lieu

- Speaker Profile/Voice: danh tinh nguoi noi, dataset, model, runtime, preview va metadata.
- Reading Style Profile: prosody, rhythm, pause, pacing, expression va reference indexes.
- Variant: Generate Profile, khong chua checkpoint, dataset hoac weight.
- Style Profile co ID rieng dang `style_000001` va co the dung lai cho nhieu Voice.

### Service boundary

- UI chi goi StyleProfileService va service lien quan.
- Repository chi doc/ghi du lieu tren dia.
- Local API chi goi service chinh thuc, khong doc truc tiep folder runtime/model.
- Generate engine chua ap dung Style Profile that thi validation phai bao ro, khong silently ignore.

### Package `.avstyle`

`.avstyle` la ZIP package portable gom manifest, style_profile.json, prosody, indexes, references/manifest.json va checksums.

Mac dinh khong export:

- MP3 goc.
- Dataset goc.
- Model/checkpoint.
- Token.
- Absolute path may ca nhan.

### Local API moi

- `GET /api/v1/style-profiles`
- `GET /api/v1/style-profiles/{style_profile_id}`
- `GET /api/v1/style-profiles/{style_profile_id}/readiness`
- `GET /api/v1/voices/{voice_id}/style-profile`

### UI Layout Foundation

Them component nen:

- PageHeader.
- SectionCard.
- StatusBadge.
- EmptyState.
- SettingsRow.

Trang `Phong cach doc / Voice DNA` cung cap list/detail, empty state, wizard tao profile, import/export, backup va readiness check o muc foundation.

---

## AVS-014.12 Training Reference Architecture

TrainingPage tach ba loai du lieu:

- Training Dataset: source audio/text, scan, health, repair, review, alignment, metadata va train readiness.
- Reading Style Profile / Voice DNA: du lieu phong cach doc co ID rieng, owner la Style Profile domain.
- Speaker Reference: audio/transcript tham chieu de clone chat giong, owner la Voice/Speaker Reference domain.

TrainingPage co ba reference mode loai tru nhau:

- `app_style_profile`: dung Style Profile co san.
- `create_style_profile_from_audio_text`: tao draft/pending Style Profile tu audio + text, khong tao Voice DNA gia.
- `speaker_reference_only`: chi dung audio tham chieu clone chat giong.

`TrainingReferenceConfig` luu lua chon workflow/reference theo cach migration-safe. Mode inactive duoc giu draft nhung khong resolve vao engine.

`VoiceConfig.reference_audio` va `VoiceConfig.reference_text` van duoc giu de tuong thich Generate/GPT-SoVITS cu. `speaker_reference` moi chi bo sung contract ro hon va co the mirror legacy reference khi load voice cu.

Rename:

- Voice display name co the doi, Voice ID khong doi.
- Style Profile display name co the doi, Style Profile ID khong doi.
- Rename khong doi checkpoint, Variant link hoac Style Profile folder.

Scroll/responsive:

- `ContentScrollArea` va `ScrollablePage` la nen chung cho page dai.
- TrainingPage dung scroll de noi dung dai khong ep MainWindow giu kich thuoc lon.

---

## AVS-014.13 Project & Workspace Manager

Project Manager tach ro:

- Project ID: khoa ky thuat bat bien, dung cho lien ket noi bo/API.
- Project display_name: ten hien thi cho nguoi dung, co the doi.
- Project storage folder: Project moi uu tien ID-based, vi du `projects/project_000001/`.
- Legacy Project folder theo ten van load duoc, khong tu rename folder that.

Application Workspace:

- `projects/`: project roots va registry.
- `workspace/`: external/source workspace hien tai, vi du `workspace/Thu Minh/`.
- `cache/`, `temp/`, `output/`, `logs/`: du lieu sinh ra theo domain.

Project Workspace:

- `project.json`.
- `text/`.
- `audio/`.
- `export/`.
- `cache/`.
- `logs/`.
- `backups/` khi co backup.

Project Registry:

- Chi luu metadata du de tim Project: project_id, display_name, root_path, status, archive_state, last_opened_at, favorite, health_state, missing.
- Khong chua toan bo du lieu Project.
- Registry ghi atomic.
- Project missing khong bi xoa khoi registry.

Lifecycle:

- Create tao Project ID moi va folder ID-based.
- Open cap nhat last_opened_at, recent va AppContext.current_project.
- Close clear current project, khong xoa du lieu.
- Switch clear stale current project truoc khi open Project moi.
- Rename chi doi display_name.
- Duplicate tao Project ID moi, mac dinh chi copy config/metadata an toan.
- Archive chi doi status/archive_state, khong xoa folder.
- Restore Archive doi status ve active.

Export/Import:

- Export mac dinh la package nhe co manifest va project.json.
- Import validate manifest va chan path traversal/absolute path.
- Neu import as new, tao Project ID moi va khong ghi de Project cu.
- Khong export secret, token, runtime command hoac absolute path nhay cam.

Backup/Restore:

- Backup khac Export: dung de khoi phuc cung moi truong.
- Backup luu manifest, reason, timestamp va config can thiet.
- Restore tao safety backup truoc khi ghi lai file.

Validation/Repair:

- Validation kiem tra project.json, Project ID, required folders va registry mismatch.
- Repair chi sua loi an toan, hien tai tao lai folder thieu va backup truoc repair.
- Khong tao Voice/Style/Dataset gia.

API:

- Local API co read-only endpoints Project/Workspace.
- API khong tra duong dan runtime/model/checkpoint/secret.

## AVS-014.13.1 Reference Data Vault

Reference Vault la kho managed reference do app quan ly, mac dinh nam trong `workspace/reference_vault/`.

Thanh phan:

- `ReferenceAsset`: metadata cua audio/text/manifest/report managed asset.
- `ReferenceRegistry`: index asset_id, checksum, managed_relative_path, health va usage.
- `ReferenceVaultService`: atomic import, checksum, deduplication, verify va relink.

Nguyen tac:

- File goc ben ngoai app la provenance/fallback, khong phai ban luu ben vung duy nhat.
- Managed path serialized la relative path tu vault root.
- Deduplication dua tren checksum + asset_type + extension, khong dua vao filename.
- Rename Project/Voice/Style Profile khong lam mat reference.
- Archive Project khong xoa reference.
- Import/export/backup standard co the gom managed reference assets.
- Legacy `reference_audio` va `reference_text` van load.
- Resolver uu tien asset ID neu co, fallback legacy path neu chua migrate.

---

## AVS-014.14 Job & Queue System

Job & Queue la ha tang dung chung cho tac vu dai. UI khong chay tac vu dai truc tiep; UI tao Job hoac goi service, Worker chay qua JobRunner va phat event/progress.

Thanh phan:

- JobModel: identity, state, owner IDs, payload/result JSON-safe, progress, ETA, retry, dependency va recovery.
- JobStateMachine: validate transition hop le.
- JobRepository: persistent JSON trong `workspace/jobs`, atomic save va corrupt quarantine.
- JobQueueService: enqueue/dequeue/list, priority, idempotency, dependencies va control request.
- JobRunner: chay mac dinh mot job tai mot thoi diem, khong parallel GPU task.
- BaseJobWorker: execute, pause/resume/cancel cooperative, progress, log, heartbeat, checkpoint va cleanup.
- JobLogService: moi job co log rieng va UI/API co the doc tail.

Recovery:

- queued giu queued qua restart.
- paused giu paused.
- running/pause_requested/resume_requested/cancel_requested/cancelling cu thanh interrupted.
- corrupt job record duoc quarantine, khong lam crash app.
- auto-resume interrupted mac dinh tat.

UI/API:

- Trang Cong viec/Hang doi hien summary, list, detail, log tail va cac action Pause/Resume/Cancel/Retry/Priority.
- Dashboard chi hien summary nhe.
- Local API read-only cho jobs, queue va logs.

Data safety:

- Worker khong sua UI truc tiep.
- Cancel cooperative, khong kill thread cuong buc.
- Cancel/Retry khong duoc danh dau completed khi output chua hop le.
- Sprint nay chua Train/Generate that.
# AVS-014.15 Resource Manager

Resource Manager la lop ha tang nam giua Job Queue va cac workflow nang.

Luon di theo chuoi:

Job -> ResourceRequirement -> ResourceDecision -> ResourceLease -> Worker.

Thanh phan:

- HardwareDetectionService: doc CPU/RAM/Disk/FFmpeg/FFprobe/NVIDIA GPU bang cach nhe va co timeout.
- ResourceSnapshotService: tao snapshot hien tai, co TTL de tranh poll qua day.
- ResourcePolicyService: giu policy tap trung cho max job, max GPU job va reserve RAM/VRAM/Disk.
- ResourceDecisionService: tra ready, waiting_resource hoac unsupported kem reason/remediation.
- ResourceLeaseManager: cap/release/cleanup lease persistent trong `workspace/jobs/resources`.
- ResourceMonitorService: tong hop hardware, snapshot, policy, leases va waiting jobs cho UI/API.

Resource Manager khong train, generate, stress test, kill process, cai driver, tai model hoac sua GPT-SoVITS runtime.

---

## Resource Safety Hardening Phase 1

Phase 1 chi them foundation policy/config cho Resource Safety Hardening.

Thanh phan:

- `ResourcePolicy` schema v2 theo huong additive, van giu field cu.
- `ResourcePolicyService` la facade chung cho load, save, migration, validation, fallback va resolve.
- `ResolvedResourcePolicy` la effective policy cho v2, co fingerprint deterministic.

Luon resolve theo chuoi:

Persisted Policy

-> Schema Defaults

-> Migration Result

-> Validated Runtime Override duoc phep

-> ResolvedResourcePolicy

Nguyen tac Phase 1:

- Global Application Policy la scope duy nhat.
- Khong co Project/Voice override.
- Feature mode hop le: disabled, monitor_only, enforced.
- Initial modes la monitor_only, rieng job runner safety integration disabled.
- Khong mode nao tu dong enforced.
- Backup duoc tao truoc migration save dau tien.
- Corrupt primary khong bi ghi de khi fallback.
- Neu fallback tu backup hoac built-in policy, enforcement modes phai disabled va observability chi monitor_only.
- Runtime override khong duoc persist ngam.
- Existing runtime/scheduling consumers van dung projection tuong thich qua `load()` trong Phase 1.
- Effective v2 policy cho quan sat/Phase sau duoc lay qua `resolve()`.

Ranh gioi:

- Khong doi Job Queue scheduling.
- Khong doi ResourceDecisionService runtime behavior.
- Khong doi ResourceLeaseManager lifecycle.
- Khong doi thread count, batch runtime hoac CPU fallback runtime.
- Khong cancel/terminate process.
- Khong kich hoat runtime pressure guard moi.
- Khong train/generate/goi GPT-SoVITS runtime.

---

## Resource Safety Hardening Phase 2

Phase 2 chi them snapshot validation va Resource Decision v2 dang shadow/monitor-only.

Thanh phan:

- `ResourceSnapshot` co provider status, validation status, reason codes va freshness age.
- `ResourceSnapshotValidation` mo ta status tong va status rieng RAM/GPU/Disk.
- `ResourceRequirement` co workload class va uoc luong peak RAM/VRAM/Disk theo huong additive.
- `ResourceDecisionObservation` la structured shadow result gan vao `ResourceDecision.shadow_observation`.

Nguyen tac Phase 2:

- Actual Queue decision van la legacy decision tu `ResourceDecision.status`.
- Shadow decision khong duoc block queue, doi job state, doi scheduling, doi lease, doi CPU fallback, thread, batch, Runtime Guard hoac Process Supervisor.
- Shadow decision dung `ResourcePolicyService.resolve()` va `ResolvedResourcePolicy`.
- Actual legacy decision tiep tuc dung `ResourcePolicyService.load()` projection tuong thich.
- Unknown/invalid/stale snapshot khong duoc coi la du tai nguyen trong shadow result.
- Light workload khong bi block chi vi GPU unknown neu khong requires_gpu.
- Heavy workload co the WOULD_BLOCK/WOULD_WAIT/CONFIRMATION_REQUIRED trong shadow observation, nhung job that van chay theo legacy behavior.

Ranh gioi:

- Khong doi Job Queue scheduling.
- Khong doi ResourceLeaseManager lifecycle.
- Khong kich hoat enforcement.
- Khong kill/cancel process.
- Khong train/generate/goi GPT-SoVITS runtime.

---

## Resource Safety Hardening Phase 3

Phase 3 chi them Lease Lifecycle v2 o dang shadow/monitor-only.

Thanh phan:

- `ResourceLeaseV2` mo hinh hoa lease lifecycle v2 voi lease_id, job_id, resource_kind, owner/runner, workload_class, acquired_at, last_renewed_at, expires_at, ttl, status, policy_fingerprint, process_identity, metadata/provenance va schema_version.
- `ResourceLeaseObservation` la structured observation cho actual lease state, shadow lease state, shadow action, reason codes, flags would_* va policy fingerprint.
- `ResourceLeaseShadowEvaluator` tinh toan acquire/renew/release/expiry/stale/reconciliation/duplicate theo clock inject duoc, khong sleep va khong dung process/GPU that.
- `ResourceLeaseManager.shadow_observations()` va `shadow_observation_for_job()` chi doc lease legacy va sinh observation, khong goi `cleanup_stale()`, khong renew/release/save actual lease.

Nguyen tac Phase 3:

- Actual lease legacy van la source runtime.
- Shadow lease v2 dung `ResourcePolicyService.resolve()` va `ResolvedResourcePolicy`.
- Policy lease v2 doc tu single source of truth: `resource_lease_v2_mode`, max job/GPU job, `lease_ttl_seconds`, `lease_renew_interval_seconds`, `stale_lease_handling_mode` va policy fingerprint.
- Corrupt/unavailable legacy lease store khong crash va khong bi ghi de trong observation path.
- Reconciliation chi la proposed action: WOULD_ACQUIRE, WOULD_RENEW, WOULD_RELEASE, WOULD_EXPIRE, WOULD_MARK_STALE, WOULD_RECONCILE, WOULD_SKIP hoac WOULD_BLOCK_DUPLICATE.

Ranh gioi:

- Khong doi Job Queue scheduling.
- Khong doi JobRunner behavior.
- Khong renew/release/cleanup actual lease trong monitor-only observation.
- Khong kich hoat Process Supervisor, Runtime Guard, Thread Budget, kill-tree, pause/cancel/retry behavior moi.
- Khong train/generate/goi GPT-SoVITS runtime.

---

## Resource Safety Hardening Phase 4

Phase 4 them Lease Lifecycle v2 enforcement nhung chi sau activation flag.

Thanh phan:

- `resource_lease_v2_mode` co mode chinh: disabled, monitor_only, enforce; literal `enforced` cu duoc xem la legacy alias.
- `ResourceLeaseManager` resolve policy qua `ResourcePolicyService.resolve()` va chi dung v2 enforcement khi policy effective la `enforce`.
- Acquire v2 atomic/idempotent cho cung job/owner/resource, deny owner mismatch, duplicate/conflict va concurrency theo policy.
- Renew/release v2 yeu cau lease_id/job_id/owner khop; release idempotent voi lease da released.
- Reconcile v2 xu ly expired, stale, duplicate va unknown store theo huong fail-safe, non-destructive voi corrupt/unavailable store.
- Lease store ghi schema_version 2 bang temp file + replace, cleanup temp va khong ghi de corrupt store trong enforce path.

Nguyen tac Phase 4:

- disabled va monitor_only giu legacy/Phase 3 behavior.
- Default production van monitor_only; khong tu bat enforcement khi migration/load policy.
- Stable reason codes gom acquire, renew, release, expired, stale, duplicate, owner/process/policy mismatch, store corrupt/unavailable va reconciliation.
- JobRunner chi truyen them job_id/owner khi release de enforce co du thong tin xac thuc; legacy release van tuong thich.

Ranh gioi:

- Khong them Process Supervisor, kill-tree, Runtime Guard action hoac Thread Budget enforcement.
- Khong dung process identity provider production de kill/restart process.
- Khong train/generate/goi GPT-SoVITS runtime.

---

## Resource Safety Hardening Phase 5

Phase 5 them Process Supervisor va kill-tree foundation, mac dinh monitor-only.

Thanh phan:

- `ProcessIdentity`: identity khong chi dua vao PID, gom pid/start time/parent/job/lease/owner/executable/command fingerprint/workload/resource/group/session/policy fingerprint.
- `ProcessSupervisorObservation`: structured shadow observation cho process state, tree, identity validity, orphan/stale flags va proposed action.
- `ProcessProvider`: abstraction cho process snapshot va list process; tests dung fake provider deterministic.
- `ProcessSupervisor`: registry atomic, process tree discovery, identity validation, orphan/restart recovery observation va shutdown plan simulated.

Policy Phase 5 lay tu `ResourcePolicyService.resolve()`:

- `process_supervisor_mode`;
- `graceful_shutdown_timeout_seconds`;
- `terminate_timeout_seconds`;
- `kill_tree_timeout_seconds`;
- `process_identity_required`;
- `orphan_handling_mode`;
- `process_observation_ttl_seconds`;
- policy fingerprint.

Nguyen tac Phase 5:

- Default `process_supervisor_mode` van monitor_only.
- disabled khong supervisor action.
- monitor_only chi quan sat, sinh WOULD_* action va audit.
- enforce chi la gate/contract fail-safe trong Phase 5, khong production kill.
- Unknown, permission denied, provider unavailable, tree incomplete hoac identity mismatch deu defer/non-destructive.

Ranh gioi:

- Khong goi `taskkill`, `os.kill`, `psutil.Process.kill` trong production path hay tests.
- Khong thay JobQueue scheduling, retry, pause/cancel, Job final state, Generate/Training execution.
- Khong bat Runtime Guard action hay Thread Budget enforcement.
