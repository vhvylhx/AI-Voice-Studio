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

AGENTS.md là quy tắc làm việc cao nhất của dự án. Nếu cần thêm bối cảnh, hãy đọc PROJECT_STATUS.md, CURRENT_SPRINT.md, ROADMAP.md và các tài liệu liên quan trước khi bắt đầu.
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
Nếu phát hiện lỗi kiến trúc hoặc vấn đề nghiêm trọng ngoài phạm vi task:

- Không tự sửa.
- Báo trước.
- Chờ người dùng quyết định.

---

# Quy tắc đọc trạng thái dự án

Trước khi bắt đầu bất kỳ task hoặc Sprint nào, phải đọc theo thứ tự:

1. AGENTS.md
2. ROADMAP.md
3. docs/PROJECT_STATUS.md
4. CURRENT_SPRINT.md
5. docs/Architecture.md
6. docs/DECISIONS.md
7. CHANGELOG.md
8. Source liên quan
9. Tests liên quan

Không dùng trí nhớ từ cuộc trò chuyện trước thay cho source hiện tại.

Không dùng báo cáo cũ thay cho source hiện tại.

Nếu tài liệu và source mâu thuẫn:

- Source hiện tại là sự thật ưu tiên.
- Phải báo rõ điểm mâu thuẫn.
- Sau khi hoàn thành task, cập nhật lại tài liệu cho khớp source.

---

# Quy tắc PROJECT_STATUS.md

`docs/PROJECT_STATUS.md` là tài liệu phản ánh trạng thái hiện tại của toàn bộ dự án.

Sau mỗi Sprint hoặc thay đổi capability đáng kể, bắt buộc cập nhật:

- Phiên bản hiện tại.
- Sprint hiện tại hoặc Sprint vừa hoàn thành.
- Chức năng đã hoàn thành.
- Capability hiện tại.
- Các trạng thái READY, DEGRADED, UNAVAILABLE, MISSING.
- Các blocker.
- Phạm vi chưa triển khai.
- Sprint tiếp theo dự kiến.

Không được kết thúc Sprint nếu `docs/PROJECT_STATUS.md` chưa phản ánh đúng source hiện tại.

---

# Quy tắc an toàn dữ liệu

Không được tự ý sửa, xóa, di chuyển, đổi tên hoặc ghi đè dữ liệu thật trong:

- projects/
- workspace/
- voices/
- outputs/
- backups/
- exports/
- Reference Vault
- Dataset người dùng

Tests phải dùng thư mục tạm hoặc fixture riêng.

Không được dùng đường dẫn dữ liệu thật của người dùng trong tests.

Không được tạo WAV, MP3, model hoặc Artifact giả trong thư mục production.

---

# Quy tắc Git

Không được tự ý thực hiện:

- commit
- push
- pull
- merge
- rebase
- reset
- restore
- clean
- checkout
- stash
- tag

Chỉ được đọc:

- git status
- git diff
- git diff --check
- git log

Chỉ thực hiện Git write khi người dùng yêu cầu rõ ràng.

Worktree có dữ liệu thật đang dirty không phải lý do để tự động restore hoặc clean.

---

# Quy tắc Production và Test

Không tạo fake production để làm capability trông như đã READY.

Test provider, fake engine, fake handler và mock runtime:

- Chỉ được đăng ký trong tests hoặc test composition.
- Không được đăng ký trong production AppContext.
- Không được làm thay đổi production readiness.

Nếu GPT-SoVITS runtime thật chưa được tích hợp:

- Generate Execution phải là UNAVAILABLE.
- Preview Audio phải là UNAVAILABLE.
- WAV Output phải là UNAVAILABLE.
- MP3 Output phải là UNAVAILABLE.

Không được báo READY chỉ vì tests dùng fake provider chạy được.

---

# Quy tắc Readiness

Không dùng một boolean chung cho toàn bộ tính năng.

Mỗi capability phải có trạng thái riêng:

- READY
- DEGRADED
- TEST_ONLY
- UNAVAILABLE
- BLOCKED
- NOT_IMPLEMENTED
- MISSING
- NOT_APPLICABLE

Readiness phải phản ánh đúng production runtime hiện tại.

Không được che capability thiếu bằng tài liệu, UI placeholder hoặc test fake.

---

# Quy tắc Job và Engine

UI không được gọi Engine trực tiếp.

Luồng chuẩn:

UI
→ Page/Controller
→ Service
→ Job Queue
→ Engine Manager
→ Engine Adapter
→ Runtime

Business logic không được đặt trong Widget.

Worker không được phụ thuộc vào Project đang mở trên UI.

Mọi Job phải mang Project ID, Session ID và các immutable ID cần thiết.

---

