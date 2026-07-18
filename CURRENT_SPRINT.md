# Current Sprint

## Trạng thái hiện tại

- AVS-013 hoàn thành.
- AVS-013.5 hoàn thành.
- AVS-013.6 hoàn thành.
- AVS-013.7 Text ↔ MP3 Matching Rules hoàn thành.
- AVS-013.8 Dataset Health hoàn thành.
- AVS-013.9 Dataset Workflow hoàn thành.
- Sprint tiếp theo chưa bắt đầu.

## Mốc ổn định gần nhất

- Complete AVS-013.6: Quality-First Dataset Alignment.
- Complete AVS-013.7: Text ↔ MP3 Matching Rules.
- Complete AVS-013.8: Dataset Health.
- Complete AVS-013.9: Dataset Workflow.
- Git commit hiện tại: `3b583e1`.

## Thành quả chính

- Faster-Whisper chạy local.
- Timestamp thật và word timestamp.
- Chia clip dài không cắt giữa từ.
- Quality config tập trung.
- Metadata chỉ chứa valid clip được phép train.
- Weak source không train tự động.
- Progress payload cho job dài.
- Runtime Profile nền tảng.
- Text ↔ MP3 ghép theo số chương trước.
- Một text có thể ghép nhiều MP3 cùng chương theo thứ tự part.
- File test hoặc gần giống test không ghép tự động.
- File không lấy được số chương bị loại khỏi ghép tự động.
- Dataset Workflow có Input Folder, Output Folder và Use Input Folder as Output.
- Dataset Health báo lỗi trước Alignment.
- Dataset Health có lỗi chặn thì không chạy Alignment.

## Quyết định đã chốt

- Quality-first.
- `similarity_threshold = 90`
- `min_clip_duration = 2.0`
- `max_clip_duration = 10.0`
- `target_clip_duration = 6.0`
- `max_source_error_rate = 0.35`
- `min_valid_segments_per_source = 3`
- `allow_ratio_fallback = False`
- `sample_rate = 32000`
- `language = vi`

## Blocker còn lại

- Cần review suspicious.
- Cần xử lý Dataset Health errors của workspace Thu Minh trước AVS-014.
- Chưa bắt đầu AVS-014 Train thật.

## Task đề xuất tiếp theo

- Review và xử lý Dataset Health report.
- Sau đó mới AVS-014.

## File cần đọc khi quay lại

- AGENTS.md
- ROADMAP.md
- docs/Architecture.md
- CURRENT_SPRINT.md
- docs/DECISIONS.md
- src/services/alignment_service.py
- src/services/train_audio_prep_service.py
- src/models/alignment_quality_config.py
- src/services/runtime_profile_service.py
- src/models/runtime_profile.py

## Không được tự ý

- Không đưa suspicious vào metadata.
- Không hạ threshold để tăng dữ liệu.
- Không dùng ratio fallback cho valid.
- Không đổi Voice ID.
- Không phá portable path.
- Không hard-code ổ đĩa.

---

## Cập nhật AVS-013.10 Dataset Repair

- AVS-013.10 hoàn thành ở mức service/model/config.
- Dataset Repair phát hiện: duplicate, empty_file, broken_file, missing_audio, missing_text, filename_content_mismatch, test_version, invalid_filename.
- Duplicate được repair an toàn bằng cách giữ bản tốt nhất đã được DatasetService chọn và copy bản trùng vào cache ignored.
- Các lỗi không sửa an toàn được chuyển sang skipped để Manual Review, không dừng toàn batch.
- Workflow đã chuẩn bị lựa chọn Auto Repair hoặc Manual Review cho UI sau này.
- Kiểm tra workspace Thu Minh: repaired 55 duplicate, skipped 42 lỗi còn cần review trước AVS-014.

## Task tiếp theo

- Review các skipped errors còn lại trong Dataset Repair report.
- Chỉ bắt đầu AVS-014 sau khi Dataset Health/Repair không còn blocker train thật.

---

## Cập nhật AVS-013.11 Dataset Review

- AVS-013.11 hoàn thành ở mức service/model.
- Dataset Review hỗ trợ mode Auto/Manual thông qua DatasetReviewConfig.
- Review item gồm source_audio, source_text, reason, suggestion và status pending/approved/rejected/ignored.
- ReviewService hỗ trợ approve_all, reject_all, ignore_all và filter theo reason/code.
- Dataset chỉ được phép đi tiếp khi blocking_errors = 0 hoặc toàn bộ blocking_errors đã có trạng thái reviewed.
- TrainAudioPrepService có thể nhận review_report; nếu không truyền report thì hành vi chặn Dataset Health giữ nguyên như cũ.
- Kiểm tra workspace Thu Minh: sau Repair còn 42 blocking items; Review tạo 42 pending; approve_all làm train_allowed = True.

## Task tiếp theo

- Người dùng cần chốt approve/reject/ignore cho 42 review items của workspace Thu Minh trước AVS-014.
- Sau khi chốt Review mới bắt đầu AVS-014 Train thật.

---

