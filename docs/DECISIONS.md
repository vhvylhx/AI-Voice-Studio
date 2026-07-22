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

## DEC-025: Train GPT-SoVITS phải qua validation gate và run_id riêng

- Trạng thái: Chấp nhận.
- Bối cảnh: Train thật tốn thời gian, phụ thuộc runtime/GPU và có thể ghi model mới.
- Quyết định: Trước khi train phải chạy validation gate kiểm tra Dataset Review, metadata.list, WAV format, Voice, Runtime Profile, Python/torch, GPT-SoVITS scripts, pretrained model và output model path. Mỗi lần train dùng run_id riêng.
- Lý do: Tránh train bằng dữ liệu lỗi, tránh ghi đè model cũ và tránh phụ thuộc đường dẫn máy cá nhân.
- Hệ quả: Model output nằm trong voices/<voice_id>/model/<run_id>/; validation_only không train, smoke_test/train thật chỉ chạy sau khi người dùng chốt tham số và xác nhận.
- Ngày cập nhật: 2026-07-16.

## DEC-026: Smoke test GPT-SoVITS tối thiểu trước full train

- Trạng thái: Chấp nhận.
- Bối cảnh: Full train GPT-SoVITS cần tham số, dataset format đầy đủ và có rủi ro VRAM trên Quadro P1000 4 GB.
- Quyết định: AVS-014.1 chạy smoke test runtime/process tối thiểu trước full train: gọi Python runtime thật, import GPT-SoVITS config, kiểm tra CUDA, đọc metadata/WAV và ghi checkpoint smoke riêng.
- Lý do: Xác minh Runtime Profile, CUDA, metadata và output path thật mà không chạy full train hoặc ghi đè model.
- Hệ quả: Full `s1_train.py`/`s2_train.py` chỉ chạy sau khi người dùng chốt tham số train và dataset train format đúng GPT-SoVITS.
- Ngày cập nhật: 2026-07-16.

## DEC-027: Suspicious Recovery khong ha nguong va khong ghi de baseline

- Trang thai: Chap nhan.
- Boi canh: AVS-014.2 tao duoc it valid clip, can thu cuu suspicious nhung khong duoc ha chat luong dataset.
- Quyet dinh: Suspicious Recovery la pipeline rieng sau Full Dataset Preparation, doc baseline report/state va ghi output vao cache rieng.
- Quyet dinh: Khong ha similarity threshold duoi 90, khong dung ratio fallback de dua clip vao valid, va chi chay full recovery neu preview nho co ket qua tot.
- Ly do: Bao ve chat luong dataset va giu baseline AVS-014.2 co the rollback.
- He qua: Clip duoi threshold van nam trong still_suspicious, chi di tiep bang manual review hoac bang text/audio nguon dung hon.
- Ngay cap nhat: 2026-07-16.

## DEC-028: Full Dataset moi uu tien nguon dung hon recovery dataset cu

- Trang thai: Chap nhan.
- Boi canh: AVS-014.3 preview recovery khong cuu them clip valid, trong khi nguoi dung co kho MP3 va Text/DOCX moi lon hon.
- Quyet dinh: Khong tiep tuc full recovery dataset cu. Dataset cu giu lam cache lich su; Full Dataset Expansion quet lai nguon moi bang audio_folder va text_folder rieng.
- Ly do: Du lieu nguon dung tot hon viec co cuu suspicious co similarity thap hoac text goc sai ngon ngu.
- He qua: Alignment toan bo nguon moi chi chay sau Scan, Health, Repair va Review hop le.
- Ngay cap nhat: 2026-07-16.

## DEC-029: Voice la identity, Variant/Preset/Reference/Text Profile la contract rieng

- Trang thai: Chap nhan.
- Boi canh: Can tranh train nhieu model chi vi style, emotion, speed hoac bien the doc.
- Quyet dinh: Voice chi la danh tinh nguoi noi va mot model chinh. Variant mo ta cach noi, Preset chua tham so Generate, Reference Style chua audio tham chieu, Text Profile chua luat xu ly van ban.
- Quyet dinh: Generate Request duy nhat gom VoiceID, VariantID, PresetID, ReferenceStyleID, TextProfileID, Engine va Text.
- Ly do: Giu Voice model on dinh, tranh no so luong model va de mo rong multi-engine.
- He qua: Engine chi sinh audio; Engine Profile map tham so chung sang tham so rieng tung engine.
- Ngay cap nhat: 2026-07-16.

## DEC-030: Same Folder Mode la mac dinh cho workspace cu

- Trang thai: Chap nhan.
- Boi canh: Du lieu hien tai dang nam trong workspace/<Voice Name>/ voi MP3 va TXT/DOCX cung mot thu muc.
- Quyet dinh: Workflow ho tro source_mode = same_folder va coi day la che do mac dinh cho Project/Voice cu.
- Ly do: Giu tuong thich du lieu hien tai, khong bat nguoi dung tach thu muc va khong migration pha cau truc cu.
- He qua: audio_folder va text_folder co the cung tro vao mot thu muc; Separate Folder Mode van duoc ho tro khi nguoi dung muon tach nguon.
- Ngay cap nhat: 2026-07-16.