# Quy tắc Persistence

Không dùng tên hiển thị làm khóa định danh.

Các ID sau phải bất biến nếu đã được tạo:

- Project ID
- Voice ID
- Variant ID
- Style ID
- Reference ID
- Session ID
- Plan ID
- Unit ID
- Attempt ID
- Artifact ID
- Job ID

Đổi tên hiển thị không được làm thay đổi ID.

Không fallback theo tên hoặc đường dẫn nếu đã có immutable ID.

---

# Quy tắc Generate Pipeline

Generate Request và Generate Session phải tách biệt.

Frozen Plan không được thay đổi semantic sau khi freeze.

Resume và Retry không được tự động:

- Normalize lại.
- Detect chapter lại.
- Split lại.
- Thay settings đã frozen.
- Thay selection đã frozen.
- Thay Unit ID.

Unit chỉ được xem là thành công khi có Artifact hợp lệ.

Job thành công không đồng nghĩa Unit thành công.

File tồn tại không đồng nghĩa Artifact hợp lệ.

Không silent overwrite output.

Không tự xóa temp, orphan hoặc Artifact lỗi nếu chưa có chính sách và xác nhận phù hợp.

---

# Quy tắc kiểm thử

Sau mỗi nhóm thay đổi phải chạy targeted tests liên quan.

Trước khi kết thúc task hoặc Sprint, tùy phạm vi phải chạy:

- python -m compileall src tests
- targeted pytest
- full pytest
- bootstrap smoke
- UI smoke nếu có thay đổi UI
- API smoke nếu có thay đổi API
- git diff --check
- git status đọc-only

Nếu không thể chạy một kiểm tra, phải ghi rõ:

- Kiểm tra nào chưa chạy.
- Lý do.
- Rủi ro còn lại.

Không được ghi “pass” khi chưa thực sự chạy.

---

# Quy tắc cập nhật tài liệu

Sau mỗi Sprint, bắt buộc cập nhật đồng bộ:

- docs/PROJECT_STATUS.md
- CURRENT_SPRINT.md
- ROADMAP.md
- CHANGELOG.md

Nếu thay đổi kiến trúc:

- cập nhật docs/Architecture.md

Nếu có quyết định thiết kế mới:

- cập nhật docs/DECISIONS.md

Tài liệu không được tuyên bố capability cao hơn source thực tế.

---

# Quy tắc phạm vi Sprint

Không tự mở Sprint mới.

Không tự đổi mã Sprint.

Không chuyển sang task tiếp theo khi Sprint hiện tại còn thiếu yêu cầu bắt buộc.

Nếu phát hiện phần thiếu lớn thuộc Sprint hiện tại:

- Tiếp tục hoàn thiện Sprint hiện tại.
- Không che bằng báo cáo.
- Không tự giảm phạm vi.

Nếu phát hiện vấn đề ngoài phạm vi:

- Không tự sửa.
- Báo rõ mức độ ảnh hưởng.
- Chờ người dùng quyết định.

---

# Final Status

Chỉ được dùng một trong các trạng thái cuối sau:

READY_FOR_GITHUB_REVIEW

hoặc:

SOURCE_DOCS_TESTS_READY
WORKTREE_NOT_CLEAN_DUE_TO_REAL_USER_DATA

hoặc:

NOT_READY

Không tự tạo Final Status khác.

Nếu source, docs và tests đã hoàn tất nhưng worktree còn dirty do dữ liệu thật có sẵn và không được phép đụng vào, dùng:

SOURCE_DOCS_TESTS_READY
WORKTREE_NOT_CLEAN_DUE_TO_REAL_USER_DATA

Nếu còn thiếu yêu cầu bắt buộc hoặc test chưa pass, dùng:

NOT_READY

---

# Định dạng báo cáo hoàn thành

Khi hoàn thành, luôn báo:

## Đã thực hiện

- Nội dung thực sự đã triển khai.
- Không overclaim.
- Phân biệt rõ production, foundation, test-only và unavailable.

## File đã sửa

- Liệt kê đầy đủ.

## File mới

- Liệt kê đầy đủ.
- Nếu không có, ghi rõ “Không có”.

## File đã xóa

- Liệt kê đầy đủ.
- Nếu không có, ghi rõ “Không có”.

## Kiểm tra

- Ghi chính xác command đã chạy.
- Ghi chính xác kết quả.

## Capability Table

- Liệt kê capability và trạng thái thực tế.

## Chưa thực hiện

- Liệt kê các phần còn thiếu hoặc cố ý để UNAVAILABLE.

## Ghi chú

- Data safety.
- Git status.
- Blocker.
- Rủi ro còn lại.

## Final Status

- Chỉ dùng trạng thái được cho phép.