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
