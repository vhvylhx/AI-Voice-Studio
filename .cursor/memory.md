# AI Voice Studio - Project Memory

## Project

Tên:

AI Voice Studio

---

## Mục tiêu

Tạo ứng dụng Windows giúp clone giọng và tạo truyện audio bằng AI.

Sau khi đã train xong, ứng dụng phải có thể chạy hoàn toàn trên máy tính mà không phụ thuộc dịch vụ TTS trực tuyến.

Mục tiêu cuối cùng là thay thế toàn bộ quy trình tạo truyện audio hiện tại.

---

## Đối tượng sử dụng

Chủ yếu phục vụ đọc truyện dài.

Ưu tiên:

- Clone giọng giống nhất có thể.
- Đọc tự nhiên.
- Batch nhiều chương.
- Ít thao tác.

---

## Dataset

datasets/

Mỗi thư mục là một Dataset.

Ví dụ:

datasets/

Thu Minh/

Lan Anh/

Giọng Nam/

...

Trong mỗi Dataset có thể có:

- mp3
- docx
- txt

Tên file được dùng để ghép dữ liệu.

Ví dụ:

0001.mp3

0001.docx

Nếu không ghép được:

- bỏ qua
- ghi log

Không được dừng chương trình.

---

## Voice

Sau khi Train sẽ tạo:

voices/

Thu Minh/

Lan Anh/

...

Mỗi Voice là một thư mục độc lập.

---

## Engine

Engine đầu tiên:

GPT-SoVITS

Thiết kế theo hướng có thể thay Engine sau này.

---

## Reader

Nguồn nhập:

- Paste
- TXT
- DOCX
- Folder

---

## Output

Xuất:

- MP3

---

## Nguyên tắc

Ưu tiên:

- MVP trước
- Dễ dùng
- Dễ mở rộng
- Không tối ưu quá sớm