## Cập nhật AVS-014 GPT-SoVITS Training

- AVS-014 đã có Training validation pipeline ở mức service/model.
- TrainConfig tập trung tham số train, mặc định validation_only=True.
- TrainJobState lưu run_id, checkpoint, model_output, report_path và trạng thái resume.
- TrainingService chỉ train từ metadata.list hợp lệ và kiểm tra WAV bằng ffprobe trước khi train.
- Model output chuẩn bị theo voices/<voice_id>/model/<run_id>/, không lưu model vào Runtime GPT-SoVITS.
- Runtime lấy từ Runtime Profile hiện tại; không hard-code đường dẫn runtime, Python hoặc pretrained model.
- Chưa chạy train thật.
- Chưa chốt batch size, epoch, save interval, learning rate, worker, checkpoint policy, resume policy hoặc pretrained model version.
- Validation-only trên workspace Thu Minh: metadata có 19 clip, tổng thời lượng khoảng 140.04 giây; chưa ready vì review_report còn pending và chưa có Runtime Profile mặc định.

## Blocker AVS-014

- Cần người dùng chốt approve/reject/ignore cho review_report Thu Minh.
- Cần cấu hình Runtime Profile mặc định có runtime_path, python_path và pretrained_model_path.
- Cần chốt tham số train trước khi chạy smoke_test hoặc train thật.

---

## Cập nhật AVS-014.1 Runtime Profile và GPT-SoVITS Smoke Test

- AVS-014.1 hoàn thành ở mức validation/smoke test tối thiểu, chưa train model hoàn chỉnh.
- Dataset Review Thu Minh đã được chốt theo quyết định: test_version = ignored; broken_file, empty_file, empty_content, filename_content_mismatch = rejected.
- Review summary Thu Minh: approved 0, rejected 20, ignored 22, pending 0, train_allowed = True.
- Runtime Profile mặc định `gpt_sovits_v2pro_default` đã trỏ tới GPT-SoVITS v2Pro runtime thật ngoài app.
- Runtime validation READY: Python 3.9.13, torch 2.0.0+cu118, CUDA True, faster-whisper 1.1.1, GPU Quadro P1000.
- Phát hiện script train thật: `GPT_SoVITS/s1_train.py` và `GPT_SoVITS/s2_train.py`.
- Phát hiện pretrained v2Pro: `v2Pro/s2Gv2Pro.pth`, `v2Pro/s2Dv2Pro.pth`, `s1v3.ckpt`, BERT và HuBERT.
- Validation-only Thu Minh đạt: 19 clip, khoảng 140.04 giây, không lỗi.
- Smoke test tối thiểu đã gọi runtime Python thật, import GPT-SoVITS config, kiểm tra CUDA, đọc metadata, đọc WAV đầu tiên và tạo checkpoint smoke trong `voices/0001/model/avs0141_smoke_20260716_053444/`.

## Blocker còn lại AVS-014

- Chưa chạy full train GPT-SoVITS.
- Chỉ mới smoke test runtime/process, chưa gọi trực tiếp `s1_train.py`/`s2_train.py` vì cần dataset train format đầy đủ của GPT-SoVITS và tham số train được chốt.
- Cần người dùng chốt tham số train thật: batch size, epoch, save interval, learning rate, worker, checkpoint/resume policy và pretrained model version.

---

## Cập nhật AVS-014.2 Full Dataset Preparation

- Full Dataset Preparation Thu Minh đã chạy hoàn tất bằng runner có resume state, không khởi chạy lại từ đầu.
- Runner xử lý 68/68 source, stderr rỗng, không có lỗi runtime.
- Output alignment nằm trong `cache/avs0142_full_alignment_thu_minh/`.
- `metadata.list` chỉ chứa valid clip: 13 clip, tổng thời lượng 93.98 giây, trung bình 7.23 giây/clip.
- Suspicious: 76 clip; errors: 0.
- 2 source bị bỏ toàn file vì `source_error_rate_exceeded`: `5137.mp3` và `5164.mp3`.
- Validate metadata bằng ffprobe đạt: không trùng clip, WAV tồn tại, đọc được, mono, pcm_s16le, 32000 Hz, transcript không rỗng.
- Compile, script tests với `PYTHONPATH=src`, và UI smoke đều đạt.

## Blocker còn lại trước Train thật

- Dataset valid hiện chỉ có 13 clip / 93.98 giây, quá ít cho train chất lượng cao.
- Cần người dùng quyết định: train thử với dataset nhỏ hiện có, hay review/sửa suspicious để tăng số clip valid trước khi train thật.
- Chưa chạy Train GPT-SoVITS thật.
- Chưa Generate.

---

## Cập nhật AVS-014.3 Suspicious Review & Recovery

