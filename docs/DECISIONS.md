# Architecture Decisions

## DEC-001: Voice ID cố định

- Trạng thái: Chấp nhận.
- Bối cảnh: Voice cần ổn định khi đổi tên và khi API dùng lâu dài.
- Quyết định: Mỗi Voice có ID cố định, không dùng tên Voice làm khóa.
- Lý do: Tên có thể đổi, ID phải ổn định cho model, API và dữ liệu.
- Hệ quả: Rename Voice không được đổi ID.
- Ngày cập nhật: 2026-07-14.

## DEC-002: Một API dùng cho toàn bộ Voice

- Trạng thái: Chấp nhận.
- Bối cảnh: Dự án cần mở rộng nhiều Voice và Variant.
- Quyết định: Chỉ có một API chung cho AI Voice Studio.
- Lý do: Tránh API riêng lẻ theo từng Voice.
- Hệ quả: API phải nhận Voice ID, Variant và các tham số generate.
- Ngày cập nhật: 2026-07-14.

## DEC-003: Speed là tham số Generate

- Trạng thái: Chấp nhận.
- Bối cảnh: Speed có thể thay đổi theo lần sinh audio.
- Quyết định: Speed là tham số Generate, không tạo model riêng chỉ để đổi Speed.
- Lý do: Giảm số model và giữ quản lý Voice đơn giản.
- Hệ quả: Engine/Adapter phải xử lý Speed lúc sinh audio.
- Ngày cập nhật: 2026-07-14.

## DEC-004: Không sửa file TXT/DOCX/audio gốc

- Trạng thái: Chấp nhận.
- Bối cảnh: Dataset gốc cần giữ nguyên để kiểm chứng và tái lập.
- Quyết định: Không ghi đè hoặc sửa file TXT, DOCX, audio gốc.
- Lý do: Tránh mất dữ liệu và tránh thay đổi nghĩa nội dung.
- Hệ quả: Mọi xử lý phải tạo dữ liệu mới ở cache/output.
- Ngày cập nhật: 2026-07-14.

## DEC-005: Mọi xử lý dataset nằm trong cache

- Trạng thái: Chấp nhận.
- Bối cảnh: Dataset pipeline cần có thể chạy lại và dọn được.
- Quyết định: Dữ liệu sinh ra từ validation, segmentation, alignment nằm trong cache.
- Lý do: Giữ workspace gốc sạch.
- Hệ quả: Cache không phải dữ liệu nguồn để commit.
- Ngày cập nhật: 2026-07-14.

## DEC-006: Metadata chỉ chứa valid clip

- Trạng thái: Chấp nhận.
- Bối cảnh: metadata.list là đầu vào train.
- Quyết định: Chỉ ghi clip valid vào metadata.list.
- Lý do: Không đưa dữ liệu nghi ngờ vào train.
- Hệ quả: Suspicious chỉ nằm trong report.
- Ngày cập nhật: 2026-07-14.

## DEC-007: Quality-first, không hạ chuẩn để lấy số lượng

- Trạng thái: Chấp nhận.
- Bối cảnh: Train ít lần nên chất lượng dataset quan trọng hơn số lượng.
- Quyết định: Không hạ threshold để tạo thêm clip valid.
- Lý do: Dataset kém làm hỏng train.
- Hệ quả: Clip thiếu chắc chắn bị loại hoặc đưa vào report.
- Ngày cập nhật: 2026-07-14.

## DEC-008: Không dùng ratio fallback cho valid

- Trạng thái: Chấp nhận.
- Bối cảnh: Chia theo tỷ lệ ký tự không đảm bảo khớp audio-text.
- Quyết định: Ratio fallback không được đưa clip vào valid.
- Lý do: Valid phải dựa trên ASR + timestamp thật.
- Hệ quả: Ratio fallback nếu dùng chỉ để tham khảo/suspicious.
- Ngày cập nhật: 2026-07-14.

## DEC-009: Clip dài chia bằng timestamp ASR thật

- Trạng thái: Chấp nhận.
- Bối cảnh: GPT-SoVITS cần clip ngắn có transcript khớp.
- Quyết định: Clip dài phải chia theo sentence/word timestamp từ Faster-Whisper.
- Lý do: Không cắt giữa từ và giữ audio-text khớp nhất có thể.
- Hệ quả: Cần word timestamp trong AlignmentService.
- Ngày cập nhật: 2026-07-14.

