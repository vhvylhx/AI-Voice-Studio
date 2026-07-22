# Current Sprint
## Cap nhat AVS-016 Sprint 8 Round01 Deep Review Integration

- Da tich hop evidence bat buoc tu `review_inputs/avs016_round01/AVS_Round01_Deep_Review.xlsx`, `AVS_Round01_review_sheet_filled.csv` va `AVS_Round01_Analysis_Report.md`.
- Root cause `pair_002`: reference `000070_005_002` dai 5.8 giay nhung transcript 233 ky tu / 49 syllables, tuong duong 40.17 chars/s va 8.45 syllables/s, vuot preflight plausibility va bi BLOCK.
- Da tao manifest Sprint 8 moi tai `cache/avs016_sprint8_reference_selection_voice_0001/`, loai `000070_005_002` khoi Top20/Holdout va thay bang Top50 candidate ke tiep hop le `000015_022_001`.
- Da normalize transcript o preview-input layer va giu source text/provenance trong pair manifest cho cac pair affected.
- Da flag/penalize transcript boundary-fragment/ellipsis de uu tien cau hoan chinh cho holdout/preview review.
- Round02 tai `cache/avs016_sprint6_preview_generation_voice_0001/Round02/` READY: 20 Pair / 40 WAV; regenerate 10 WAV cua `pair_002`, `pair_005`, `pair_010`, `pair_012`, `pair_017`; 30 WAV con lai carry-forward tu Round01 co audit.
- Khong Train, khong LoRA, khong Runtime Binding va khong Production Inference. Ranking/review signal khong phai phe duyet Training.

## Blocker/Ghi chu AVS-016 Sprint 8

- Round02 la diagnostic/manual-review artifact bang VieNeu isolated CPU/ONNX runtime, khong nang Production Generate/Preview readiness.
- Cac pair borderline/low priority trong workbook van can human listening review truoc moi quyet dinh training hoac binding.
## Cap nhat AVS-016 Sprint 4 Reference Selection Engine

- Da xac minh implementation hien co trong `src/services/reference_selection_service.py` va regression tests trong `tests/test_reference_selection_service.py`.
- Reference Selection Engine scan toan bo `metadata.list` lam authority, khong dung candidate cache lam authority.
- Engine doc evidence tu alignment manifest/report va dataset-health de loai duplicate, suspicious, invalid, AI-generated, music-heavy va multiple-speakers.
- Quality ranking dung audio metrics, transcript quality, pitch distribution va AVS-014.24 calibration-aware weighting.
- Ket qua co Top50 ranking va diversified Top20 theo source/chapter coverage.
- Frozen Top20 duoc gan `freeze_status=frozen` va `exclude_from_future_training=true`.
- Output ghi `reference_selection_manifest.json` va `evaluation_holdout_manifest.json`.
- Sprint nay khong bind Production Generate/Engine/Runtime, khong chay inference production va khong thay doi production readiness.

## Blocker/Ghi chu AVS-016 Sprint 4

- Reference Selection Engine foundation READY o muc service/test.
- Production Reference binding/inference thuc te van phu thuoc cac gate AVS-014.24 va consumer production sprint sau.
## Cap nhat AVS-016 Sprint 3 Voice Preview Generation

- Da mo rong `VoicePreviewBenchmarkService` cho isolated diagnostic preview generation: moi Pair hop le tao `same_preview_v1.wav` va `new_preview_v1.wav` trong Round moi, bang callable runtime duoc truyen explicit; service khong goi Production Generate/Engine binding.
- Output Round dung versioning `Round01`, `Round02`, ...; khong ghi de Round, preview WAV hoac manifest da ton tai.
- Service validate moi preview bang WAV parser: file phai doc duoc, PCM16, mono, dung sample rate runtime, co duration duong va khong toan im lang.
- Manifest luu preview path, SHA-256, duration, generation timestamp, runtime profile va generation status; evidence chi duoc ghi sau khi WAV pass validation.
- Regression test PASS: 20 test bao phu tao 20 same/new preview, versioning, no-overwrite, manifest update va WAV validation, voi temporary directory.
- Khong co training, fine-tune, preprocessing, thay doi inference algorithm, production binding, scoring, similarity metric, blind review hoac UI review.
- Chua chay real Round: diagnostic calibration hien co chi trỏ metadata/dataset cache, khong co benchmark manifest da freeze gom dung 20 reference pair duoc phe duyet va benchmark transcript. Service fail-closed, khong tu suy doan Pair hoac dung du lieu nguon lam input.