## DEC-031: Auto Review chi ignored/rejected loi an toan

- Trang thai: Chap nhan.
- Boi canh: Dataset moi co missing_audio, missing_text, test_version va broken_file nhung cac cap matched hop le van co the alignment.
- Quyet dinh: Auto Review khong approve file loi. test_version, missing_audio, missing_text, invalid_filename = ignored; broken_file, empty_file, empty_content, filename_content_mismatch = rejected.
- Ly do: Loi khong duoc dua vao train, nhung khong chan toan batch khi cac cap matched hop le da duoc loc rieng.
- He qua: pending = 0 va train_allowed = true chi co nghia la cac blocking item da duoc xu ly bang ignored/rejected, khong co nghia la file loi duoc train.
- Ngay cap nhat: 2026-07-16.

## DEC-032: Generate Standard va AI Style phai co scope ro rang

- Trang thai: Chap nhan.
- Boi canh: Generate sau nay can cho AI chon Variant/Style theo ngu canh nhung khong duoc vuot qua y dinh nguoi dung.
- Quyet dinh: Standard Mode chi dung Voice va Variant nguoi dung chon. AI Style Mode chi duoc chon Variant va Style trong danh sach nguoi dung tick hoac all scope.
- Quyet dinh: Neu khong co Variant/Style hop le trong scope thi chan generate, khong tu doan. Fallback chi duoc dung default neu default nam trong scope; neu khong thi chon best allowed trong scope.
- Quyet dinh: Timeline chi duoc doi Variant/Style tai sentence, paragraph, dialogue, scene hoac pause boundary; khong doi giua tu hoac giua cau.
- Quyet dinh: Temp workspace nam trong temp/<job_kind>/<job_id>; output folder chi chua final artifact/report.
- Ly do: Giu kiem soat cua nguoi dung, tranh AI tu doi giong/doc sai vai va tranh output folder bi ban temp file.
- He qua: Can chot default Variant, default Style va custom speed safe limits truoc khi noi vao generate that.
- Ngay cap nhat: 2026-07-16.

## DEC-033: Default Variant, Style va Speed cho Generate

- Trang thai: Chap nhan.
- Boi canh: AVS-014.6 can chot fallback Generate ma khong hard-code trong engine.
- Quyet dinh: Moi Voice bat buoc co default_variant_id, mac dinh la `default`.
- Quyet dinh: Moi Voice co default_style_id; khong hard-code ten Style trong logic engine.
- Quyet dinh: AI chi fallback sang default Variant/Style neu default nam trong allowed scope hoac allow_all = true.
- Quyet dinh: Neu default khong duoc phep, AI chon candidate co confidence cao nhat trong allowed scope. Neu khong co candidate hop le thi dung Generate.
- Quyet dinh: Custom speed chi cho phep 0.80 den 1.20. Preset 0.5, 0.75, 1.0, 1.1, 1.2, 1.3, 1.5 la che do dac biet.
- Ly do: Giu chat luong audio, tranh meo tieng va tranh AI tu mo rong pham vi nguoi dung cho phep.
- He qua: UI AVS-014.7 phai cho nguoi dung chon scope va hien loi neu scope rong.
- Ngay cap nhat: 2026-07-16.

## DEC-034: Cleanup policy cho Generate temp workspace

- Trang thai: Chap nhan.
- Boi canh: Generate co chunk, timeline, merge va co the pause/cancel/error.
- Quyet dinh: SUCCESS xoa toan bo temp.
- Quyet dinh: PAUSE giu temp, state va progress.
- Quyet dinh: CANCEL phai hoi nguoi dung giu hay xoa temp.
- Quyet dinh: ERROR giu temp, log va state.
- Quyet dinh: RESUME dung temp cu, khong tao job moi va khong generate lai chunk da hoan thanh.
- Ly do: Bao ve kha nang resume/debug va giu output folder sach.
- He qua: Temp workspace nam trong temp/<kind>/<job_id>; output chi chua final artifact/report.
- Ngay cap nhat: 2026-07-16.

## DEC-035: Ranh gioi Voice, Variant, Style va Engine

- Trang thai: Chap nhan.
- Boi canh: Can tranh tron lan Voice model, style doc va engine runtime.
- Quyet dinh: Voice chi co Dataset, Model, Runtime, Preview va Metadata; khong luu Emotion, Style, Speed hoac Preset.
- Quyet dinh: Variant khong phai model. Variant chi la Generate Profile, Prompt, Style, Speed, Emotion va Parameter; khong chua checkpoint, dataset hoac weight.
- Quyet dinh: Style khong phai Voice. Style mo ta cam xuc, cach doc, pacing va expression, co the dung cho nhieu Voice.
- Quyet dinh: Engine chi nhan GenerateRequest va tra GenerateAudio; khong quan ly Voice, Variant, Style, Project hoac Workflow.
- Ly do: Giu kien truc mo rong, tranh no so luong model va de thay engine runtime sau nay.
- He qua: AVS-014.7 chi noi cac contract da chot vao UI/Adapter, khong them kien truc moi.
- Ngay cap nhat: 2026-07-16.

