# Training, Dataset và Model Integrity — AI Voice Studio

## Dữ liệu nguồn và workspace

- TXT, DOCX, transcript, audio reference và dataset gốc là dữ liệu nguồn bất biến; không sửa, chuẩn hóa ghi đè, đổi tên, di chuyển hoặc xóa trực tiếp.
- Mọi bước detect, split, resample, alignment, lọc, transcript derivation hoặc feature extraction phải tạo bản sao/cache có lineage rõ ràng trong workspace/cache được quản lý.
- Không dùng thư mục production hoặc dataset thật của người dùng làm nơi thử nghiệm; tests và smoke test phải dùng temporary directory hoặc fixture riêng.
- Không dùng filename/display name làm identity dataset item, speaker, reference hoặc training run nếu contract đã có immutable ID.
- Không tự loại quảng cáo, tiêu đề chương, intro hoặc outro khi chưa có lựa chọn rõ ràng từ người dùng theo workflow hiện có.

## Validation gate và provenance

- Training/preprocessing chỉ bắt đầu khi toàn bộ validation gate được contract yêu cầu đã pass, gồm input integrity, transcript, language compatibility, runtime profile, asset/pretrained requirement và resource preflight.
- Kết quả validation phải giữ evidence và blocker có thể hành động; không chuyển blocker thành cảnh báo để tiếp tục workflow.
- Không coi số lượng clip, thời lượng, file tồn tại, cache có feature hoặc một command exit code 0 là bằng chứng Training `READY` hay model hợp lệ.
- Mọi dataset manifest, config, model/checkpoint và report phải mang lineage tới immutable source/training run phù hợp; không sửa trực tiếp manifest để mô phỏng state pass.
- Không tự repair, merge, deduplicate, promote hoặc xóa sample suspicious/orphan ngoài recovery policy hiện có.

## Runtime, language và training execution

- GPT-SoVITS Vietnamese preprocessing/training phải giữ `BLOCKED` khi runtime chưa có Vietnamese cleaner/phoneme frontend/inference contract hợp lệ cho `vi`.
- Không fake-map `vi` sang language token khác và không sử dụng token khác để vượt validation gate.
- Khi `PREPROCESS_CONFIG_INVALID`, runtime/asset thiếu hoặc resource policy không đạt, không chạy preprocessing, smoke train, checkpoint generation hay artifact creation.
- Runtime discovery, pretrained asset có mặt hoặc test fake thành công không đủ để nâng Training production thành `READY`.
- Không tự fallback CPU/GPU, runtime profile, engine hoặc model base nếu request và policy hiện có không cho phép rõ ràng.

## Checkpoint, publish và readiness

- Không tạo checkpoint, model, embedding, config hay artifact giả để biểu diễn Training thành công.
- Train chỉ được báo thành công khi output thực đã qua validation bắt buộc, persistence/lineage hoàn tất và các gate readiness production liên quan đã pass.
- Publish model phải thông qua Service/Repository/validation workflow hiện có; không ghi trực tiếp vào Voice/Variant hay model registry để ép capability.
- Variant, Style và speed không phải model/checkpoint mới; không dùng chúng để suy diễn một model training khác.
- Fake trainer, test checkpoint, mock runtime và canary output chỉ thuộc test composition hoặc controlled evaluation, không được nâng production readiness.