## DEC-010: Weak source không train tự động

- Trạng thái: Chấp nhận.
- Bối cảnh: Source có quá ít clip valid có thể không đủ tin cậy.
- Quyết định: Source dưới ngưỡng valid segment được đánh dấu weak_source.
- Lý do: Cần người dùng quyết định trước khi dùng để train.
- Hệ quả: Mặc định weak_source không ghi vào metadata train.
- Ngày cập nhật: 2026-07-14.

## DEC-011: Đường dẫn nội bộ phải portable/tương đối

- Trạng thái: Chấp nhận.
- Bối cảnh: App cần có thể chuyển máy/thư mục.
- Quyết định: Tài nguyên trong app dùng path tương đối khi lưu cấu hình.
- Lý do: Tránh khóa cứng ổ đĩa hoặc máy hiện tại.
- Hệ quả: Tài nguyên ngoài app mới dùng absolute path.
- Ngày cập nhật: 2026-07-14.

## DEC-012: Hỗ trợ nhiều GPT-SoVITS Runtime Profile

- Trạng thái: Chấp nhận.
- Bối cảnh: Người dùng có thể đổi máy, nâng GPU hoặc thêm runtime mạnh hơn.
- Quyết định: Runtime có nhiều profile và có default profile.
- Lý do: Không phá Voice model cũ khi đổi runtime.
- Hệ quả: Runtime mới phải validate và kiểm tra tương thích.
- Ngày cập nhật: 2026-07-14.

## DEC-013: Runtime không tải model âm thầm

- Trạng thái: Chấp nhận.
- Bối cảnh: Model ASR/AI lớn và phụ thuộc môi trường.
- Quyết định: Không tự download model nếu người dùng chưa xác nhận.
- Lý do: Tránh tải nặng, sai runtime hoặc sai quyền.
- Hệ quả: Trả trạng thái model_missing và hướng dẫn rõ.
- Ngày cập nhật: 2026-07-14.

## DEC-014: Runtime lỗi phải có hướng dẫn sửa cụ thể

- Trạng thái: Chấp nhận.
- Bối cảnh: Runtime Windows/GPU dễ lỗi do thiếu package, driver, model.
- Quyết định: Runtime status phải có nguyên nhân, đường dẫn, lệnh kiểm tra/cài đặt và link chính thức nếu cần.
- Lý do: UI/API cần hướng dẫn người dùng tự sửa.
- Hệ quả: Service trả output đủ chi tiết cho UI Sprint sau.
- Ngày cập nhật: 2026-07-14.

## DEC-015: Text ↔ MP3 ghép theo số chương trước, ASR xác minh sau

- Trạng thái: Chấp nhận.
- Bối cảnh: Một chương có thể có nhiều MP3 và text tương ứng.
- Quyết định: Ghép theo số chương trước, dùng ASR xác minh; nếu lệch nội dung thì bỏ cặp, không tự ghép sang số khác.
- Lý do: Tránh tự đoán làm sai dữ liệu train.
- Hệ quả: Cần luật matching rõ trước AVS-014.
- Ngày cập nhật: 2026-07-14.

## DEC-016: File test không ghép tự động, không phân loại chữ Trung

- Trạng thái: Chấp nhận.
- Bối cảnh: File test/gần giống test không phải dữ liệu train thật.
- Quyết định: Bỏ khỏi ghép tự động nếu tên file có dấu hiệu test hoặc gõ gần giống test. Không phân loại hoặc chặn riêng ký tự Trung.
- Lý do: Giữ luật dataset đơn giản, tập trung vào số chương và dữ liệu test.
- Hệ quả: File test trả reason `test_version`; file không lấy được số chương trả `invalid_filename`.
- Ngày cập nhật: 2026-07-16.

## DEC-017: Lỗi nhỏ bỏ đoạn, lỗi lớn bỏ source và report

- Trạng thái: Chấp nhận.
- Bối cảnh: Một vài đoạn sai không nên dừng toàn batch.
- Quyết định: Đoạn lỗi bị bỏ riêng; source vượt ngưỡng lỗi bị bỏ source và tiếp tục source khác.
- Lý do: Batch dài cần bền và có report.
- Hệ quả: Report phải có code lỗi theo đoạn/source.
- Ngày cập nhật: 2026-07-14.

## DEC-018: Job dài phải có progress, ETA và khả năng resume về sau

