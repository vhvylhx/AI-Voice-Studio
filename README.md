# AI Voice Studio

## Giới thiệu

AI Voice Studio là ứng dụng Windows giúp tạo truyện audio bằng AI.

Dự án được phát triển với mục tiêu thay thế toàn bộ quy trình tạo truyện audio thủ công bằng một ứng dụng duy nhất.

Sau khi đã có model giọng, ứng dụng có thể hoạt động hoàn toàn trên máy tính mà không phụ thuộc vào dịch vụ TTS trực tuyến.

---

## Mục tiêu

- Clone giọng đọc chất lượng cao.
- Quản lý nhiều giọng.
- Đọc trực tiếp DOCX.
- Đọc TXT.
- Dán văn bản trực tiếp.
- Đọc cả thư mục.
- Xuất MP3.
- Batch nhiều chương.
- Dễ sử dụng.
- Dễ mở rộng.
- Dễ bảo trì.

---

## Công nghệ

Ngôn ngữ:

- Python

Giao diện:

- PySide6 (Qt)

Engine đầu tiên:

- GPT-SoVITS

Âm thanh:

- FFmpeg

Thiết kế theo hướng nhiều Engine để sau này có thể thay GPT-SoVITS bằng Engine khác mà không phải viết lại ứng dụng.

---

## Kiến trúc

UI

↓

Backend

↓

Engine

↓

Voice Models

---

## Cấu trúc dữ liệu

datasets/

- Mỗi thư mục đại diện cho một bộ dữ liệu huấn luyện.

Ví dụ:

datasets/

- Thu Minh/
- Giọng A/
- Giọng B/

Trong mỗi thư mục sẽ chứa:

- mp3
- docx

Ứng dụng sẽ tự ghép file theo tên.

Các file không ghép được sẽ tự bỏ qua và ghi log.

---

voices/

Lưu model sau khi train.

Không chứa dữ liệu gốc.

---

output/

Lưu MP3 sinh ra.

---

## Nguyên tắc phát triển

Ưu tiên:

- Đơn giản.
- Ổn định.
- Không hardcode.
- Dễ mở rộng.
- Hạn chế thao tác thủ công.

Mọi tính năng mới phải hướng tới việc giảm thao tác của người dùng và gom toàn bộ quy trình tạo truyện audio vào AI Voice Studio.