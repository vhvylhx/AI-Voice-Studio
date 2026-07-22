# Kiểm thử và xác minh — AI Voice Studio

## Nguyên tắc kiểm thử

- Đọc toàn bộ tests liên quan trước khi sửa source.
- Tests phải dùng temporary directory hoặc fixture riêng; không dùng đường dẫn dữ liệu thật của người dùng.
- Không sửa assertion chỉ để làm test pass khi source đang sai, trừ khi task yêu cầu cập nhật contract.
- Fake engine, mock runtime, test provider và fake handler chỉ được đăng ký trong test composition; không được làm thay đổi production readiness.
- Không tạo WAV, MP3, model, checkpoint hoặc artifact giả trong thư mục production để kiểm thử.

## Kiểm tra theo phạm vi

Sau mỗi nhóm thay đổi, chạy targeted tests liên quan.

Trước khi kết thúc task hoặc Sprint, tùy phạm vi cần chạy:

- `python -m compileall src tests`
- targeted `pytest`
- full `pytest`
- bootstrap smoke
- UI smoke nếu có thay đổi UI
- API smoke nếu có thay đổi API
- `git diff --check`
- `git status` ở chế độ read-only

Nếu không thể chạy kiểm tra:

- Ghi rõ kiểm tra chưa chạy.
- Ghi rõ lý do.
- Nêu rủi ro còn lại.
- Không ghi “pass” khi chưa thực sự chạy.

## Xác minh capability

- Readiness production phải phản ánh runtime, asset, validation gate và smoke test thực tế.
- Test pass với fake/mock không được nâng capability production lên `READY`.
- Runtime chưa tích hợp hoặc chưa validate thật phải báo `UNAVAILABLE`, `BLOCKED`, `DEGRADED` hoặc trạng thái thực tế phù hợp.
- Job thành công không đồng nghĩa Unit thành công; Unit chỉ thành công khi Artifact hợp lệ có lineage đúng.
- File tồn tại không đồng nghĩa Artifact hợp lệ.
- Generate/Train không được báo thành công khi thiếu output thật hoặc validation bắt buộc.

## An toàn thay đổi

- Không dùng Git write operations để xử lý test hoặc worktree: không commit, push, pull, merge, rebase, reset, restore, clean, checkout, stash hoặc tag.
- Không xử lý cảnh báo LF/CRLF, không thay đổi Git configuration hoặc line ending nếu task không yêu cầu rõ.
- Khi worktree đã dirty, chỉ xác minh diff và status thuộc đúng phạm vi task; không suy luận thay đổi ngoài phạm vi do task hiện tại gây ra.