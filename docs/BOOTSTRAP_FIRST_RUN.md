# Bootstrap Launcher và First-Run Setup

Mục tiêu của Bootstrap là giúp người dùng mở AI Voice Studio trên máy Windows mới mà không thấy stack trace thô.

## Luồng khởi động

```text
AI-Voice-Studio.exe
        |
        v
Bootstrap Launcher
        |
        +-- thiếu môi trường -> First-Run Setup
        |
        +-- đủ môi trường -> Main Application
```

## Bootstrap kiểm tra

- Windows.
- Quyền đọc/ghi thư mục app.
- Dung lượng ổ đĩa.
- Python App Runtime.
- PySide6 cho UI.
- FFmpeg/ffprobe.
- Runtime GPT-SoVITS.
- CUDA/GPU nếu có.
- Cấu hình ứng dụng.

## Khi thiếu PySide6

Bootstrap vẫn chạy vì không import PySide6. Người dùng thấy thông báo tiếng Việt và hướng dẫn:

```powershell
python -m pip install -r requirements.txt
```

## Chế độ ứng dụng

- Full Mode: đủ môi trường chính.
- Limited Mode: thiếu dependency tùy chọn, ví dụ DOCX hoặc Alignment.
- Setup Required Mode: thiếu dependency bắt buộc để mở UI.

## Entry point prototype

```powershell
python .\src\bootstrap.py
```

Khi đóng gói EXE production, entry point nên trỏ vào Bootstrap trước, không trỏ thẳng vào `src/main.py`.

## Ghi chú đóng gói

Sprint hiện tại chưa bắt buộc build EXE production. Build spec chính thức cần bổ sung sau khi App Runtime ổn định.