- Đã thêm quy trình recovery riêng cho suspicious, không thay pipeline alignment chính.
- Recovery không hạ `similarity_threshold` dưới 90 và không dùng ratio fallback cho valid.
- Recovery thử match tuần tự quanh timestamp dự kiến, cho phép gộp 2-3 ASR segment liền nhau và tách text theo dấu câu.
- Recovery report ghi recovered_valid, still_suspicious, rejected, recovery_method, old_similarity, new_similarity, source_file và reason.
- Metadata recovery được ghi riêng trong cache AVS-014.3, không ghi đè baseline AVS-014.2.
- Preview đã chạy trên 1 source `no_alignment_match`, 1 source `similarity_too_low`, 1 source `source_error_rate_exceeded`.
- Kết quả preview: recovered_valid = 0, valid vẫn là 13 clip / 93.98 giây.
- Không chạy toàn bộ 76 suspicious vì preview không tạo thêm valid clip.

## Blocker sau AVS-014.3

- Nhóm `no_alignment_match` có mẫu text gốc tiếng Trung nên không thể cứu bằng ASR tiếng Việt nếu không có transcript tiếng Việt đúng.
- Nhóm `similarity_too_low` có một số đoạn cải thiện similarity nhưng vẫn dưới 90, cần manual review hoặc text/audio đúng hơn.
- Dataset vẫn dưới 10 phút audio valid, chưa nên train chất lượng cao.

---

## Cap nhat AVS-014.4 Full Dataset Expansion + Voice Architecture Foundation

- Workflow Dataset moi ho tro chon rieng MP3 folder, Text/DOCX folder va Output folder.
- Lua chon cuoi theo Project duoc luu trong ProjectConfig: audio_folder, text_folder, output_folder, use_input_as_output, Voice dang chon va Runtime Profile dang chon.
- DatasetService co scan_folders() de ghep MP3 va Text/DOCX theo so chuong tu hai thu muc rieng.
- FullDatasetPreparationService da gom cac buoc Scan -> Health -> Repair -> Review -> Alignment -> Metadata Validation cho runner/UI sau nay.
- Voice Architecture Foundation da chot: Voice la danh tinh nguoi noi; Variant khong phai model; Preset chua tham so generate; Engine chi sinh audio.
- Kiem tra nguon workspace Thu Minh moi: total_mp3 198, total_text 202, matched 183, blocking_errors 34.
- Alignment toan bo chua chay vi review_report moi con 34 pending va train_allowed = false.

## Blocker AVS-014.4

- Can nguoi dung review/resolve 34 blocking items: missing_audio 4, missing_text 15, test_version 1, broken_file 14.
- Sau khi Review cho phep di tiep moi chay Alignment toan bo nguon moi.
- Chua Train that.
- Chua Generate.

---

## Cap nhat AVS-014.5 Workspace Compatibility + Automatic Review

- Same Folder Mode duoc ho tro cho workspace/<Voice Name>/ hien tai: audio_folder va text_folder cung tro vao mot thu muc.
- Separate Folder Mode van duoc giu cho nguon MP3 va Text/DOCX tach rieng.
- WorkflowService co helper detect_legacy_workspace() de Project/Voice cu tu nhan workspace/<voice_name>.
- Auto Review an toan da ap dung: test_version/missing_audio/missing_text/invalid_filename = ignored; broken_file/empty_file/empty_content/filename_content_mismatch = rejected.
- Auto Review Thu Minh: total 34, pending 0, rejected 14, ignored 20, train_allowed true.
- Alignment da resume va xu ly 12/183 source: 155 valid clips, 50 suspicious, 0 errors, 946.32 giay valid.
- Metadata hien tai validate dat voi 155 clip, khong duplicate.

## Blocker AVS-014.5

- Full Alignment toan bo 183 source chua hoan tat vi runtime du kien nhieu gio.
- Can tiep tuc resume alignment tu cache/avs0145_full_dataset_thu_minh/alignment/alignment_state.json.
- Chua Train that.
- Chua Generate.

---

## Cap nhat AVS-014.6 Generate Architecture Foundation

- Da them nen Generate Architecture cho Standard Mode va AI Style Mode.
- Standard Mode yeu cau mot Voice va mot Variant cu the; service khong tu doi style/variant.
- AI Style Mode yeu cau scope Variant va Style ro rang; neu khong tick gi thi generate bi chan.
- VariantTimeline va StyleTimeline chi nhan decision tai sentence/paragraph/dialogue/scene/pause boundary, khong doi giua tu hoac giua cau.
- SpeedProfile ho tro preset 0.5, 0.75, 1.0, 1.1, 1.2, 1.3, 1.5; custom speed chi hop le khi co custom_min/custom_max.
- Temp workspace tao theo temp/<kind>/<job_id>, output chi de final artifact/report; success thi cleanup, error/stop thi giu lai.
- ProjectConfig luu lua chon Generate cuoi: mode, voice, variant scope, style scope va speed.

## Blocker AVS-014.6

- Cac quyet dinh chinh da duoc chot: default Variant, default Style, custom speed 0.80-1.20 va cleanup policy.
- UI Generate multi-select moi co nen model/service, chua hoan thien UI.
- Chua noi Generate Planning vao engine generate that.

## Quyet dinh da chot cho AVS-014.6

