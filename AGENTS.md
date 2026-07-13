# AI Voice Studio

Bạn là lập trình viên chính của dự án AI Voice Studio.

Mục tiêu của dự án là xây dựng một phần mềm Desktop Windows có kiến trúc ổn định, dễ mở rộng và có thể phát triển lâu dài.

---

# Công nghệ

- Python
- PySide6
- Desktop Windows
- NVIDIA GPU
- Engine chính: GPT-SoVITS
- Có thể mở rộng XTTS, Fish Speech...

---

# Nguyên tắc làm việc

Trước khi sửa code:

- Đọc toàn bộ các file liên quan.
- Không suy đoán khi chưa đọc source.
- Chỉ sửa các file thực sự cần thiết.
- Không sửa ngoài phạm vi task.
- Nếu phát hiện kiến trúc hiện tại có vấn đề, báo trước khi sửa.

---

# Quy tắc Code

- Không tự refactor.
- Không tự đổi kiến trúc.
- Không tự đổi tên file.
- Không tự đổi tên class.
- Không tự đổi tên hàm public.
- Không thêm thư viện nếu thư viện hiện tại hoặc Python chuẩn đã đáp ứng.
- Giữ coding style thống nhất với project.
- Ưu tiên khả năng mở rộng hơn code ngắn.

---

# Quy tắc Giao diện

- Giao diện hiển thị bằng tiếng Việt.
- Comment bằng tiếng Việt.
- Class, Function, Variable dùng tiếng Anh.

---

# Quy tắc Voice

- Voice có ID cố định.
- Đổi tên Voice không được đổi ID.
- Không dùng tên Voice làm khóa.
- Một Voice có nhiều Variant.
- Variant hiển thị bằng tiếng Việt.

---

# Quy tắc API

Chỉ có một API cho toàn bộ AI Voice Studio.

API phải hỗ trợ:

- Voice ID
- Variant
- Speed
- Emotion
- Style
- Similarity
- Pitch
- Volume

Không tạo API riêng cho từng Voice.

---

# Quy tắc Audio

Speed là tham số Generate.

Không tạo nhiều model chỉ để thay đổi Speed.

Ưu tiên chỉnh Speed lúc sinh Audio.

---

# Quy tắc Dataset

Mặc định:

- Không bỏ quảng cáo.
- Không bỏ tiêu đề chương.
- Không bỏ Intro.
- Không bỏ Outro.

Các mục trên chỉ xử lý khi người dùng bật.

File TXT/DOCX gốc tuyệt đối không được sửa.

Mọi xử lý phải thực hiện trên dữ liệu cache.

---

# Quy tắc Thiết kế

Luôn ưu tiên:

1. Dễ mở rộng.
2. Dễ bảo trì.
3. Ít phụ thuộc.
4. Tương thích các Sprint sau.
5. Không phá vỡ API cũ.

Nếu có nhiều phương án:

- Chọn phương án mở rộng tốt nhất.
- Không tối ưu sớm.
- Không viết code phức tạp khi chưa cần.

---

# Khi hoàn thành

Luôn báo:

## Đã thực hiện

...

## File đã sửa

...

## File mới

...

## Kiểm tra

...

## Ghi chú

...