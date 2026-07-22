# Engine, Runtime và Capability — AI Voice Studio

## Phân tách trách nhiệm

- `EngineManager` chọn engine phù hợp theo capability và request đã được Service chuẩn hóa; không đọc trực tiếp state Widget hoặc Project đang mở.
- Engine Adapter là lớp cô lập contract engine. Adapter không được quản lý Project, Voice, Variant, Style, Session, Plan hoặc UI state.
- Runtime chịu trách nhiệm discovery, command/environment, asset verification và thực thi tích hợp thực; không được chứa business workflow của ứng dụng.
- Engine chỉ xử lý request immutable và trả result có cấu trúc; mọi persistence, scheduling và state transition phải đi qua Service/Queue theo kiến trúc hiện có.
- Không thêm đường gọi tắt UI/Page/Controller trực tiếp sang Engine, Adapter hoặc Runtime.

## Capability và readiness

- Mỗi capability phải được đánh giá độc lập, tối thiểu phân biệt discovery runtime, dependency, asset/model, language compatibility, execution, preview, WAV/MP3 output, training và real smoke.
- Dùng trạng thái trung thực như `READY`, `DEGRADED`, `BLOCKED`, `UNAVAILABLE`, `MISSING`, `NOT_IMPLEMENTED`, `TEST_ONLY` hoặc `NOT_APPLICABLE`; không suy diễn từ một boolean chung.
- Runtime được phát hiện, executable tồn tại, model tải được, cache có asset hoặc test/canary chạy được không tự chứng minh Generate/Train production `READY`.
- Capability `READY` chỉ được công bố khi các gate theo contract đã pass trên production composition, gồm runtime phù hợp, asset cần thiết, validation bắt buộc và smoke thực tế khi policy yêu cầu.
- Readiness phải giữ evidence/blocker có thể truy vết; không che blocker bằng fallback ngầm, UI placeholder hoặc thông báo thành công chung chung.

## Language và engine compatibility

- Không giả map request language sang language token khác để vượt language gate.
- GPT-SoVITS hiện chưa có Vietnamese cleaner/phoneme frontend/inference contract hợp lệ cho `vi`; preprocessing, training và generate tiếng Việt phải giữ `BLOCKED` cho đến khi runtime hoặc upstream patch hợp lệ được validate.
- Không map giả `vi` sang `zh`, `en`, `auto`, `all_zh`, `yue` hoặc token ngôn ngữ khác.
- Không chạy preprocessing, smoke train hoặc tạo checkpoint/artifact chỉ để chứng minh luồng hoạt động khi `PREPROCESS_CONFIG_INVALID` hoặc language gate chưa đạt.
- VieNeu CPU canary, managed-cache asset và offline resolution không đồng nghĩa production integration đã sẵn sàng. Manual listening review, production binding và full-pipeline real smoke vẫn là các gate riêng.
- Không tự động fallback CPU/GPU hoặc đổi engine nếu request, runtime profile và resource policy chưa cho phép rõ ràng.

## Execution và output

- Adapter/Runtime chưa được tích hợp thực phải trả `UNAVAILABLE`, `BLOCKED` hoặc trạng thái thực tế tương đương; không tạo audio, WAV, MP3, checkpoint, model hay artifact giả.
- Một command process trả exit code thành công không tự đồng nghĩa engine result, Unit hoặc Artifact thành công.
- Kết quả engine phải bao gồm lỗi/blocker có thể hành động được, không làm mất context validation, runtime và resource preflight.
- Không ghi đè asset, model cache quản lý hoặc output đã tồn tại ngoài policy explicit của hệ thống.
- Fake engine, mock runtime, test provider và fake handler chỉ được đăng ký trong test composition; tuyệt đối không làm thay đổi production AppContext hoặc production readiness.