- Moi Voice co default_variant_id, mac dinh la `default`.
- Moi Voice co default_style_id, khong hard-code ten Style.
- AI chi fallback sang default Variant/Style neu default nam trong allowed scope hoac allow_all = true.
- Neu default khong duoc phep, AI chon candidate co confidence cao nhat trong allowed scope.
- Neu khong con candidate hop le, dung Generate.
- Custom speed chi cho phep 0.80 den 1.20; preset 0.5, 0.75, 1.0, 1.1, 1.2, 1.3, 1.5 van la che do dac biet.
- SUCCESS xoa temp; PAUSE/ERROR giu temp/state/progress/log; CANCEL hoi nguoi dung giu hay xoa; RESUME dung temp cu va khong generate lai chunk da xong.
- Variant khong phai model; Variant chi la generate profile/prompt/style/speed/emotion/parameter.
- Style khong phai Voice; Style mo ta cam xuc, cach doc, pacing va expression, co the dung cho nhieu Voice.
- Voice chi giu Dataset, Model, Runtime, Preview va Metadata.
- Engine chi nhan GenerateRequest va tra GenerateAudio, khong quan ly Voice/Variant/Style/Project/Workflow.

## Task tiep theo

- AVS-014.7 Generate UI hoan chinh va Generate that.
- Pham vi AVS-014.7: UI Generate, Engine Adapter, Chunk Merge, Context Analysis, StyleTimeline, VariantTimeline, Audio Merge, Transition va Crossfade.
- Khong Train, khong Voice Morph, khong them kien truc moi ngoai nhung gi da chot.

---

## Cap nhat AVS-014.7 Generate UI + Generate Pipeline

- AVS-014.7 da co Generate UI tren AudioPage cho Standard Mode va AI Style Mode.
- UI ho tro Voice hien tai, Variant, All Variants, Style scope, All Styles, Speed, Output, WAV/MP3 va MP3 bitrate.
- MP3 bitrate mac dinh 192 kbps va ho tro 128/192/256/320 kbps, luu lua chon cuoi theo Project.
- GenerateAudioProfile tap trung pause, crossfade, retry_count va output format; khong rai hard-code trong UI.
- GeneratePipelineService da noi GenerateRequest -> Context/Timeline -> chunk generate -> Audio Merge -> report.
- Standard Mode chi dung Variant duoc chon.
- AI Style Mode chi chon Variant/Style trong scope cho phep.
- Chunk loi sau retry_count = 1 se dung toan job, giu temp/state/log va khong tao final output gia thanh cong.
- Temp generate nam trong temp/generate/<job_id>, khong nam trong Output; success thi cleanup, error thi giu de resume.
- GenerateService co entrypoint generate_request() moi, giu API queue cu.
- Audio merge ho tro WAV va MP3 qua ffmpeg, metadata/report duoc ghi theo job.
- Mock/smoke generate pipeline da pass bang test, chua Train.

## Blocker/ghi chu AVS-014.7

- Generate that can Voice co gpt_model, sovits_model, reference_audio va reference_text hop le.
- UI smoke dat khi chay ngoai sandbox de doc PySide6 trong user site-packages.
- Crossfade/pause hien da co config tap trung; DSP nang cao de phat hien natural silence/crossfade boundary an toan can tiep tuc tinh chinh o sprint Generate audio quality.
- Chua Train that.
- Chua Voice Morph.

## Task tiep theo

- Kiem tra Generate that voi mot Voice da co model hop le.
- Hoan thien Adapter mapping tham so rieng GPT-SoVITS neu runtime yeu cau tham so bo sung.
- Tinh chinh audio merge quality: natural silence detection, pause insertion va crossfade boundary safety.

---

## Cap nhat AVS-014.8 Full Alignment Completion + Real Training Preparation

- Resume Full Alignment Thu Minh tu checkpoint hien co, khong chay lai tu dau.
- Alignment hoan tat 183/183 source hop le.
- Final metadata duoc rebuild tu `alignment_state.json`, khong dua suspicious vao train.
- Metadata cu 155 dong duoc thay bang metadata final 2329 clip trainable.
- Dataset Quality Report da sinh trong `cache/avs0145_full_dataset_thu_minh/dataset_quality_report.json`.
- Reference Audio candidates da sinh trong `cache/avs0145_full_dataset_thu_minh/reference_audio_candidates.json`.
- Train validation_only dat voi Runtime Profile `gpt_sovits_v2pro_default`: Python 3.9.13, torch 2.0.0+cu118, CUDA, Quadro P1000 4096 MiB.
- Dataset final: 2329 clip, tong thoi luong 13232.40 giay, similarity min/avg/max = 90.00 / 95.62 / 100.00.
- Chua Train that.
- Chua Generate.

## Blocker AVS-014.8

- Python hien tai cua UI/test la `C:\Program Files\Python312\python.exe` dang thieu `pytest` va `PySide6`, nen chua chay duoc pytest/UI smoke bang interpreter nay.
- Can nguoi dung xac nhan cai dependency hoac chon dung interpreter da co PySide6/pytest.
- Can nguoi dung nghe va chot Reference Audio cuoi.
- Can nguoi dung chot tham so Train that truoc khi goi `s1_train.py`/`s2_train.py`.

