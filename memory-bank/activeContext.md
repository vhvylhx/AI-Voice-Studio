# Active Context — AI Voice Studio

## Thời điểm ghi nhận

Nguồn xác minh: `CURRENT_SPRINT.md` hiện tại.

## Trạng thái kỹ thuật quan trọng

### GPT-SoVITS Voice `0001` Training

- Dataset trainable đã được xác minh: 2329 clip, 13232.40 giây, language `vi`, WAV unique, không duplicate/missing và transcript không rỗng.
- Runtime Profile `gpt_sovits_v2pro_default` nhận diện được runtime GPT-SoVITS v2Pro, Python, torch CUDA, GPU Quadro P1000, scripts và pretrained files.
- Preprocessing/Training thực vẫn `BLOCKED`.
- Blocker chính: runtime GPT-SoVITS hiện tại không hỗ trợ Vietnamese cleaner/phoneme frontend/inference language contract cho `vi`.
- Không được map giả `vi` sang `zh`, `en`, `auto`, `all_zh`, `yue` hoặc language khác.
- Không được chạy preprocessing để tạo artifact rỗng/sai, smoke train hay checkpoint giả khi `PREPROCESS_CONFIG_INVALID` còn tồn tại.
- `GPTSoVITSAdapter.train()` chưa có implementation production.

### VieNeu-TTS Vietnamese Engine

- Candidate được khóa trong controlled-import plan: `vieneu==3.2.3`, model `pnnbao-ump/VieNeu-TTS-v3-Turbo`, revision `75ff82a`, license Apache-2.0 theo evidence đã ghi nhận.
- Isolated CPU runtime có CPU-only torch frontend; policy cấm GPU/CUDA fallback.
- Model và codec đã được resolve vào managed cache; offline resolution đã được kiểm tra.
- CPU canary đã tạo 3 WAV hợp lệ 48 kHz mono pcm_s16le.
- Manual listening review đang `PENDING_USER_REVIEW`.
- Vietnamese production integration, Generate execution và WAV output production vẫn `BLOCKED`.
- Chưa bind VieNeu vào Voice production và chưa có Real Smoke qua full app pipeline.

## Hướng tiếp theo đã nêu trong source

- Người dùng cần nghe/chấm `reference_audio.wav` và các output canary VieNeu trước khi thiết kế production integration.
- Với GPT-SoVITS training tiếng Việt, chỉ tiếp tục preprocessing/smoke train sau khi có runtime hoặc upstream patch hỗ trợ Vietnamese frontend hợp lệ, đã validate.