## DEC-036: Generate output, pause, crossfade va chunk failure policy

- Trang thai: Chap nhan.
- Boi canh: AVS-014.7 can chot mac dinh cho output MP3, pause/crossfade va cach xu ly chunk loi.
- Quyet dinh: MP3 bitrate mac dinh la 192 kbps; cac bitrate hop le la 128, 192, 256 va 320 kbps; app luu lua chon cuoi theo Project.
- Quyet dinh: Pause mac dinh tap trung trong GenerateAudioProfile: comma 120ms, sentence/question/exclamation 300ms, dialogue 250ms, paragraph 500ms va scene 800ms.
- Quyet dinh: Crossfade mac dinh 20ms va chi ap dung o boundary an toan; khong ap dung khi chunk da co silence/pause tu nhien phu hop.
- Quyet dinh: retry_count mac dinh la 1. Neu chunk van loi sau retry thi dung toan job, khong xuat final audio gia thanh cong, giu temp/state/log va cho phep resume.
- Ly do: Uu tien chat luong va kha nang debug/resume hon viec tao output thieu chunk.
- He qua: Generate Pipeline phai report ro chunk_id, text, loi va retry count khi dung job.
- Ngay cap nhat: 2026-07-16.

## DEC-037: Metadata final phai rebuild tu alignment_state

- Trang thai: Chap nhan.
- Boi canh: Job alignment dai co the resume nhieu lan, metadata.list co the lech state neu process dung truoc khi flush final.
- Quyet dinh: Sau khi Full Alignment hoan tat, `alignment_state.json` la source of truth. `metadata.list` final phai duoc rebuild tu toan bo valid clips trong state va ghi bang atomic write.
- Quyet dinh: Neu metadata cu co so dong khac state, khong dung metadata cu lam dau vao train.
- Ly do: Bao ve train pipeline khoi metadata thieu clip, duplicate hoac lech voi checkpoint moi nhat.
- He qua: Train validation chi chay sau khi metadata final da validate bang ffprobe va clip count khop valid trainable trong state.
- Ngay cap nhat: 2026-07-17.

## DEC-038: Runtime Training Profile truoc Train that

- Trang thai: Chap nhan.
- Boi canh: May co the doi GPU/CPU/RAM hoac them runtime moi, cau hinh train khong nen hard-code cho mot may duy nhat.
- Quyet dinh: App co Runtime Training Profile voi Auto, Compatibility, Performance va Custom. Auto Detect Hardware mac dinh bat va chon cau hinh dua tren VRAM, CUDA, CPU/RAM va runtime validation that.
- Quyet dinh: Quadro P1000 4 GB voi GPT-SoVITS v2Pro duoc Auto chon cau hinh Compatibility: batch_size 1, num_workers 0, compute cuda neu validation dat.
- Ly do: Giam OOM va giu train an toan khi doi may/nang cap phan cung.
- He qua: Truoc train that phai chay detect hardware, runtime validation, dataset validation va hien cau hinh thuc te de nguoi dung xac nhan.
- Ngay cap nhat: 2026-07-17.

## DEC-039: Khong sua runtime goc, dung app-managed runtime copy

- Trang thai: Chap nhan.
- Boi canh: GPT-SoVITS runtime co the hard-code tham so nhu SoVITS `num_workers=5`, trong khi profile Compatibility can `num_workers=0`.
- Quyet dinh: Khong sua truc tiep runtime GPT-SoVITS goc. Neu can thay tham so runtime khong expose qua config, app tao ban copy trong run directory va chi sua tham so can thiet.
- Quyet dinh: Ban copy phai compile truoc khi dung va ghi checksum/diff summary.
- Ly do: Giu runtime goc sach, co the rollback va khong pha cac Voice/model cu.
- He qua: Command train that phai tro toi config/script app-managed copy khi profile yeu cau tham so da override.
- Ngay cap nhat: 2026-07-17.

## DEC-040: AVS-014.9 chi train mot model chinh cho Voice

- Trang thai: Chap nhan.
- Boi canh: Can giu kien truc Voice/Variant mo rong va tranh no so model theo cam xuc/phong cach.
- Quyet dinh: Voice Thu Minh chi train mot model chinh gan voi Voice ID 0001. Khong train rieng model cho Variant, emotion, style, tuoi/gioi tinh gia lap.
- Ly do: Variant la generate profile/prompt/style/speed/emotion/parameter, khong phai checkpoint hay dataset.
- He qua: Model train lan nay phai luu vao Voice 0001 va van tuong thich voi khong gioi han Variant/Preset/Reference Style sau nay.
- Ngay cap nhat: 2026-07-17.