---

## Cap nhat AVS-014.9 Runtime Training Profile

- Da them Runtime Training Profile cho Cài đặt o muc model/service/UI.
- Ho tro mode Auto, Compatibility, Performance va Custom.
- Auto Detect Hardware phat hien GPU, VRAM, CUDA, CPU thread, RAM, Python runtime va Runtime Profile.
- May hien tai Quadro P1000 4 GB duoc Auto chon cau hinh Compatibility:
  - runtime_profile_id = `gpt_sovits_v2pro_default`
  - compute = cuda
  - batch_size = 1
  - num_workers = 0
  - GPT config = s1longer.yaml
  - GPT epochs = 20
  - SoVITS config = s2v2Pro.json
  - SoVITS epochs = 50
  - save_interval = 1
  - resume_policy = manual
- Da them app-managed runtime copy: copy config/script vao run directory va chi sua tham so can thiet, khong sua runtime goc.
- Pre-flight app-managed copy tao tai `voices/0001/model/avs0149_preflight_runtime_20260717_053711/runtime_copy`.
- SoVITS script copy chi doi `num_workers=5` thanh `num_workers=0`; compile copy dat.
- Reference Audio chinh da chot: `cache/avs0145_full_dataset_thu_minh/alignment/clips/000135_028_001.wav`.
- Train validation_only voi profile moi dat: 2329 clip, 13232.40 giay, CUDA/Quadro P1000, khong warning/error.

## Blocker AVS-014.9

- Chua Train that vi can nguoi dung xac nhan lan cuoi sau khi xem pre-flight/app-managed copy.
- Chua cai/doi interpreter co `pytest` va `PySide6`; script tests chay duoc bang `python tests/...`, nhung `python -m pytest` va UI smoke bang Python hien tai van bi chan.

---

## Cap nhat AVS-014.9 Runtime & Training Guide

- Da hoan thien huong dan tieng Viet trong Cài đặt -> Runtime & Training.
- Giao dien Runtime & Training da Viet hoa cac mode: Tu dong, Tuong thich, Hieu nang, Tuy chinh.
- Moi mode co mo ta ngan, tooltip va noi dung chi tiet de nguoi dung khong ranh ky thuat van hieu.
- Da them nut:
  - Phat hien lai phan cung.
  - Kiem tra Runtime.
  - Khoi phuc cau hinh khuyen nghi.
  - Xem cau hinh thuc te se dung.
  - Sao chep bao cao kiem tra.
  - Xem giai thich chi tiet.
- Huong dan chi tiet mo bang dialog rieng va co the sao chep noi dung.
- Noi dung giai thich cac tham so Runtime, Compute, Batch Size, Workers, VRAM Profile, GPT Epochs, SoVITS Epochs, Save Interval, Resume Policy va Auto Detect Hardware.
- Da them canh bao tieng Viet de hieu cho CUDA unavailable, runtime missing, out of memory va pretrained missing.
- Hardware Summary sinh tu du lieu detection/mock, khong hard-code ten GPU.
- Chua Train that.

---

## Cap nhat AVS-014.9 Interpreter + Train Command Pre-flight

- Xac dinh Python ung dung hien tai la `C:\Program Files\Python312\python.exe`.
- Python ung dung hien tai thieu `PySide6`, `pytest`, `python-docx` va `faster-whisper`; chua cai dependency tu dong.
- Python runtime GPT-SoVITS la `F:\AI\GPT-SoVITS-v2pro-20250604\runtime\python.exe`, co `faster-whisper` va `torch`, khong dung de chay UI.
- Nut Runtime & Training trong Settings da co handler that cho detect hardware, validate runtime, reset recommended, xem cau hinh va copy report.
- Pre-flight AVS-014.9 moi tao run directory `voices/0001/model/avs0149_thu_minh_train_20260717_061215`.
- Validation-only dat `validation_ready`: 2329 clip, 13232.40 giay, CUDA/Quadro P1000 4096 MiB.
- App-managed runtime copy compile dat va khong sua runtime goc.
- GPT command preview da tao trong `voices/0001/model/avs0149_thu_minh_train_20260717_061215/reports/gpt_command_preview.json`.
- Command GPT stage chua san sang chay vi config copy thieu cac key bat buoc cua `s1_train.py`: `output_dir`, `train_semantic_path`, `train_phoneme_path`, `half_weights_save_dir`, `exp_name`.
- Chua Train that.
- Chua Generate.

---

## Cap nhat AVS-014.10 Bootstrap + Local API Foundation

