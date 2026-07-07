# AI Voice Studio - Development Rules

## General

- Luôn ưu tiên phiên bản đơn giản nhất.
- Không tối ưu sớm.
- Mọi tính năng phải có thể mở rộng.
- Không tạo code phức tạp nếu chưa cần.

---

## Architecture

Luôn tách riêng:

- UI
- Backend
- Engine
- Voice
- Reader
- Trainer

Không được viết lẫn.

---

## Code

- Không hardcode đường dẫn.
- Không hardcode tên Voice.
- Không hardcode Engine.
- Không hardcode Model.

Tất cả phải đọc từ cấu hình.

---

## Project

Một thư mục trong datasets tương ứng với một Voice.

Ví dụ

datasets/

Thu Minh/

Lan Anh/

Nam Trầm/

Ứng dụng tự quét dữ liệu.

Không yêu cầu người dùng chọn từng file.

---

## Dataset

Trong mỗi Dataset có thể chứa:

- mp3
- docx
- txt

Ứng dụng tự ghép theo tên.

File không ghép được:

- bỏ qua
- ghi log

Không được làm treo chương trình.

---

## Development

Luôn ưu tiên:

1. Chạy được.
2. Dễ đọc.
3. Dễ bảo trì.
4. Dễ mở rộng.

Không viết code "thông minh" nhưng khó hiểu.