## DEC-041: Local API MVP dung Python stdlib HTTP server

- Trang thai: Chap nhan.
- Boi canh: FastAPI/Uvicorn chua nam trong dependency hien tai; Bootstrap/Main App khong duoc chet khi thieu dependency API.
- Quyet dinh: MVP Local API dung Python stdlib `http.server` thong qua LocalApiService. Route chi la lop mong va phai goi application services nhu VoiceCatalogService, GenerationJobService va FeatureReadinessService.
- Ly do: Khong them dependency moi khi Python chuan da dap ung MVP localhost API, va tranh lam First-Run Setup phuc tap hon.
- He qua: OpenAPI tu dong chua co trong MVP. Neu sau nay chuyen sang FastAPI, contract service va docs/LOCAL_API_V1.md phai giu tuong thich.
- Ngay cap nhat: 2026-07-17.

## DEC-042: Bootstrap phai chay duoc khi thieu PySide6

- Trang thai: Chap nhan.
- Boi canh: May moi co the chua cai PySide6 nen `src/main.py` se crash neu duoc goi truc tiep.
- Quyet dinh: Bootstrap entry point khong import PySide6. Bootstrap dung RuntimeEnvironmentManager va FeatureReadinessService de quyet dinh mo Main Application hay First-Run Setup.
- Ly do: Nguoi dung pho thong can huong dan tieng Viet thay vi stack trace tho.
- He qua: EXE production sau nay nen tro vao Bootstrap Launcher truoc, khong tro thang vao Main Application.
- Ngay cap nhat: 2026-07-17.

## DEC-043: Reading Style Profile tach khoi Voice model

- Trang thai: Chap nhan.
- Boi canh: Voice can mot model chinh on dinh, nhung phong cach doc/prosody can co the dung lai, backup va ap dung linh hoat.
- Quyet dinh: Reading Style Profile co ID rieng dang `style_000001`, khong phai Voice, khong phai Variant va khong phai checkpoint.
- Quyet dinh: Mot Style Profile co the dung cho nhieu Voice; Voice chi lien ket style profile mac dinh qua `reading_style`.
- Ly do: Tranh train nhieu model chi vi cach doc va giu kien truc VoiceID -> mot model chinh -> nhieu Variant/Preset/Style.
- He qua: Style Profile repository/service/export/import phai tach rieng khoi VoiceService va khong sua Voice ID.
- Ngay cap nhat: 2026-07-17.

## DEC-044: Style Profile extraction khong duoc ready gia

- Trang thai: Chap nhan.
- Boi canh: AVS-014.11 moi tao foundation, chua co prosody analyzer that.
- Quyet dinh: Neu chua co analyzer that, Style Profile extraction phai o trang thai pending/source_ready/degraded/blocked, khong danh dau ready.
- Ly do: Tranh UI/API va Generate tin nham rang prosody da duoc trich xuat that.
- He qua: FeatureReadinessService phai bao `style_profile_extraction` blocked va `style_profile_generation_usage` degraded cho den khi co analyzer/engine support that.
- Ngay cap nhat: 2026-07-17.

## DEC-045: `.avstyle` export mac dinh chi chua du lieu phan tich

- Trang thai: Chap nhan.
- Boi canh: Style Profile can backup/import portable nhung khong duoc ro ri dataset/model/path ca nhan.
- Quyet dinh: `.avstyle` la ZIP package co manifest, checksums, style_profile.json, prosody, indexes va references/manifest.json.
- Quyet dinh: Export mac dinh khong gom MP3 goc, dataset goc, model, checkpoint, token hoac absolute path.
- Ly do: Bao ve du lieu ca nhan va giu package nhe/portable.
- He qua: Neu sau nay muon export selected reference clips, phai co tuy chon rieng va manifest ro rang.
- Ngay cap nhat: 2026-07-17.

## DEC-046: UI Style Profile dung service, khong doc repository truc tiep

- Trang thai: Chap nhan.
- Boi canh: UI redesign can giu ranh gioi kien truc de sau nay them API/automation.
- Quyet dinh: Style Profile UI chi goi StyleProfileService/ExportService va hien readiness, khong tu doc/ghi repository.
- Ly do: Giu UI mong, de test va tranh logic nghiep vu nam trong widget.
- He qua: Repository chi doc/ghi, Service la contract chinh cho UI/API.
- Ngay cap nhat: 2026-07-17.

## DEC-047: Tach Training Dataset, Voice DNA va Speaker Reference