- Da tach kien truc ba lop: Bootstrap Launcher, Main App va Local API.
- Bootstrap Launcher khong import PySide6, co the chay tren may thieu dependency UI va dua ra huong dan First-Run Setup bang tieng Viet.
- RuntimeEnvironmentManager phat hien Python app, dependency du an, FFmpeg/FFprobe, NVIDIA/GPU va Runtime Profile GPT-SoVITS hien co.
- FeatureReadinessService tao trang thai available/degraded/blocked cho cac tinh nang de Main App co the mo che do gioi han thay vi crash.
- Settings co nhom API & Tich hop de bat/tat Local API, xem host/port/token, sao chep URL/token va tao token moi.
- Local API MVP dung Python stdlib HTTP server, mac dinh `127.0.0.1`, yeu cau token cho moi endpoint tru `/api/v1/health`.
- Local API cung cap health, capabilities, readiness, voice catalog, variant catalog va generation job contract.
- Generation job API tao job/state/log/temp/output rieng trong `workspace/api_jobs/`, khong Generate that neu Voice chua ready.
- Voice Catalog API khong leak duong dan runtime/model/checkpoint/pretrained.
- Da them tai lieu `docs/BOOTSTRAP_FIRST_RUN.md`, `docs/LOCAL_API_V1.md` va vi du client `examples/video_app_client.py`.
- Chua Train that.
- Chua Generate that.

## Blocker AVS-014.10

- Python hien tai van thieu `PySide6` va `pytest`, nen UI smoke/pytest bang interpreter nay bi chan neu chua cai dependency.
- OpenAPI tu dong chua co trong MVP vi Local API hien dung stdlib; neu can OpenAPI runtime that thi can chot them dependency FastAPI/Uvicorn o sprint sau.

---

## Cap nhat AVS-014.11 Voice DNA Foundation + UI Layout Redesign

- Da them foundation cho Reading Style Profile / Voice DNA, tach rieng khoi Speaker Profile va Voice model.
- Style Profile co ID rieng dang `style_000001`, co the tai su dung cho nhieu Voice.
- Da them schema, repository, service, integrity check, extraction placeholder va export/import `.avstyle`.
- `.avstyle` mac dinh chi export du lieu phan tich, khong gom MP3 goc, dataset, model, checkpoint, token hoac absolute path.
- VoiceConfig duoc mo rong migration-safe voi `reading_style`; Variant duoc bo sung `style_profile_id`, `style_mode`, `style_strength`.
- FeatureReadinessService co trang thai style_profile_* cho UI/API.
- Local API bo sung endpoint Style Profile va voice style profile.
- Generate request chap nhan style fields nhung validation se bao ro engine hien chua ap dung Style Profile that, khong silently ignore.
- UI co trang `Phong cach doc / Voice DNA` va section `Du lieu tham chieu giong doc` trong Settings.
- Da them tai lieu Voice DNA, data format, backup/restore va UI design system.

## Blocker AVS-014.11

- Chua co prosody analyzer that nen Style Profile extraction van o trang thai pending/blocked, khong danh dau ready gia.
- Generate engine chua ap dung Style Profile vao audio that.
- Python hien tai van thieu `PySide6` va `pytest`, nen UI smoke/pytest bang interpreter nay van bi chan neu chua cai dependency.

---

## Cap nhat AVS-014.12 Training Workflow Clarification

- AVS-014.12 da tach ro ba loai du lieu: Training Dataset, Reading Style Profile / Voice DNA va Speaker Reference.
- TrainingPage co scroll foundation va ba reference mode loai tru nhau:
  - dung Style Profile co san;
  - tao draft Style Profile tu audio + text;
  - chi dung audio tham chieu de clone chat giong.
- TrainingPage khong con goi train that truc tiep; nut Train that bi khoa va yeu cau validation gate/xac nhan nguoi dung.
- VoiceConfig duoc mo rong migration-safe voi `speaker_reference` va `training_reference`, van giu `reference_audio` va `reference_text` cu.
- Them TrainingReferenceConfig, SpeakerReference, TrainingReferenceService, TrainingReferenceResolver, ReferenceAudioValidationService va AudioTextPairService.
- Voice rename va Style Profile rename co validation; ID khong doi.
- FeatureReadinessService co cac feature moi cho training reference, speaker reference, rename va scroll/responsive.
- Chua Train that.
- Chua Generate that.
- Chua tao Voice DNA gia; extraction van blocked/degraded khi chua co analyzer that.

## Task tiep theo

- UI smoke thu cong tren cac kich thuoc nho neu can tinh chinh them layout.
- Khi co analyzer that moi nang Style Profile extraction tu blocked/degraded sang ready.

---

## Cap nhat AVS-014.13 Project & Workspace Manager

- AVS-014.13 da them nen Project & Workspace Manager o muc model/service/UI/API.
- Project moi uu tien folder ID-based dang `project_000001`, nhung Project legacy folder theo ten van load duoc.
- ProjectConfig duoc mo rong migration-safe voi display_name, metadata lifecycle, archive_state, workspace/project root, favorite, health va active IDs.
- Rename Project chi doi display_name, khong rename folder, khong doi Project ID.
- ProjectService co facade cho create, open, close, switch, recent, rename, duplicate, archive, restore archive, export/import, backup/restore, validation va repair an toan.
- Project Registry luu metadata tim kiem/recent/missing/archive, khong chua toan bo du lieu Project.
- ProjectPage duoc chuyen thanh Project Manager foundation, khong expose delete vinh vien.
- Local API bo sung read-only endpoints Project/Workspace.
- Chua Train that.
- Chua Generate that.
- Khong sua GPT-SoVITS runtime.