- Trạng thái: Chấp nhận.
- Bối cảnh: Dataset/train là job lâu.
- Quyết định: Service phải chuẩn bị progress payload; resume là ưu tiên sau.
- Lý do: UI cần thông tin trạng thái rõ.
- Hệ quả: Không viết logic UI trong Service.
- Ngày cập nhật: 2026-07-14.

## DEC-019: Dataset Health là tính năng ưu tiên cao

- Trạng thái: Chấp nhận.
- Bối cảnh: Train thật phụ thuộc chất lượng dataset.
- Quyết định: Dataset Health cần làm trước hoặc sát trước AVS-014.
- Lý do: Phải biết dữ liệu đủ sạch trước khi train.
- Hệ quả: Task tiếp theo nên ưu tiên matching rules và health report.
- Ngày cập nhật: 2026-07-14.

## DEC-020: Trạng thái UI và lựa chọn cuối phải lưu theo project

- Trạng thái: Chấp nhận.
- Bối cảnh: Người dùng cần mở lại dự án đúng trạng thái.
- Quyết định: UI state và lựa chọn cuối nên lưu theo project.
- Lý do: Giảm mất ngữ cảnh khi đóng/mở app hoặc đổi phiên Codex.
- Hệ quả: Settings/project state cần mở rộng ở Sprint phù hợp.
- Ngày cập nhật: 2026-07-14.

## DEC-021: Dataset Health lỗi thì chặn Alignment/Train

- Trạng thái: Chấp nhận.
- Bối cảnh: Alignment và Train chỉ an toàn khi dataset đã qua kiểm tra đầy đủ.
- Quyết định: Nếu Dataset Health có lỗi chặn thì dừng trước Alignment, ghi report rõ file, reason và suggestion.
- Lý do: Không đợi đến Train mới phát hiện thiếu text/audio, file test, invalid filename, duplicate hoặc mismatch.
- Hệ quả: Người dùng phải xử lý Dataset Health report trước AVS-014 Train thật.
- Ngày cập nhật: 2026-07-16.

## DEC-022: Workflow chung có Input Folder và Output Folder

- Trạng thái: Chấp nhận.
- Bối cảnh: Các job dài cần cách chọn input/output thống nhất trong toàn app.
- Quyết định: Mọi job dùng WorkflowConfig gồm input_folder, output_folder và use_input_folder_as_output.
- Lý do: Giữ UX nhất quán và chuẩn bị cho UI/Job Resume sau này.
- Hệ quả: Nếu use_input_folder_as_output bật thì output mặc định là input; nếu tắt thì bắt buộc có output_folder riêng.
- Ngày cập nhật: 2026-07-16.

## DEC-023: Dataset Repair chỉ sửa lỗi an toàn trong cache

- Trạng thái: Chấp nhận.
- Bối cảnh: Dataset Health có thể phát hiện nhiều lỗi trước Alignment/Train, nhưng không phải lỗi nào cũng được phép sửa tự động.
- Quyết định: Dataset Repair chỉ auto repair lỗi an toàn, hiện tại là duplicate bằng cách giữ bản tốt nhất và copy bản trùng vào ignored trong cache/workspace output. Các lỗi còn lại bị skip/report để Manual Review.
- Lý do: Không sửa file gốc, không tự đoán nội dung, không tự đổi chương và không làm mất dữ liệu nguồn.
- Hệ quả: Workflow Dataset là Scan → Health → Repair → Health → Alignment → Train; UI sau này có thể chọn Auto Repair hoặc Manual Review.
- Ngày cập nhật: 2026-07-16.

## DEC-024: Dataset Review là cổng chốt trước Alignment/Train

- Trạng thái: Chấp nhận.
- Bối cảnh: Sau Repair vẫn có lỗi không nên tự sửa như test_version, broken_file, empty_file hoặc filename_content_mismatch.
- Quyết định: Dataset Review sinh review_report.json và yêu cầu mọi blocking error còn lại có trạng thái approved, rejected hoặc ignored trước khi cho phép đi tiếp.
- Lý do: Người dùng phải chốt quyết định chất lượng dataset thay vì app tự đoán hoặc tự bỏ dữ liệu quan trọng.
- Hệ quả: Workflow Dataset là Scan → Health → Repair → Review → Alignment → Train; nếu không có review_report thì Dataset Health blocker vẫn chặn như cũ.
- Ngày cập nhật: 2026-07-16.