- Trang thai: Chap nhan.
- Boi canh: TrainingPage can lam ro ba loai du lieu de tranh nguoi dung nham dataset train voi phong cach doc hoac audio clone giong.
- Quyet dinh: Training Dataset thuoc Training domain; Reading Style Profile / Voice DNA thuoc Style Profile domain; Speaker Reference thuoc Voice/Speaker Reference domain.
- Quyet dinh: TrainingPage chi chon/khoi tao workflow tham chieu, khong tao repository Style Profile thu hai va khong tao Voice DNA gia.
- Ly do: Giu single source of truth va tranh duplicate ownership giua TrainingPage, VoicePage, StyleProfilePage va GeneratePage.
- He qua: VoiceConfig duoc mo rong migration-safe bang `speaker_reference` va `training_reference` nhung van giu `reference_audio`/`reference_text` legacy.
- Ngay cap nhat: 2026-07-17.

## DEC-048: Rename la display-name only, ID bat bien

- Trang thai: Chap nhan.
- Boi canh: Voice va Style Profile can doi ten hien thi nhung cac lien ket Project, Variant, Generate va backup phai on dinh.
- Quyet dinh: Voice rename phai giu Voice ID, reference, Variant va model path; Style Profile rename chi doi display_name, giu style_profile_id va folder.
- Ly do: ID moi la khoa on dinh; ten hien thi co the thay doi theo nguoi dung.
- He qua: Rename phai co validation ten rong, ten qua dai, control character va duplicate khi co rui ro.
- Ngay cap nhat: 2026-07-17.

## DEC-049: Project ID bat bien, display name co the doi

- Trang thai: Chap nhan.
- Boi canh: Project can duoc doi ten hien thi ma khong pha Voice, Style Profile, Training, Generate, API va backup.
- Quyet dinh: Project ID la khoa ky thuat bat bien. Project display_name la ten nguoi dung nhin thay va co the doi.
- Quyet dinh: Project moi uu tien folder ID-based dang `project_000001`; Project legacy folder theo ten van load duoc bang resolver mem.
- Ly do: Ten hien thi co the thay doi, folder legacy da ton tai, con lien ket lau dai can ID on dinh.
- He qua: Rename Project chi doi display_name, khong rename folder, khong doi Project ID va khong doi Voice/Style/Variant ID.
- Ngay cap nhat: 2026-07-17.

## DEC-050: Archive Project khong phai Delete

- Trang thai: Chap nhan.
- Boi canh: Project chua du lieu that va co the rat lon, khong duoc mat du lieu vi thao tac UI.
- Quyet dinh: Sprint Project Manager chi expose Archive/Restore Archive. Delete vinh vien bi khoa trong UI va service bao loi neu goi truc tiep.
- Ly do: Bao ve du lieu nguoi dung va phu hop yeu cau khong xoa Project/workspace that.
- He qua: Archived Project van nam trong registry va folder du lieu khong bi xoa.
- Ngay cap nhat: 2026-07-17.

## DEC-051: Export khac Backup

- Trang thai: Chap nhan.
- Boi canh: Export can portable/an toan; Backup dung de khoi phuc cung moi truong.
- Quyet dinh: Export Project la package nhe co manifest va path traversal guard, mac dinh khong gom cache/temp/output/model lon. Backup luu metadata/config de restore an toan va co safety backup truoc restore/repair.
- Ly do: Tranh leak path/secret va tranh copy file lon khi chua co xac nhan.
- He qua: Full export asset lon can tuy chon rieng va canh bao dung luong o sprint sau.
- Ngay cap nhat: 2026-07-17.
## DEC-052: Reference asset ID is identity

- Quyet dinh: Reference ben vung duoc lien ket bang `asset_id`, `pair_id`, `segment_id` va manifest ID.
- Ly do: Filename, display name va absolute path co the doi khi nguoi dung rename/move/delete file goc.
- He qua: Legacy path van load nhung chi la fallback/provenance.

## DEC-053: Managed copy is durable reference

- Quyet dinh: File goc ben ngoai app khong phai ban luu ben vung duy nhat; Reference Vault la ban app quan ly.
- Ly do: Project/Voice/Style rename, archive, duplicate, backup/export/import khong duoc lam mat reference da chon.
- He qua: Workflow ready/valid/official nen co managed copy hoac user xac nhan external-only.

## DEC-054: Metadata backup differs from complete backup

- Quyet dinh: Metadata backup chi gom config/registry/manifest; complete backup moi gom media managed reference.
- Ly do: Tranh hieu nham backup nhe la package doc lap.
- He qua: UI/report phai ghi ro package co doc lap hay khong.

## DEC-055: Job ID la identity bat bien

- Trang thai: Chap nhan.
- Boi canh: Tac vu dai can persistence, log, dependency, API va recovery qua restart.
- Quyet dinh: Moi Job co `job_id` bat bien dang `job_000001`. Display name chi la ten hien thi va co the doi.
- Ly do: Khong dung title, index hoac filename lam identity vi chung co the doi.
- He qua: JobRepository, logs, dependency va Local API dung `job_id`.
- Ngay cap nhat: 2026-07-17.

## DEC-056: Pause/Cancel Job phai cooperative