## Blocker AVS-016 Sprint 3

- `BENCHMARK_INPUT_NOT_FROZEN`: can manifest benchmark 20 Pair da duoc phe duyet, co immutable pair/reference identity, duong dan reference hop le va transcript benchmark da freeze truoc khi chay 40 VieNeu diagnostic inference that.
- ROADMAP hien ghi Voice Preview la AVS-015, trong khi task goi AVS-016 Sprint 3; khong tu y doi ma Sprint/roadmap lich su.

## Cap nhat AVS-014.24 Sprint C5 Production Binding Foundation

- Da them `ProductionReferenceBindingService` lam diem vao duy nhat de consumer production resolve winner reference da duoc phe duyet.
- Binding fail-closed: chi tra `ProductionReferenceWinnerBinding` khi Reference Selection, Generalization va Production Readiness deu `READY`.
- Service tu choi artifact khong nhat quan, winner khong hop le, readiness chua `READY`, consumer khong dang ky hoac consumer co direct-artifact access; khong fallback, default winner, hard-code hay automatic replacement.
- Khong co consumer Generate/Engine/Runtime production nao duoc bind trong C5; hanh vi generation production hien tai khong thay doi.
- Da them regression tests cho ba readiness gate, artifact consistency, winner validation va consumer-bypass validation.

## Cap nhat AVS-014.24 Sprint C2.5 Reference Selection Manual Review Workflow

- Da hoan thien diagnostic review artifact cho Reference Selection; review chi `COMPLETE` khi `review_completed=true`, `review_status=REVIEW_COMPLETED` va co dung mot `winner_reference_variant` hop le.
- Artifact luu metadata review `reviewer`, `review_date` va `notes`.
- Validation fail khi winner khong ton tai, khong thuoc `available_reference_variants`, winner null khi review complete, status/completed khong dong bo, hoac co nhieu winner.
- Loader chi tra winner tu review hop le; moi artifact pending/invalid deu fail-closed bang `ReferenceSelectionPendingError`.
- Da them regression tests cho literal completed status, metadata bat buoc va cac invalid winner state.
- Khong co production binding, inference production, training, fine-tune, audio artifact, commit hay push trong task nay.

## Trang thai AVS-014.24

- Manual Reference Selection review artifact: READY cho diagnostic/manual-review workflow.
- Production Reference Binding Foundation: READY o muc service gate fail-closed; chua bind consumer Generate/Engine/Runtime va khong nang readiness inference.
- Production Voice binding thuc te, Generate execution, WAV/MP3 output va training: khong thay doi; van giu capability/blocker hien co.

## Cap nhat AVS-014.23 GPT-SoVITS Voice 0001 Training Readiness

- Da audit lai GPT-SoVITS training readiness cho Voice `0001` theo source hien tai, khong dua vao so lieu hoi thoai.
- Dataset trainable hien tai duoc xac minh tu `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`: 2329 clip, 13232.40 giay, 2329 WAV unique, language `vi`, speaker `Thu Minh`, khong duplicate, khong missing, transcript khong rong.
- Runtime Profile `gpt_sovits_v2pro_default` van detect duoc GPT-SoVITS v2Pro, Python runtime, torch CUDA, GPU Quadro P1000, scripts va pretrained files.
- Machine safety baseline nhe dat cho audit: RAM kha dung tren 10 GB, disk F con khoang 109 GB, GPU co 4004 MiB free va khong co GPU compute process.
- Power status qua WMI khong tra du lieu; ghi warning, khong gia vo PASS.
- Da tao preprocessing readiness plan moi tai `cache/training/voice_0001/gpt_sovits/avs01423_voice_0001_training_readiness_20260719_021009/preprocessing/preprocessing_manifest.json`.
- Plan bi BLOCKED dung cach voi `PREPROCESS_CONFIG_INVALID`: runtime preprocessing hien tai khong ho tro language `vi`; supported languages doc tu source/runtime la `en`, `ja`, `jp`, `ko`, `yue`, `zh`.
- Training validation-only moi ghi report tai `cache/train_validation/avs01423_validation_only_0001/train_report.json` va fail dung cach voi `preprocessing_not_ready`.
- Khong chay preprocessing stage, khong chay SoVITS/GPT smoke train, khong tao checkpoint smoke va khong tao canary bang checkpoint smoke.

