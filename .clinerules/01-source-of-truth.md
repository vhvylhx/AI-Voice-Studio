# Nguồn sự thật — AI Voice Studio

## Thứ tự đọc bắt buộc

Trước khi bắt đầu task hoặc Sprint, đọc theo thứ tự:

1. `AGENTS.md`
2. `ROADMAP.md`
3. `docs/PROJECT_STATUS.md`
4. `CURRENT_SPRINT.md`
5. `docs/Architecture.md`
6. `docs/DECISIONS.md`
7. `CHANGELOG.md`
8. Source liên quan
9. Tests liên quan

Không dùng trí nhớ từ cuộc trò chuyện hoặc báo cáo cũ thay cho source hiện tại.

## Khi thông tin mâu thuẫn

- Source hiện tại là sự thật ưu tiên.
- Báo rõ điểm mâu thuẫn giữa tài liệu và source.
- Sau khi hoàn thành thay đổi, cập nhật tài liệu liên quan để phản ánh source nếu phạm vi task cho phép.
- Không tuyên bố capability cao hơn production runtime thực tế.

## Readiness

Không dùng một boolean chung cho toàn bộ tính năng. Mỗi capability phải phản ánh trạng thái riêng, ví dụ:

- `READY`
- `DEGRADED`
- `TEST_ONLY`
- `UNAVAILABLE`
- `BLOCKED`
- `NOT_IMPLEMENTED`
- `MISSING`
- `NOT_APPLICABLE`

Test fake, mock hoặc provider test-only không được nâng production readiness.

## Dữ liệu và capability production

- Nếu runtime GPT-SoVITS thật chưa tích hợp/validate, Generate Execution, Preview Audio, WAV Output và MP3 Output phải báo trạng thái thực tế.
- Không tạo WAV, MP3, checkpoint, model hoặc artifact giả trong production để biểu diễn thành công.
- Dataset/audio pass không tự động đồng nghĩa train hoặc generate đã READY; các validation gate và engine/language compatibility phải pass thật.