- Trang thai: Chap nhan.
- Boi canh: Kill thread cuong buc co the corrupt Project, Reference Vault, output hoac state.
- Quyet dinh: Worker chi pause/cancel tai safe point, ghi checkpoint/log/state truoc khi dung.
- Ly do: Bao ve du lieu va cho phep resume/retry an toan.
- He qua: Job khong pausable/cancellable phai bao ro, UI disable/bao loi thay vi fake action.
- Ngay cap nhat: 2026-07-17.

## DEC-057: Queue persistent va khong auto-resume job nguy hiem

- Trang thai: Chap nhan.
- Boi canh: App co the crash/close khi job dai dang chay.
- Quyet dinh: queued giu queued, paused giu paused, running cu thanh interrupted. Auto-resume interrupted mac dinh tat.
- Ly do: Tranh chay lai train/generate/analyzer nguy hiem khi nguoi dung chua xac nhan.
- He qua: Recovery state phai ghi ro previous state va policy manual_resume_required.
- Ngay cap nhat: 2026-07-17.
# DEC-058: Resource Manager dieu phoi Job truoc khi Worker chay

- Trang thai: Chap nhan.
- Boi canh: Train, Generate va analyzer sau nay co the can CPU/RAM/GPU/VRAM/Disk khac nhau; queue can biet job nao du tai nguyen truoc khi khoi dong.
- Quyet dinh: Job phai co ResourceRequirement va duoc ResourceDecisionService danh gia truoc khi Worker chay. Neu chua du tai nguyen, job vao `waiting_resource`, khong bi fake failed va khong chan toan bo queue.
- Quyet dinh: ResourceLeaseManager cap lease persistent khi job duoc chon chay va release khi job ket thuc, pause, cancel, fail, interrupted hoac app shutdown.
- Ly do: Bao ve GPU/VRAM/Disk, tranh chay trung job nang va giu recovery ro rang.
- He qua: Moi workflow nang sau nay phai khai bao ResourceRequirement ro rang thay vi tu chay thang.
- Ngay cap nhat: 2026-07-18.

---

# DEC-059: Generate foundation phai tach khoi inference that

- Trang thai: Chap nhan.
- Boi canh: Generate that can engine/runtime/Voice model hop le, trong khi app can nen request/session/plan/manifest de UI/API/Job Queue dung chung truoc.
- Quyet dinh: AVS-014.16 chi tao Generate foundation gom source snapshot, normalized text, document/chapter/unit, plan, manifest, registry, resume/retry inspection va prepare job.
- Quyet dinh: Foundation khong duoc goi GPT-SoVITS/engine synthesize, khong tao WAV/MP3 gia va khong danh dau completed neu output audio chua ton tai that.
- Ly do: Tranh fake success, bao ve output va cho phep sprint sau noi inference that tren contract on dinh.
- He qua: GeneratePrepareJobWorker la CPU-light; real Generate worker sau nay phai khai bao ResourceRequirement rieng va validate Voice/runtime truoc khi chay.
- Ngay cap nhat: 2026-07-18.

---

# DEC-060: Readiness AVS-014.16 phai bao dung truth status

- Trang thai: Chap nhan.
- Boi canh: Post-implementation verification phat hien mot so claim de gay hieu nham la Generate execution/output da san sang.
- Quyet dinh: Local API readiness dung `planning_ready_execution_unavailable`; Feature readiness tach planning READY, inspection READY, execution/output UNAVAILABLE va full audio validation DEGRADED.
- Quyet dinh: Generate Session/Plan UI, resume/retry execution, production artifact lifecycle va WAV/MP3 output that khong duoc danh dau completed trong AVS-014.16.
- Ly do: Tranh overclaim, giu UI/API biet dung phan nao co the goi that va phan nao con bi chan.
- He qua: Sprint sau noi inference that phai them worker/action rieng va nang readiness tung capability khi co test thuc.
- Ngay cap nhat: 2026-07-18.

---

# DEC-061: Generate foundation success phai qua reconstruction, frozen plan va artifact validation

- Trang thai: Chap nhan.
- Boi canh: AVS-014.16 can chung minh foundation that, khong chi co model/schema.
- Quyet dinh: Plan chi duoc frozen khi reconstruction verifier pass va immutable checksum duoc persist/read-back.
- Quyet dinh: Artifact chi duoc xem la valid sau reservation, temp-to-final promotion va WAV validation co ban pass.
- Quyet dinh: Attempt/Unit khong duoc success chi vi Job success, provider return hoac file ton tai; phai co valid Artifact dung lineage.
- Quyet dinh: Test-only WAV provider chi duoc dung trong tests, production readiness van bao Generate execution/output UNAVAILABLE khi chua co handler that.
- Ly do: Tranh fake success, giu kha nang resume/retry/recovery an toan va khong tao audio gia.
- He qua: Sprint sau khi noi GPT-SoVITS real handler phai su dung cung Artifact lifecycle va validation gate nay.
- Ngay cap nhat: 2026-07-18.

---

# DEC-062: Resource Policy v2 resolve rieng voi runtime projection Phase 1