## Blocker AVS-014.23

- `VI_UNSUPPORTED_BY_CURRENT_GPT_SOVITS_RUNTIME`: upstream GPT-SoVITS v2Pro hien tai khong co Vietnamese cleaner/phoneme frontend/inference language contract cho `vi`.
- `GPTSoVITSAdapter.train()` trong app van chua co implementation production; training lifecycle s1/s2 that chua san sang.
- Full Training van `BLOCKED_PENDING_USER_APPROVAL` va bi chan them boi preprocessing/frontend gate.

## Task tiep theo

- Nguoi dung can cung cap/chot mot runtime GPT-SoVITS co Vietnamese frontend hop le, hoac upstream patch co cleaner/phoneme/train preprocessing/inference language `vi` da duoc validate.
- Sau khi co runtime/patch hop le moi chay lai preprocessing artifact real PASS, roi moi tinh den smoke train.

## Cap nhat AVS-014.22 VieNeu Isolated CPU Runtime with CPU-Only Torch Frontend

- Da them contract/service cho VieNeu-TTS controlled import va local canary gate.
- Candidate duoc khoa o muc plan: `vieneu==3.2.3`, model `pnnbao-ump/VieNeu-TTS-v3-Turbo`, revision `75ff82a`, license Apache-2.0 theo upstream evidence.
- Target import duoc quan ly trong `cache/engines/vieneu_tts/<revision>/`; diagnostics nam trong `diagnostics/vietnamese_engine_evaluation/<run_id>/`.
- Reference Thu Minh Voice 0001 da validate: `cache/avs0145_full_dataset_thu_minh/alignment/clips/000135_028_001.wav`, duration 6.50s, mono, pcm_s16le, 32000 Hz, transcript `vi` khong rong.
- Service khong chay canary khi gate model/revision/license chua an toan.
- Source contract da sua thanh `CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND`: inference backend la ONNX CPU, fresh reference enrollment dung CPU-only `torch`/`torchaudio` frontend; GPU/CUDA khong duoc phep.
- Isolated runtime da tao tai `cache/engines/vieneu_tts/75ff82a/runtime/.venv/` va cai `torch==2.8.0+cpu`, `torchaudio==2.8.0+cpu`, `onnxruntime==1.27.0`, `vieneu==3.2.3`.
- CPU policy PASS: `torch.cuda.is_available()==False`, ONNX providers khong co `CUDAExecutionProvider`, khong dung GPU fallback.
- Runtime manifest da ghi tai `cache/engines/vieneu_tts/75ff82a/runtime/runtime_manifest.json`.
- SSL gate da fix an toan bang `truststore==0.10.4` trong isolated runtime; khong dung `verify=False`, khong `trusted-host`, khong sua Windows global certificate store.
- HTTPS read-only toi Hugging Face PASS qua truststore SSL context.
- Model `pnnbao-ump/VieNeu-TTS-v3-Turbo` da resolve full commit `75ff82a72f54d55ed389e1eeb12041d3c4bac7d4`, license `apache-2.0`, va tai/promote atomically 11 required VieNeu files vao managed cache.
- Model manifest: `cache/engines/vieneu_tts/75ff82a/models/pnnbao-ump__VieNeu-TTS-v3-Turbo__75ff82a72f54d55ed389e1eeb12041d3c4bac7d4/model_manifest.json`.
- Codec dependency `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX` da resolve commit `ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae`, license `apache-2.0`, tai/promote atomically vao managed codec cache va validate ONNX CPU load.
- Offline resolution test PASS voi local `checkpoint_path`, `onnx_dir`, `codec_dir`; monkeypatch network fetch de dam bao khong implicit Hugging Face download.
- Safe CPU canary PASS trong `diagnostics/vietnamese_engine_evaluation/vieneu_cpu_canary_20260719_012122/`, tao 3 WAV hop le 48 kHz mono pcm_s16le.
- Manual listening review dang `PENDING_USER_REVIEW`.
- Canary run `diagnostics/vietnamese_engine_evaluation/vieneu_cpu_canary_20260719_005351/evaluation_report.json` ghi BLOCKED, khong tao WAV.
- Production readiness khong thay doi: Vietnamese engine production integration, Generate execution va WAV output van BLOCKED.

