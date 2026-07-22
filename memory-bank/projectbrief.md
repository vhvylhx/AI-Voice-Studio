# Project Brief — AI Voice Studio

## Mục tiêu sản phẩm

AI Voice Studio là ứng dụng Desktop Windows dùng Python và PySide6, hướng tới phần cứng NVIDIA GPU. Ứng dụng quản lý dữ liệu, Voice, Style, Project, Job và các workflow Train/Generate theo kiến trúc có thể mở rộng cho nhiều engine.

## Nguyên tắc sản phẩm

- Voice có immutable `voice_id`; tên hiển thị chỉ là metadata.
- Một Voice có một model chính; Variant, Preset và Style không phải model/checkpoint.
- `speed` là tham số Generate, không dùng để tạo model Voice mới.
- UI chỉ gọi Page/Controller hoặc Service; UI không gọi Engine/Runtime trực tiếp.
- Job dài phải bền vững, có immutable IDs, progress, resource requirement và lifecycle rõ ràng.
- File TXT, DOCX, audio nguồn và dữ liệu thật của người dùng không được sửa hoặc ghi đè.
- Capability production phải phản ánh runtime, asset, validation và real smoke thực tế; fake/test-only không được làm trạng thái thành `READY`.

## Kiến trúc bắt buộc

```text
UI
→ Page/Controller
→ Service
→ Job Queue
→ Engine Manager
→ Engine Adapter
→ Runtime
```

## Phạm vi engine

GPT-SoVITS là engine chính hiện tại. Kiến trúc phải hỗ trợ mở rộng engine khác, bao gồm engine tiếng Việt riêng khi cần. Tiếng Việt (`vi`) không được fallback sang GPT-SoVITS hoặc language mode khác nếu chưa có contract hợp lệ.