## Ghi chu AVS-014.13

- Delete vinh vien Project bi khoa trong Sprint nay.
- Export/Import hien o muc package nhe co manifest va chan path traversal; full package/copy file lon can user confirm o sprint sau.
- Project repair hien chi lam cac sua an toan nhu tao lai folder thieu, co backup truoc repair.

---

## Cap nhat AVS-014.13.1 Reference Data Vault & Persistence Hardening

- Da them Reference Vault foundation de luu managed copy cho audio/text/manifest/report bang stable asset ID.
- ReferenceAsset, ReferenceRegistry va ReferenceVaultService ho tro checksum sha256, atomic import, deduplication theo checksum/asset_type/extension, verify va relink co checksum warning.
- AudioTextPairService giu API cu va co them persistent pair manifest khi bat `persist_manifest=True`.
- SpeakerReference, VoiceConfig va TrainingReferenceConfig duoc mo rong migration-safe voi audio_asset_id, text_asset_id, manifest_id va segment asset IDs.
- TrainingReferenceResolver uu tien resolve bang asset ID neu co, fallback legacy path/text de giu tuong thich.
- Project backup/export/import co hook reference_vault: metadata backup khac complete backup; standard export co the gom managed reference.
- Project validation co the kiem tra Reference Registry, managed path, missing asset va checksum mismatch khi duoc truyen reference_vault.
- Style Profile co source_assets de giu draft source asset IDs ma khong tao Voice DNA gia.
- Chua Train that.
- Chua Generate that.
- Chua chay analyzer that.

## Ghi chu AVS-014.13.1

- File goc ben ngoai app chi la provenance/fallback, khong phai ban luu ben vung duy nhat.
- Managed copy trong Reference Vault moi la ban app quan ly lau dai.
- Worktree van dirty vi du lieu that trong projects/workspace; khong restore/clean/stage/commit/push.

---

## Cap nhat AVS-014.14 Job & Queue System

- AVS-014.14 da them ha tang Job & Queue dung chung cho tac vu dai.
- Job co ID bat bien dang `job_000001`, display name tach khoi identity.
- Job model ho tro scope, owner IDs, payload/result JSON-safe, progress, ETA, retry, dependency, lease, heartbeat va recovery_state.
- Job state machine co cac trang thai created, queued, waiting_dependency, running, pause_requested, paused, resume_requested, cancel_requested, cancelling, retry_wait, completed, failed, cancelled, interrupted va blocked.
- JobRepository luu persistent JSON theo `workspace/jobs/jobs/<job_id>/job.json`, atomic write va quarantine record hong.
- JobQueueService ho tro enqueue/dequeue/list, priority, idempotency_key, dependency waiting/blocked, pause/resume/cancel request.
- JobRunner chay mac dinh mot job tai mot thoi diem, worker cooperative pause/cancel, retry va shutdown mark interrupted.
- Worker contract gom execute, request_pause, request_resume, request_cancel, report_progress, write_log, heartbeat, checkpoint va cleanup.
- Handler an toan da co: demo_progress, reference_verify, project_validate va project_backup adapter co guard test scope.
- Queue UI moi nam trong trang `Cong viec / Hang doi`, Dashboard co summary job, Local API co endpoint read-only `/api/v1/jobs`, `/api/v1/queue`, `/api/v1/jobs/{job_id}` va `/api/v1/jobs/{job_id}/logs`.
- FeatureReadinessService co cac feature job_model, job_repository, persistent_queue, job_runner, progress/ETA/log, pause/resume/cancel/retry, priority, dependency, recovery, queue_ui va dashboard_job_summary.
- Khong Train that, khong Generate that, khong chay analyzer that, khong sua GPT-SoVITS runtime.

## Ghi chu AVS-014.14

- Queue Generate cu tren AudioPage duoc giu tuong thich; Job system moi chay song song de adapter workflow dan dan.
- Worktree van dirty do du lieu that trong projects/workspace; khong restore/clean/stage/commit/push.

---

## Cap nhat AVS-014.15 Intelligent Resource Manager