## Blocker AVS-014.22

- Chua co manual listening decision cua nguoi dung.
- Chua bind VieNeu vao Voice production.
- Chua production Generate/Real Smoke qua full app pipeline.

## Task tiep theo

- Nguoi dung nghe `reference_audio.wav`, `output_01.wav`, `output_02.wav`, `output_03.wav` trong diagnostics run va cham diem manual review.
- Neu manual review dat, sprint sau moi thiet ke production integration/binding cho Vietnamese engine; Generate production van BLOCKED trong sprint nay.

## Cap nhat AVS-014.21 Vietnamese Engine Evaluation & Language Selection

- Da hoan thien Voice language selection UI cho 6 ngon ngu: `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- Checkbox `Tat ca` chi mo scope cac language da cau hinh; khong tu dich noi dung va khong unlock readiness.
- Voice cu migration mac dinh chi bat `vi`; khong cho luu enabled_languages rong.
- Generate UI co 3 che do language foundation: auto detect, fixed language va multilingual planning.
- Fixed language chi hien cac language Voice dang enable; route blocker van duoc hien neu language chua READY.
- Da them static evaluation service cho VieNeu-TTS, F5-TTS Vietnamese va viXTTS.
- VieNeu-TTS duoc de xuat lam Vietnamese primary candidate do license Apache-2.0 va huong CPU/GPU/low-resource ro hon.
- F5-TTS Vietnamese bi chan production default do checkpoint cong khai dang non-commercial/NC license.
- viXTTS chi giu de comparison; license/model usage can review rieng, khong chon lam production default trong sprint nay.
- Download plan chi la ke hoach; sprint nay khong tai model, khong chay canary, khong Generate/Train.
- Low-resource safety profile cho Quadro P1000 4 GB: 1 inference process, GPU concurrency 1, lazy load, batch size 1, no background benchmark.

## Blocker AVS-014.21

- Vietnamese Engine Production Integration chua READY vi chua co local model, chua co user-approved download va chua co local canary/Real Smoke.
- Language readiness cho `vi` van BLOCKED neu Voice chua bind Vietnamese engine/model/reference hop le.
- Generate production readiness khong thay doi trong sprint nay.

## Task tiep theo

- Neu nguoi dung dong y, tao download/import workflow cho VieNeu-TTS candidate va chay local canary rieng sau khi license/model/disk/runtime gate dat.
- Sau canary PASS moi cau hinh binding `vi` cho Voice va chay per-language Real Smoke.

## Cap nhat AVS-014.20 Multi-Engine Language Capability & Routing Foundation

- Da them foundation de mot Voice co the lien ket nhieu Engine Profile theo language, khong dung display name/folder name lam identity.
- Language Catalog hien co: `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- Tieng Viet la primary language va phai dung Vietnamese-capable engine rieng; khong fallback sang GPT-SoVITS.
- GPT-SoVITS chi duoc khai bao routing foundation cho `zh`, `en`, `ja`, `ko`, `yue` voi mapping language mode rieng.
- Voice cu migration mac dinh chi bat `vi`, engine binding `vi` o trang thai blocked/unconfigured.
- All checkbox behavior duoc xu ly o service: all = bat du 6 language; selected = chi cac language nguoi dung tick.
- Generate Plan co route snapshot theo Unit de Sprint sau goi dung engine theo language, nhung Sprint nay khong Generate that.
- API co endpoint foundation cho catalog/detection/language plan/enabled languages/language capabilities.

## Blocker AVS-014.20