- Trang thai: Chap nhan.
- Boi canh: Resource Safety Hardening Phase 1 can luu schema v2, feature flags, safe defaults va fallback, nhung yeu cau tuyet doi khong doi scheduling/runtime behavior hien tai.
- Quyet dinh: `ResourcePolicyService.resolve()` la entrypoint cho effective Resource Policy v2 va tra `ResolvedResourcePolicy` co fingerprint deterministic.
- Quyet dinh: `ResourcePolicyService.load()` trong Phase 1 tiep tuc tra projection tuong thich cho consumer runtime cu de khong bat enforcement, reserve, CPU fallback, batch hoac thread behavior moi.
- Quyet dinh: Feature modes ban dau chi monitor_only hoac disabled; khong capability nao tu dong enforced sau migration.
- Quyet dinh: Global Application Policy la scope duy nhat; khong ho tro Project/Voice override.
- Ly do: Cho phep dong bang config/policy foundation truoc khi tung consumer runtime duoc migrate va test o Phase sau.
- He qua: Module scheduling/runtime khong duoc coi policy v2 la enforced cho den khi co Phase 2 duoc phe duyet rieng.
- Ngay cap nhat: 2026-07-22.

---

# DEC-063: Resource Decision v2 la shadow observation trong Phase 2

- Trang thai: Chap nhan.
- Boi canh: Can validate snapshot, unknown/invalid/stale state va tinh Resource Decision v2 ma khong pha scheduling hien co.
- Quyet dinh: Phase 2 gan `shadow_observation` vao `ResourceDecision`, gom actual_decision, shadow_decision, reason_codes, snapshot_status, workload_class, policy_fingerprint va flags would_block/would_wait/confirmation_required.
- Quyet dinh: Queue va JobRunner van chi dung actual legacy decision/status; shadow decision khong duoc block Queue, doi job state, cap/release lease, doi CPU fallback, thread, batch, Runtime Guard hoac Process Supervisor.
- Quyet dinh: Shadow decision dung `ResourcePolicyService.resolve()` va `ResolvedResourcePolicy`; actual legacy behavior tiep tuc dung `load()` projection tuong thich.
- Ly do: Cho phep quan sat deterministic truoc khi enforcement, tranh fail-open voi unknown snapshot nhung cung khong lam doi runtime behavior.
- He qua: Resource Decision v2 enforcement can phase rieng va tests rieng truoc khi duoc dung de dieu phoi Queue that.
- Ngay cap nhat: 2026-07-22.

---

# DEC-064: Lease Lifecycle v2 la monitor-only observation trong Phase 3

- Trang thai: Chap nhan.
- Boi canh: Lease legacy dang duoc Job Queue/JobRunner dung de dieu phoi runtime, nhung can nen v2 de quan sat TTL, renew, expiry, stale, duplicate va reconciliation truoc khi enforcement.
- Quyet dinh: Phase 3 them `ResourceLeaseV2`, `ResourceLeaseObservation` va `ResourceLeaseShadowEvaluator` de tinh shadow lifecycle; actual lease legacy van la source runtime.
- Quyet dinh: Observation path phai dung `ResourcePolicyService.resolve()`/`ResolvedResourcePolicy`, co `lease_renew_interval_seconds`, `stale_lease_handling_mode` va policy fingerprint; khong hard-code policy trong ResourceLeaseManager.
- Quyet dinh: `ResourceLeaseManager.shadow_observations()` va `shadow_observation_for_job()` khong duoc goi `cleanup_stale()`, `renew()`, `release()`, `release_job()` hoac `save_all()` khi chi quan sat.
- Ly do: Cho phep phat hien leak/duplicate/stale/reconciliation can thiet ma khong doi scheduling, Job state, pause/cancel/retry hoac runtime behavior.
- He qua: Phase enforcement sau nay phai co phe duyet va tests rieng truoc khi shadow action duoc dung de block queue hoac mutate lease that.
- Ngay cap nhat: 2026-07-22.

---

# DEC-065: Lease Lifecycle v2 enforcement chi kich hoat bang policy enforce

- Trang thai: Chap nhan.
- Boi canh: Phase 3 da co observation monitor-only; Phase 4 can enforcement co the rollback ma khong doi default production.
- Quyet dinh: `resource_lease_v2_mode=enforce` moi kich hoat acquire/renew/release/reconcile v2. `disabled` va `monitor_only` giu legacy/Phase 3 behavior.
- Quyet dinh: `enforce` la literal chinh cho Phase 4; `enforced` cu duoc ho tro nhu legacy alias de load policy/data cu.
- Quyet dinh: Enforce phai fail-safe voi corrupt/unavailable lease store, khong ghi de corrupt store, va phai dung stable reason codes.
- Quyet dinh: Phase 4 khong bao gom Process Supervisor, kill-tree, Runtime Guard action hay Thread Budget enforcement.
- Ly do: Cho phep validate lifecycle enforcement deterministic truoc khi noi process/runtime action nguy hiem hon.
- He qua: Rollback ve monitor_only khong mat lease data; production default khong thay doi sau migration.
- Ngay cap nhat: 2026-07-22.

