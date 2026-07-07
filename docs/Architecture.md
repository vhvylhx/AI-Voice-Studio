# AI Voice Studio - Architecture

## Mục tiêu

AI Voice Studio là phần mềm quản lý toàn bộ quy trình tạo audiobook AI.

Không phụ thuộc engine.

Có thể mở rộng nhiều AI Engine.

---

# Kiến trúc

UI
↓
Pages
↓
Services
↓
Repositories
↓
Core

Engine hoạt động độc lập thông qua Plugin.

---

# Core

- Config
- Logger
- Event Bus
- App
- Paths

Không phụ thuộc UI.

---

# Services

Chứa toàn bộ nghiệp vụ.

Ví dụ:

WorkspaceService

SettingsService

QueueService

VoiceService

RuleService

ProjectService

...

Service không truy cập trực tiếp giao diện.

---

# Repository

Chỉ đọc / ghi dữ liệu.

Không xử lý logic.

Ví dụ

settings.json

project.json

rule.json

...

---

# Pages

Dashboard

Workspace

Voice

Queue

Settings

...

Chỉ hiển thị dữ liệu.

Không xử lý nghiệp vụ.

---

# Widgets

Widget dùng lại nhiều nơi.

Ví dụ

InfoCard

ProgressBar

VoiceCard

...

---

# Engine

Engine là Plugin.

Ví dụ

GPT-SoVITS

FishSpeech

CosyVoice

XTTS

...

Engine phải implement cùng interface.

Không sửa UI khi thêm Engine.

---

# Workspace

workspace/

└── Thu Minh/
    ├── 001.docx
    ├── 001.mp3
    ├── 002.docx
    ├── 002.mp3

Mỗi thư mục = 1 Voice Dataset.

---

# Quy tắc

UI không gọi Repository.

UI chỉ gọi Service.

Service mới gọi Repository.

Core không phụ thuộc module nào.