- Vietnamese Engine: BLOCKED_PENDING_ENGINE_SELECTION.
- GPT-SoVITS Multilingual: BLOCKED_PENDING_TRAINED_ASSETS_AND_SMOKE.
- Real Generate: BLOCKED.

## Task tiep theo

- Chon/cau hinh Vietnamese-capable engine production cho `vi`.
- Sau khi co engine/assets that, chay per-language Real Smoke truoc khi nang readiness.

## Cap nhat AVS-014.19A1 Vietnamese Text Frontend Compatibility

- Da audit runtime GPT-SoVITS v2Pro that truoc khi code frontend tieng Viet.
- `prepare_datasets/1-get-text.py` chi map language train hop le ve `zh`, `ja`, `en`, `ko`, `yue`; metadata hien tai la `vi` nen bi bo qua truoc khi tao `2-name2text.txt`.
- `text/cleaner.py` chi co cleaner module cho `zh`, `ja`, `en`, `ko`, `yue`; khong co Vietnamese cleaner/phoneme frontend.
- GPT stage doc `2-name2text.txt` va convert phoneme token bang vocab runtime co san; runtime hien tai khong co token/frontend tieng Viet duoc validate.
- Inference UI/runtime cung expose language `all_zh`, `all_ja`, `all_ko`, `all_yue`, `en`, `auto`, `auto_yue`; khong co `vi`.
- Ket luan compatibility: current runtime khong ho tro Vietnamese frontend hop le. Khong duoc fake map `vi` sang `zh`, `en`, `auto`, `all_zh` hay `yue`.
- Khong build `VietnameseTextFrontend`, khong chay canary preprocessing va khong tao artifact train that.
- Preprocessing tiep tuc BLOCKED voi `PREPROCESS_CONFIG_INVALID` cho den khi co runtime/upstream frontend tieng Viet hop le hoac user cung cap patch/runtime da ho tro `vi`.

## Blocker AVS-014.19A1

- VI_UNSUPPORTED_BY_CURRENT_RUNTIME: GPT-SoVITS v2Pro hien tai khong co Vietnamese text cleaner/phoneme/BERT/inference language contract.
- Can mot trong cac huong sau truoc AVS-014.19B:
  - runtime GPT-SoVITS da support Vietnamese frontend chinh thuc;
  - upstream patch rieng co cleaner, phoneme token mapping, train preprocessing va inference language `vi` duoc test;
  - chon engine/branch khac da ho tro tieng Viet that.

## Cap nhat AVS-014.19A GPT-SoVITS Dataset Preprocessing Pipeline

- AVS-014.19A da them foundation cho preprocessing artifact truoc Real Train.
- Preprocessing Run khong dua theo display name; run_id dang `avs01419a_voice_<voice_id>_<timestamp>`.
- Frozen Preprocessing Plan khoa metadata checksum, runtime fingerprint, script/pretrained fingerprint, stage order, command/env va output root.
- Output preprocessing nam trong `cache/training_preprocessing/<preprocessing_run_id>/`, khong sua metadata/audio/text goc.
- Service validate metadata truoc khi chay: duplicate, path scope, ffprobe, mono, pcm_s16le, 32000 Hz, transcript va language.
- Runtime discovery doc dung script that: `1-get-text.py`, `2-get-hubert-wav32k.py`, `2-get-sv.py`, `3-get-semantic.py`.
- Artifact validator doc `2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`; ghi nhan artifact phu v2Pro `5-wav32k` va `7-sv_cn`.
- TrainingService co the doc `preprocessing_manifest_path` va chan Train neu manifest MISSING/BLOCKED/STALE.
- Real pre-flight Voice `0001` dat dataset gate: 2329 clip, 13232.40 giay, khong dataset error.
- Real preprocessing chua chay vi runtime GPT-SoVITS v2Pro hien tai khong ho tro language `vi` trong prepare text/cleaner upstream.

## Blocker AVS-014.19A

- `PREPROCESS_CONFIG_INVALID`: metadata language la `vi`, nhung runtime upstream chi detect duoc en/ja/jp/ko/yue/zh cho preprocessing text/phoneme.
- Khong duoc chay `1-get-text.py` voi `vi` vi se tao artifact rong hoac sai, dan toi readiness gia.
- Can runtime GPT-SoVITS/co cleaner tieng Viet hop le, hoac user chot mot huong mapping language chinh thuc truoc khi tao 4 artifact train that.