---

# DEC-066: Process Supervisor Phase 5 chi la foundation monitor-only

- Trang thai: Chap nhan.
- Boi canh: Can nen quan sat process dai/nang tai nguyen truoc khi co bat ky production kill-tree nao.
- Quyet dinh: Phase 5 them ProcessIdentity, ProcessSupervisorObservation, provider abstraction, registry atomic va shutdown plan simulated.
- Quyet dinh: `process_supervisor_mode` mac dinh monitor_only; enforce trong Phase 5 chi la contract/gate fail-safe, khong tu kill process production.
- Quyet dinh: Process identity khong chi dua vao PID ma phai gom start time, command/executable fingerprint, owner/job/lease va policy fingerprint.
- Quyet dinh: Unknown identity, permission denied, provider unavailable, tree incomplete, PID reuse hoac owner mismatch phai defer/non-destructive.
- Ly do: Bao ve process ngoai ownership boundary va tranh kill nham Codex, terminal, Python nguoi dung hoac process he thong.
- He qua: Phase sau muon production kill-tree phai co phe duyet, provider production va tests rieng.
- Ngay cap nhat: 2026-07-22.

---

# DEC-067: Runtime Guard Phase 6 chi la action foundation simulated

- Trang thai: Chap nhan.
- Boi canh: Sau Resource Policy, Decision, Lease va Process Supervisor foundation, can nen Runtime Guard de phan loai pressure va de xuat action ma chua duoc phep tac dong production process/job.
- Quyet dinh: Phase 6 them `runtime_guard_mode`, `RuntimeGuardObservation`, `RuntimeGuard` va simulated action executor; default la monitor_only.
- Quyet dinh: Runtime Guard phai dung `ResourcePolicyService.resolve()`/`ResolvedResourcePolicy` lam single source of truth cho mode, cooldown, hysteresis, retry va simulated action allow-list.
- Quyet dinh: Enforce trong Phase 6 chi duoc goi simulated executor; terminate/kill-tree destructive luon deferred va khong goi `taskkill`, `os.kill`, `psutil` kill/terminate.
- Ly do: Cho phep validate pressure/action contract deterministic truoc khi Phase sau noi action production nguy hiem hon.
- He qua: Runtime Guard production pause/terminate/kill-tree, Thread Budget enforcement va JobRunner safety integration can phase rieng va tests rieng.
- Ngay cap nhat: 2026-07-22.

---

# DEC-068: Thread Budget Phase 7 chi la enforcement foundation simulated

- Trang thai: Chap nhan.
- Boi canh: Can nen kiem soat CPU thread theo workload/job/engine truoc khi noi vao JobRunner hoac engine production.
- Quyet dinh: Phase 7 them policy additive, `ThreadBudgetObservation`, `ThreadBudgetService` va simulated executor; default `thread_budget_mode=monitor_only`.
- Quyet dinh: Allocation, oversubscription, nested parallelism, environment/runtime plan, restore, cooldown va retry phai dung `ResourcePolicyService.resolve()`/`ResolvedResourcePolicy`.
- Quyet dinh: Enforce trong Phase 7 chi simulated; khong mutate `os.environ`, khong goi CPU affinity, khong goi production runtime setter va khong doi JobQueue/engine behavior.
- Ly do: Tranh pha runtime/engine production khi chua co contract rollback/integration test day du.
- He qua: Production Thread Budget enforcement va JobRunner safety integration can phase rieng va tests rieng.
- Ngay cap nhat: 2026-07-22.

---

# DEC-069: Thread Budget Phase 8 enforcement integration phai scoped va adapter-gated

- Trang thai: Chap nhan.
- Boi canh: Sau Phase 7 can noi Thread Budget vao JobRunner/engine theo cach co rollback, nhung khong duoc bat enforcement mac dinh hoac mutate system-wide environment.
- Quyet dinh: Phase 8 them `ThreadBudgetEngineCapability`, `ThreadBudgetApplyState`, capability registry, runtime adapter contract va `ScopedThreadBudgetExecutor`.
- Quyet dinh: JobRunner chi kich hoat Thread Budget khi duoc inject service; `monitor_only` khong mutate, `enforce` can engine capability/adapter dang ky va apply truoc workload, restore sau workload.
- Quyet dinh: Environment change la scoped dict trong `JobExecutionContext`, khong ghi `os.environ`; runtime thread setting chi qua adapter da dang ky; khong CPU affinity.
- Ly do: Cho phep validate production integration boundary deterministic truoc khi Phase 9 dang ky adapter GPT-SoVITS that.
- He qua: Rollback ve monitor_only hoac bo inject service se tra JobRunner ve behavior cu; Phase 9 van can engine-specific adapter va rollout rieng.
- Ngay cap nhat: 2026-07-22.

---