- AVS-014.15 da them nen Resource Manager dung chung cho Job Queue va cac pipeline AI sau nay.
- Resource model gom HardwareProfile, ResourceSnapshot, ResourceRequirement, ResourceDecision, ResourcePolicy va ResourceLease.
- Hardware detection chi doc thong tin an toan: CPU thread, RAM, FFmpeg/FFprobe, NVIDIA GPU/VRAM qua `nvidia-smi`; khong quet process list, khong stress CPU/GPU/RAM/VRAM.
- Resource snapshot co TTL ngan, gom CPU/RAM/Disk/GPU/VRAM va pressure_state.
- Resource policy tap trung: max_concurrent_jobs, max_gpu_jobs, reserve RAM/VRAM/Disk, TTL lease va nguong pressure.
- JobModel da co resource_requirement, resource_decision, resource_lease_id, selected_gpu_device_id, resource_wait_reason va resource_pressure_state.
- Job state machine co `waiting_resource`.
- JobQueueService danh gia Resource truoc khi chay, cap lease khi ready, dua job vao `waiting_resource` neu chua du tai nguyen va khong chan cac job khac.
- JobRunner giai phong lease khi completed/failed/cancelled/interrupted/paused va khi shutdown.
- Resource Monitor UI moi hien hardware/snapshot/policy/leases/waiting jobs.
- JobsPage hien job dang cho tai nguyen; Dashboard co Resource pressure card; Settings hien policy hien hanh.
- Local API co endpoint read-only `/api/v1/resources`, `/api/v1/resources/hardware`, `/api/v1/resources/snapshot`, `/api/v1/resources/policy`, `/api/v1/resources/leases`, `/api/v1/resources/waiting-jobs`.
- FeatureReadinessService da co cac feature resource_*.
- Khong Train that, khong Generate that, khong chay analyzer that, khong sua GPT-SoVITS runtime.

## Ghi chu AVS-014.15

- Resource Manager hien moi dieu phoi mot process app local; chua co distributed scheduler.
- Auto pause khi pressure critical dang mac dinh tat.
- Worktree van dirty do du lieu that trong projects/workspace; khong restore/clean/stage/commit/push.

---

## Cap nhat AVS-014.16 Generate Pipeline Foundation

- AVS-014.16 da them nen Generate Pipeline o muc domain/service/persistence/API/job.
- Generate foundation tao duoc Request, Session, Source Snapshot, Document, Chapter, Unit, Attempt, Plan, Manifest va Registry.
- Source TXT/DOCX/pasted text chi duoc doc; snapshot/normalized text duoc ghi vao session folder, khong sua file goc.
- GenerateRepository ghi JSON atomic va registry co the list session theo project.
- GenerateSessionService co validation, create_session, no-loss reconstruction verifier, request checksum/materialized_at, frozen plan guard, get plan/manifest, inspect_resume/execute_resume va inspect_retry/retry_unit/retry_chapter.
- Manifest co planned artifact records; artifact lifecycle foundation co registry, reservation, temp-to-final promotion va basic WAV validation.
- Job Queue co worker `generate_prepare` voi ResourceRequirement CPU-light, khong dung GPU va khong chay inference.
- Local API co foundation endpoints:
  - `/api/v1/generate/readiness`
  - `/api/v1/generate/requests/validate`
  - `/api/v1/generate/sessions`
  - `/api/v1/generate/sessions/{session_id}`
  - `/api/v1/generate/sessions/{session_id}/plan`
  - `/api/v1/generate/sessions/{session_id}/manifest`
  - `/api/v1/generate/sessions/{session_id}/resume`
  - `/api/v1/generate/sessions/{session_id}/units/{unit_id}/retry`
- Feature readiness co trang thai tach bach: planning/source/normalization/splitter/frozen plan/manifest/artifact lifecycle/recovery/API READY; preview audio, production execution va WAV/MP3 output UNAVAILABLE; full audio validation DEGRADED.
- Local API co them routes cho chapters, units pagination, attempts, artifacts, resume/retry action, recovery inspect va manifest rebuild.
- AudioPage co Generate Foundation controls toi thieu: Validate Request, Tao Plan, Resume Inspect, Retry Inspect va execution disabled khi production handler unavailable.
- Chua Generate that, chua Train, chua goi GPT-SoVITS runtime, chua tao audio gia.

## Blocker/Ghi chu AVS-014.16

- Generate inference that van can Voice model/reference/runtime hop le va sprint rieng de noi adapter.
- Generate UI Session/Plan detail rieng chua polish; UI foundation toi thieu da co tren trang Tao Audio.
- Resume/retry production execution van UNAVAILABLE khi khong co handler/provider that; test-only provider chi dung trong tests.
- Full audio validation bang ffprobe/codec policy va production MP3 output van thuoc sprint sau.
- Worktree van dirty do du lieu that trong projects/workspace va cac thay doi sprint truoc; khong clean/restore/commit/push.

---

## Cap nhat AVS-014.16A Foundation Cleanup & Consistency

- AVS-014.16A la sprint on dinh hoa foundation, khong phai sprint tinh nang moi.
- Pham vi: cleanup source/docs/tests, dong bo capability truth status va giu Generate production execution UNAVAILABLE.
- Khong Train that.
- Khong Generate that.
- Khong tich hop GPT-SoVITS runtime trong sprint nay.
- `docs/PROJECT_STATUS.md` duoc khoi tao de phan anh trang thai source hien tai va Capability Table trung thuc.

## Task tiep theo sau AVS-014.16A

- Chi bat dau AVS-014.17 GPT-SoVITS Runtime Integration sau khi compileall, targeted pytest, full pytest, bootstrap, UI smoke, API smoke va git diff --check dat.