## Cap nhat AVS-014.18 Voice Publish Automation & Post-Training Style Variants

- AVS-014.18 hoan thien foundation de publish ket qua train co san vao Voice theo `voice_id`.
- VoiceConfig co `display_name` rieng voi folder name; legacy `voices/<Voice Name>/` tiep tuc load ma khong auto move.
- Rename chuan moi chi doi `display_name`, khong doi Voice ID, folder, model, checkpoint, reference, Project, Generate Session, Artifact hay train history.
- VoicePublishService validate/link existing GPT checkpoint `.ckpt`, SoVITS checkpoint `.pth`, reference audio/text, languages va Runtime Profile; yeu cau `confirm_publish=True` moi ghi voice.json.
- Publish fingerprint khong phu thuoc display_name.
- Style Profile schema da san sang cho post-training style/prompt/parameter profile; Variant binding khong tao model rieng va khong fake checkpoint.
- Local API co endpoint xem Voice theo `voice_id`, doi display name, validate/publish Voice assets va discover checkpoint candidates.
- Khong Train, khong Generate, khong Real Smoke trong sprint nay.
- Generate production readiness van phu thuoc Selected Assets va Real GPT-SoVITS Smoke PASS.

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

---

## Cap nhat AVS-014.17 GPT-SoVITS Runtime Integration for Generate

- Da them Runtime Doctor cho Generate dua tren Runtime Profile hien tai.
- Doctor kiem tra runtime root, Python, torch, faster-whisper, GPT-SoVITS scripts, pretrained models, FFmpeg va FFprobe.
- Da tach `inference_cli.py` va `inference_webui.py`; Generate production chi duoc coi la chay duoc khi CLI script ton tai that.
- Da them `GPTSoVITSGenerateProvider` de noi Generate Session/Unit voi EngineManager va GPT-SoVITS Engine/Adapter.
- Da them Job Queue worker `generate_unit` voi ResourceRequirement GPU, khong CPU fallback mac dinh.
- Da them API Runtime Doctor va endpoint enqueue Generate Unit.
- Generate artifact van di qua reservation -> temp -> validation -> final promotion; khong tao audio gia.
- Neu provider/engine loi, attempt/unit/artifact duoc mark failed de Retry/Resume khong ket state.
- Chua chay Generate that trong validation mac dinh.
- Chua Train that.

## Blocker/Ghi chu AVS-014.17

- Runtime/Voice production chi READY khi ca 3 lop deu dat: Environment readiness, Selected Voice/Variant/Reference asset readiness va Real Inference verification.
- AVS-014.17B da chan false-positive: Environment Doctor READY khong con tu dong lam `generate_execution` hoac `wav_output` READY.
- Runtime Doctor hien tra them fingerprint va stale smoke handling; smoke report chi duoc tinh PASS khi fingerprint khop va output WAV hop le.
- Kiem tra thuc te hien tai: Environment READY voi Runtime Profile `gpt_sovits_v2pro_default`; Selected Assets BLOCKED vi Voice Thu Minh `0001` thieu `gpt_model`, `sovits_model`, `reference_audio`, `reference_text`; Real Smoke BLOCKED/SKIPPED.
- Real Smoke end-to-end duoc yeu cau voi Voice Thu Minh `0001` / Variant `default`, nhung da dung o asset gate: 4 asset bat buoc dang trong nen khong tao Session/Job inference.
- MP3 production qua Generate foundation van chua noi.
- Can cap nhat Voice 0001 bang model/reference hop le va explicit enable real smoke truoc khi nang Generate Execution len READY.

---

## Cap nhat AVS-014.19 GPT-SoVITS Real Training Execution Audit

- Da audit Training Run `avs0149_thu_minh_train_20260717_061215`.
- Dataset metadata hien tai PASS o muc app gate: `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`, 2329 clip, 13232.40 giay, 2329 WAV unique, mono, pcm_s16le, 32000 Hz, language `vi`.
- Runtime Profile `gpt_sovits_v2pro_default` READY: Python runtime GPT-SoVITS, torch/CUDA, scripts train, pretrained GPT/SoVITS, FFmpeg/FFprobe deu ton tai.
- Hardware preflight nhe PASS: Quadro P1000 4 GB, CUDA available, runtime torch allocation nho OK, disk F con khoang 121 GB.
- Real Train KHONG duoc chay vi config/orchestration gate chua dat.
- `s1_train.py` runtime that yeu cau cac key: `output_dir`, `train_semantic_path`, `train_phoneme_path`, `train.half_weights_save_dir`, `train.exp_name`.
- Cache dataset hien tai chua co artifact train GPT-SoVITS bat buoc: `2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`.
- Source app hien moi co `TrainingService.prepare_train()` validation/smoke placeholder va `TrainingService.train()` legacy qua EngineManager; chua co production Training Job Worker/Frozen Training Plan/Resource lifecycle cho real s1/s2 train.
- Chua tao Training Run moi, chua tao checkpoint, chua sua runtime upstream, chua Generate, chua Publish.
- Training execution status: TRAINING_BLOCKED.

---

## Cap nhat AVS-016 Sprint 5 Production Reference Selection Execution

- Da chay `ReferenceSelectionService` tren dataset production Voice `0001` tu `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`.
- Input evidence da dung: `alignment_manifest.json`, `alignment_report.json`, `dataset/report.json` va calibration evidence AVS-014.24 theo contract hien tai.
- Da sua service de resolve duoc path metadata production dang luu dang `cache\\...` tu app root, va de diversity dung `source_audio` provenance thay vi chi gom theo folder clip cache.
- Da toi uu metric audio noi bo de selection production 2329 WAV chay xong trong mot command, khong doi public contract output.
- Output Sprint 5 ghi tai `cache/avs016_sprint5_reference_selection_voice_0001/`.
- Da tao frozen Top20, `evaluation_holdout_manifest.json` va `selection_report.json`.
- Tat ca 20 clip Top20 va 20 item holdout deu co `exclude_from_future_training=true`.
- Thong ke production run: scanned 2329, accepted 2329, rejected 0, Top50 50, frozen Top20 20.
- Diversity summary Top20: 20 source MP3, 20 chapter.
- Calibration summary: `applied=true`, evidence source `AVS-014.24 calibration-aware weighting from current repository contract`.
- Sprint nay khong Generate Preview, khong Generate 40 WAV, khong fine-tune, khong LoRA, khong Train, khong Runtime inference binding va khong Production voice generation.

## Blocker/Ghi chu AVS-016 Sprint 5

- Reference Selection production artifact READY cho Voice `0001` o muc cache/report.
- Production Reference binding/inference consumer chua thay doi; Generate production, Preview Audio, WAV/MP3 output va Train readiness giu nguyen theo blocker hien co.
## Cap nhat AVS-016 Sprint 6 Preview Generation

- Da dung Frozen Top20 cua Sprint 5 tai `cache/avs016_sprint5_reference_selection_voice_0001/reference_selection_manifest.json`.
- Da sinh Round preview that tai `cache/avs016_sprint6_preview_generation_voice_0001/Round01/`.
- Da sinh dung 40 WAV: 20 `ai_preview` va 20 `benchmark_preview`.
- Moi Pair co dung mot `preview_id`, reference, transcript, `ai_preview` va `benchmark_preview` trong pair manifest.
- Transcript giua AI Preview va Benchmark Preview duoc doi chieu bang cung `transcript_sha256` va artifact validation PASS.
- Preview WAV duoc validate mono, PCM16, 48000 Hz, duration duong va khong silent.
- Khong sua Frozen Top20, khong Train, khong LoRA, khong Runtime Binding va khong Production Inference.
- Output report: `cache/avs016_sprint6_preview_generation_voice_0001/Round01/preview_report.json`.

## Blocker/Ghi chu AVS-016 Sprint 6

- Preview generation nay la diagnostic artifact bang VieNeu isolated CPU/ONNX runtime, khong nang production Generate/Preview readiness.
- Manual listening review/cham diem chat luong van chua thuc hien.
