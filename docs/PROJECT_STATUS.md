# AI Voice Studio - Project Status

Ngay cap nhat: 2026-07-22

## AVS-016 Sprint 8 Round01 Deep Review Integration

- Sprint vua cap nhat: AVS-016 Sprint 8 Round01 Deep Review Integration & Round02 Preparation.
- Evidence bat buoc da dung: `review_inputs/avs016_round01/AVS_Round01_Deep_Review.xlsx`, `AVS_Round01_review_sheet_filled.csv`, `AVS_Round01_Analysis_Report.md`.
- `pair_002` Round01 bi BLOCK do transcript/reference mismatch: reference `000070_005_002` dai 5.8 giay nhung transcript 233 ky tu / 49 syllables, 40.17 chars/s va 8.45 syllables/s.
- Da tao adjusted Top20/Holdout tai `cache/avs016_sprint8_reference_selection_voice_0001/`, loai `000070_005_002` va thay bang Top50 candidate hop le `000015_022_001`.
- Da them preflight integrity cho preview/reference: chars/s, syllables/s va preview/reference duration ratio fail-closed BLOCK/REVIEW.
- Da normalize transcript o preview-input layer, giu provenance source text trong pair manifest; affected normalize/regenerate: `pair_005`, `pair_010`, `pair_012`, `pair_017` va replacement `pair_002`.
- Reference Selection Engine flag/penalize boundary-fragment/ellipsis de uu tien cau hoan chinh cho holdout/preview review.
- Round02 READY tai `cache/avs016_sprint6_preview_generation_voice_0001/Round02/`: 20 Pair / 40 WAV, 10 WAV regenerated cho 5 pair affected, 30 WAV carry-forward co audit.
- Khong Train, khong LoRA, khong Runtime Binding, khong Production Inference; ranking/review signal khong phai human approval cho Training.

### Capability Table Addendum

| Capability | Status | Ghi chu |
|---|---|---|
| AVS-016 Sprint 8 Review Integration | READY | Round01 deep review da duoc tich hop thanh adjusted Top20/Holdout va Round02 diagnostic artifact. |
| Pair preflight integrity | READY | chars/s, syllables/s va preview/reference duration ratio co BLOCK/REVIEW fail-closed. |
| Transcript normalization provenance | READY | Normalize preview-input layer va giu source text/source checksum trong pair manifest. |
| Round02 diagnostic previews | READY | 20 Pair / 40 WAV READY; chi 5 affected pair duoc regenerate. |
| Production Preview binding/inference | BLOCKED | Sprint 8 khong bind Generate/Engine/Runtime production va khong nang readiness production. |

## Trang thai hien tai

- Sprint vua cap nhat: AVS-016 Sprint 4 Reference Selection Engine foundation.
- AVS-016 Sprint 4 them `ReferenceSelectionService`: scan toan bo `metadata.list` lam authority, loc alignment/dataset-health evidence, quality ranking, AVS-014.24 calibration-aware weighting, Top50 va diversified frozen Top20.
- AVS-016 Sprint 4 khong bind Production Generate/Engine/Runtime, khong thay doi inference algorithm, training, fine-tune, preprocessing, scoring, blind review hoac production readiness.
- AVS-016 Sprint 4 ghi `reference_selection_manifest.json` va `evaluation_holdout_manifest.json`; frozen Top20 va evaluation holdout dat `exclude_from_future_training=true`.
- Sprint vua cap nhat truoc do: AVS-016 Sprint 3 Voice Preview Generation foundation; real diagnostic generation 40 preview van BLOCKED do chua co benchmark manifest da freeze voi dung 20 Pair da duoc phe duyet.
- Sprint truoc do nua: AVS-014.24 Sprint C5 Production Binding Foundation.
- AVS-014.24 da them `ProductionReferenceBindingService` lam binding gate fail-closed: chi resolve winner khi Reference Selection, Generalization va Production Readiness deu `READY`; winner/artifact khong nhat quan, consumer bypass hoac readiness chua READY deu bi tu choi.
- C5 chi them binding foundation; chua bind consumer Generate/Engine/Runtime, khong chay inference va khong thay doi readiness Generate/WAV/MP3 production.
- AVS-014.24 hoan thien diagnostic manual-review artifact: review chi complete khi `review_completed=true`, `review_status=REVIEW_COMPLETED`, co dung mot winner hop le va co metadata `reviewer`, `review_date`, `notes`; loader fail-closed bang `ReferenceSelectionPendingError` neu review pending/invalid.
- Nen Generate Pipeline AVS-014.16 da co o muc request/session/source snapshot/plan/manifest/recovery/API/job prepare.
- Da co production handler/worker cho Generate Unit qua GPT-SoVITS, nhung execution readiness duoc tach 3 lop: Environment, Selected Voice/Variant/Reference assets va Real Inference verification.
- Da co Voice Publish Automation foundation de link training artifacts/reference vao Voice theo `voice_id`, co validation/fingerprint va yeu cau explicit confirmation.
- Chua Train GPT-SoVITS that trong AVS-014.19A.
- Preprocessing artifact foundation da co, nhung artifact that cho Voice 0001 dang BLOCKED tai language support gate cua runtime upstream.
- AVS-014.19A1 da audit sau runtime language/text frontend va ket luan current GPT-SoVITS v2Pro runtime khong ho tro Vietnamese frontend hop le; khong chay canary de tranh artifact/readiness gia.
- AVS-014.20 da them Language Catalog, Voice Engine Binding theo language, heuristic Language Detection, Engine Capability Router va API/UI foundation cho per-language readiness.
- Tieng Viet duoc uu tien engine rieng va khong fallback sang GPT-SoVITS. Cac language zh/en/ja/ko/yue co mapping GPT-SoVITS foundation nhung chua READY khi chua co trained assets va Real Smoke PASS.
- AVS-014.21 da hoan thien Voice language checkbox UI, Generate language mode foundation va static evaluation cho VieNeu-TTS/F5-TTS Vietnamese/viXTTS.
- VieNeu-TTS la Vietnamese primary candidate de xuat, nhung chua production-ready tren may nay vi chua co local model, chua user-approved download va chua local canary/Real Smoke PASS.
- AVS-014.22 da them controlled import/canary foundation cho VieNeu-TTS, validate reference Thu Minh Voice 0001 va tao diagnostics report BLOCKED khi gate chua du an toan.
- AVS-014.22 correction da chot contract moi: CPU/ONNX inference duoc ho tro voi CPU-only `torch`/`torchaudio` frontend rieng cho fresh reference enrollment; GPU/CUDA van bi cam trong canary.
- Isolated VieNeu runtime da duoc tao tai `cache/engines/vieneu_tts/75ff82a/runtime/.venv/` voi `torch==2.8.0+cpu`, `torchaudio==2.8.0+cpu`, `onnxruntime==1.27.0`, `vieneu==3.2.3`; CPU policy PASS (`torch.cuda.is_available()==False`, khong co `CUDAExecutionProvider`).
- SSL gate da fix an toan bang `truststore==0.10.4` trong isolated runtime, khong tat certificate verification va khong sua Windows global certificate store.
- Model `pnnbao-ump/VieNeu-TTS-v3-Turbo` revision `75ff82a72f54d55ed389e1eeb12041d3c4bac7d4` da verify license `apache-2.0`, tai 11 required VieNeu files va promote atomically vao managed cache.
- Codec dependency `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX` revision `ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae` da verify license `apache-2.0`, tai/promote atomically vao managed codec cache va validate ONNX CPU load.
- Safe CPU canary da PASS voi 3 WAV trong diagnostics run `vieneu_cpu_canary_20260719_012122`; manual listening review dang PENDING_USER_REVIEW; production Generate van BLOCKED.
- AVS-014.23 da audit lai GPT-SoVITS Train readiness cho Voice `0001`: dataset metadata trainable PASS voi 2329 clip / 13232.40 giay, runtime/hardware baseline PASS o muc audit, nhung preprocessing/train van BLOCKED vi runtime GPT-SoVITS v2Pro hien tai khong ho tro language `vi` trong text/phoneme frontend.
- Preprocessing readiness plan moi: `cache/training/voice_0001/gpt_sovits/avs01423_voice_0001_training_readiness_20260719_021009/preprocessing/preprocessing_manifest.json`, status `blocked`, code `PREPROCESS_CONFIG_INVALID`.
- Training validation-only moi: `cache/train_validation/avs01423_validation_only_0001/train_report.json`, status `validation_failed`, code `preprocessing_not_ready`.
- Chua chay Generate Audio that trong nghiem thu mac dinh neu Runtime/Voice chua duoc xac nhan.

## Capability Table

| Capability | Status | Ghi chu |
|---|---|---|
| App bootstrap | READY | Bootstrap co the kiem tra moi truong va chuyen vao main app khi dependency san sang. |
| Main Window / UI shell | READY | UI desktop PySide6 da co shell va cac page chinh. |
| Project / Workspace foundation | READY | Project ID bat bien, workspace/project manager foundation da co. |
| Voice schema / Voice ID | READY | Voice ID bat bien, rename khong doi ID. |
| Voice multi-engine language binding | READY | VoiceConfig co enabled_languages, language_selection_mode va engine_bindings migration-safe theo language; legacy single-engine field van duoc giu. |
| Voice display rename safety | READY | Rename moi chi doi `display_name` theo `voice_id`, khong rename folder/model/checkpoint/reference/project ID. |
| Voice publish automation | READY | Service/API validate va publish existing checkpoint/reference vao Voice khi co confirm; khong Train/Generate va khong fake READY. |
| Dataset scan/health/repair/review | READY | Chay tren cache/output job, khong sua file goc. |
| Alignment quality-first | READY | Faster-Whisper/timestamp pipeline da co contract va metadata valid. |
| Training validation_only | READY | Kiem tra dataset/runtime/model path truoc train; chua train that. |
| GPT-SoVITS preprocessing foundation | READY | Co Preprocessing Run/Plan/Stage, run-owned cache, manifest, artifact validators va TrainingService manifest gate. |
| Vietnamese text frontend compatibility | BLOCKED | Runtime hien tai khong co cleaner/phoneme/inference language contract cho `vi`; khong fake map sang language khac. |
| Vietnamese engine static evaluation | READY | Da co scorecard/audit cho VieNeu-TTS, F5-TTS Vietnamese va viXTTS; khong tai model va khong Generate. |
| VieNeu controlled import/canary gate | DEGRADED | Contract/source gate READY, isolated CPU runtime READY, VieNeu model/codec READY va technical canary PASS; manual review va production integration chua xong nen production van BLOCKED. |
| Reference Selection manual-review artifact | READY | Diagnostic/manual-review utility validate exactly one available winner, completed state va reviewer metadata; khong phai production Voice binding hay inference readiness. |
| Production Reference Binding Foundation | READY | Service fail-closed chi tra winner da phe duyet khi Selection, Generalization va Production Readiness deu READY; chua co consumer production duoc bind va khong nang readiness inference. |
| Reference Selection Engine | READY | Metadata.list authority scan, evidence filtering, quality ranking, calibration-aware weighting, Top50 va diversified frozen Top20 da co service/test. |
| Evaluation holdout manifest | READY | evaluation_holdout_manifest.json ghi holdout_count, freeze_rank va exclude_from_future_training=true; khong dua holdout vao future training. |
| Vietnamese engine production integration | BLOCKED | VieNeu-TTS la primary candidate de xuat, nhung chua co local model/canary/Real Smoke PASS nen chua production READY. |
| GPT-SoVITS multilingual routing | BLOCKED | Catalog/router da map zh/en/ja/ko/yue sang GPT-SoVITS language mode, nhung can trained assets va Real Smoke PASS theo language truoc khi READY. |
| GPT-SoVITS preprocessing artifacts real | BLOCKED | Dataset 2329 clip pass, nhung upstream prepare text/phoneme khong ho tro language `vi`; chua tao 4 artifact train that. |
| Real GPT-SoVITS Train | BLOCKED | Dataset 2329 clip pass, runtime/hardware audit pass, nhung preprocessing artifacts cho `vi` BLOCKED va adapter train production chua implement. |
| Generate planning foundation | READY | Request, snapshot, normalized text, plan, manifest va registry da co. |
| Generate language routing foundation | READY | Generate Unit co route snapshot per language/engine/fingerprint/blockers; khong goi engine that trong sprint nay. |
| Generate resume/retry inspection | READY | Inspect duoc state; execution production phu thuoc Runtime Doctor/Voice model. |
| Generate production execution | BLOCKED | Environment runtime READY, nhung Voice Thu Minh 0001 hien thieu gpt_model, sovits_model, reference_audio va reference_text; chua co Real Smoke PASS voi fingerprint hien tai. |
| WAV production output qua Generate foundation | BLOCKED | Chi READY khi Real GPT-SoVITS Smoke tao WAV that qua production pipeline va smoke report khop fingerprint hien tai. |
| MP3 production output qua Generate foundation | UNAVAILABLE | MP3 output qua foundation chua duoc noi trong AVS-014.17. |
| Full audio validation policy | DEGRADED | Da co basic WAV validation; ffprobe/codec policy day du thuoc sprint sau. |
| Same Preview benchmark diagnostic | BLOCKED | Isolated generator/validation/manifest foundation da co; can frozen 20-Pair input truoc real generation. |
| New Preview benchmark diagnostic | BLOCKED | Isolated generator/validation/manifest foundation da co; can frozen 20-Pair input truoc real generation. |
| Preview validation benchmark | READY | Validate parse, PCM16, mono, sample rate runtime, duration duong va non-silence. |
| Preview round versioning | READY | Tao Round01, Round02, ... va tu choi overwrite output/manifest. |
| Preview benchmark manifest update | READY | Ghi path, SHA-256, duration, timestamp, runtime profile va status sau WAV validation. |
| Local API foundation | READY | API localhost stdlib co readiness/catalog/job/generate foundation endpoints. |
| API real Generate | UNAVAILABLE | API khong generate that neu chua co Voice/runtime/model ready va handler production. |
| Job Queue foundation | READY | Persistent job/queue/worker foundation da co. |
| Resource Manager foundation | READY | Hardware snapshot/resource decision/lease foundation da co. |
| Style Profile / Voice DNA foundation | DEGRADED | Quan ly/import/export va post-training Style Profile schema co; prosody analyzer va generate-applied style that chua co. |
| Post-training Variant/Style binding | DEGRADED | Variant co the bind Style Profile nhu generate profile; khong tao model rieng va chua ap dung prosody that vao audio. |
| Runtime GPT-SoVITS integration cho Generate | DEGRADED | Environment Doctor READY cho runtime v2Pro, nhung khong duoc coi la Generate Execution READY neu chua co Selected Assets READY va Real Inference PASS. |

## Runtime Doctor AVS-014.17B

- Environment readiness: READY voi Runtime Profile `gpt_sovits_v2pro_default`, Python runtime, torch/CUDA, GPT-SoVITS scripts, pretrained models, FFmpeg va FFprobe.
- Selected Voice/Variant/Reference asset readiness: BLOCKED. Voice Thu Minh `0001` ton tai va co Variant `default`, nhung thieu `gpt_model`, `sovits_model`, `reference_audio` va `reference_text`.
- Real inference verification: BLOCKED/SKIPPED. Chua co explicit enable va chua co smoke report PASS khop fingerprint hien tai.
- Real Smoke attempt AVS-014.17B: BLOCKED tai asset gate, khong chay inference vi 4 asset bat buoc cua Voice Thu Minh `0001` dang trong.
- False-positive prevention: `generate_execution` va `wav_output` khong duoc READY chi vi environment/root/script/model file ton tai.
- Fingerprint/stale smoke: real smoke report phai khop fingerprint hien tai va output WAV phai ton tai, doc duoc, mono, 32000 Hz, sample width 16-bit.

## AVS-014.18 Voice Publish Automation

- VoiceConfig co `display_name` migration-safe; legacy folder `voices/Thu Minh/` tiep tuc load theo `voice_id=0001`.
- Luong rename moi dung `VoiceService.rename_display_name(voice_id, new_display_name)` va khong doi folder path.
- VoicePublishService chi link existing `gpt_model`, `sovits_model`, `reference_audio`, `reference_text`, language va runtime profile vao Voice khi nguoi dung confirm.
- Publish fingerprint khong phu thuoc `display_name`, nen doi ten Voice khong lam stale smoke neu asset/runtime khong doi.
- StyleProfile schema duoc mo rong cho post-training style profile: intended use, classification, parameters, prompt instructions, reference requirements, compatibility, readiness, blockers va warnings.
- Variant binding voi Style Profile chi la generate profile/style metadata; khong chua checkpoint/dataset/weight rieng.
- Generate production execution van BLOCKED/DEGRADED cho den khi selected assets ready va Real GPT-SoVITS Smoke PASS voi fingerprint hien tai.

## Data safety

- Source khong duoc tu y sua/xoa/di chuyen du lieu that trong `projects/`, `workspace/`, `voices/`, `outputs/`, `backups/`, `exports/` hoac Reference Vault.
- Tests phai dung fixture/cache tam rieng, khong dung du lieu that cua nguoi dung.
- Worktree co the dirty do du lieu/project that; khong restore/clean neu nguoi dung chua xac nhan.

## Blocker / chua trien khai

- Chua chay real GPT-SoVITS Generate smoke test trong luot nay vi Selected Assets cua Voice 0001 chua du va chua co explicit enable.
- AVS-014.19 Real Train dang TRAINING_BLOCKED: dataset metadata pass, runtime/hardware pass, nhung thieu artifact GPT-SoVITS train preprocessing (`2-name2text.txt`, `3-bert`, `4-cnhubert`, `6-name2semantic.tsv`) va chua co production Training Job Worker/Frozen Training Plan/Resource lifecycle cho real s1/s2 train.
- AVS-014.19A Preprocessing Pipeline foundation da co, nhung Real Preprocessing dang BLOCKED tai runtime language gate: `1-get-text.py`/cleaner upstream ho tro en/ja/jp/ko/yue/zh, khong ho tro metadata language `vi`.
- AVS-014.19A1 Runtime Language Audit ket luan VI_UNSUPPORTED_BY_CURRENT_RUNTIME: khong co Vietnamese cleaner, phoneme frontend, BERT/word2ph contract va inference language `vi` trong runtime hien tai.
- Chua co MP3 output production trong Generate foundation.
- Chua co full audio validation policy bang ffprobe/codec cho artifact production.
- Chua chay Train GPT-SoVITS production.
- Chua co prosody analyzer that cho Voice DNA.
- Chua co Vietnamese engine production duoc nguoi dung chon/cau hinh.
- Chua co per-language trained asset/smoke PASS cho GPT-SoVITS zh/en/ja/ko/yue.

## AVS-014.20 Multi-Engine Language Foundation

- Language Catalog chuan hoa cac language: `vi`, `zh`, `en`, `ja`, `ko`, `yue`.
- GPT-SoVITS mapping foundation: `zh -> all_zh`, `en -> en`, `ja -> all_ja`, `ko -> all_ko`, `yue -> all_yue`.
- `vi` khong map sang GPT-SoVITS trong foundation nay; `vi` can Vietnamese-capable engine rieng.
- VoiceConfig them `default_language`, `preferred_language`, `language_selection_mode`, `enabled_languages` va `engine_bindings`.
- Voice cu migration mac dinh `enabled_languages=["vi"]` va binding `vi` o trang thai `blocked_unconfigured_engine`.
- EngineCapabilityRouter tra readiness rieng tung language va fingerprint tach theo `voice_id + language_code + engine/runtime/model/reference`.
- LanguageDetectionService hien la heuristic foundation, ho tro mixed-language planning o muc sentence/segment va explicit override co warning mismatch.
- Local API co foundation endpoints cho language catalog, detection, language plan, enabled language selection va voice language capabilities.
- UI Voice Detail hien enabled language foundation; UI hoan chinh cho checkbox/router polish thuoc sprint sau.

## AVS-014.21 Vietnamese Engine Evaluation & Language Selection

- Voice Detail UI hien checkbox that cho `Tat ca`, `Tieng Viet`, `Tieng Trung`, `Tieng Anh`, `Tieng Nhat`, `Tieng Han`, `Tieng Quang Dong`.
- Tooltip `Tat ca`: "Cho phep Voice doc tat ca ngon ngu da cau hinh. Tuy chon nay khong tu dich noi dung."
- Trang Voice luu language selection theo `voice_id`; legacy Voice mac dinh `vi`; khong cho luu empty selection.
- Generate Options foundation co mode auto detect, fixed language va multilingual route preview; fixed mode chi hien language da enable.
- Engine evaluation records phan biet `CLAIMED_BY_UPSTREAM`, `VERIFIED_LOCALLY`, `NOT_VERIFIED`, `UNSUPPORTED`; sprint nay khong co `VERIFIED_LOCALLY` vi khong download/canary.
- License gate tach source/model/dataset/commercial/attribution/redistribution.
- VieNeu-TTS: primary candidate de xuat cho Vietnamese engine, uu tien tiep tuc bang download/import plan va local canary sau khi nguoi dung xac nhan.
- F5-TTS Vietnamese: khong chon lam production default vi public checkpoint license non-commercial/NC.
- viXTTS: chi comparison; license/model usage can review rieng va khong production default trong sprint nay.
- Download Plans duoc tao nhung `requires_user_permission=true`; Local Canary = SKIPPED neu chua co local model/license/runtime/disk gate.
- Readiness production khong thay doi: Generate execution/WAV output van BLOCKED khi chua co selected assets va Real Smoke PASS.

## AVS-014.22 VieNeu-TTS Controlled Import & Vietnamese Local Canary Gate

- Candidate hien tai: `vieneu==3.2.3`, model `pnnbao-ump/VieNeu-TTS-v3-Turbo`, revision `75ff82a`, license Apache-2.0 theo upstream evidence.
- Managed import target: `cache/engines/vieneu_tts/<revision>/`.
- Diagnostics target: `diagnostics/vietnamese_engine_evaluation/<canary_run_id>/`.
- Reference Thu Minh Voice 0001 candidate da validate voi ffprobe: 6.50s, mono, pcm_s16le, 32000 Hz, transcript `vi` khong rong.
- Canary report da tao: `diagnostics/vietnamese_engine_evaluation/vieneu_canary_20260719_001423/vieneu_canary_report.json`.
- Source contract status: `CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND`.
- Isolated CPU runtime: READY tai `cache/engines/vieneu_tts/75ff82a/runtime/.venv/`; `runtime_manifest.json` fingerprint `0ced4dc470609f434fb86c732e1c86d7064111739a89b97fb4c2dc0f2baa5b29`.
- CPU-only dependency check: PASS (`torch==2.8.0+cpu`, `torchaudio==2.8.0+cpu`, `onnxruntime==1.27.0`, ONNX providers `AzureExecutionProvider`, `CPUExecutionProvider`, CUDA false).
- SSL root cause: certifi bundle trong isolated runtime khong verify duoc TLS chain tren may nay; `truststore` official Windows trust bridge verify HTTPS PASS ma khong disable SSL.
- Model cache: `cache/engines/vieneu_tts/75ff82a/models/pnnbao-ump__VieNeu-TTS-v3-Turbo__75ff82a72f54d55ed389e1eeb12041d3c4bac7d4`.
- Model manifest fingerprint: `77e59508e5c13b654e7eed5138c5bb1f21c99a50a109c933689048352435b26b`.
- Codec cache: `cache/engines/vieneu_tts/75ff82a/codecs/OpenMOSS-Team__MOSS-Audio-Tokenizer-Nano-ONNX__ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae`.
- Safe CPU canary: PASS tai `diagnostics/vietnamese_engine_evaluation/vieneu_cpu_canary_20260719_012122/`, tao `output_01.wav`, `output_02.wav`, `output_03.wav` bang CPU_ONNX va reference frontend CPU_TORCH.
- Manual review: `PENDING_USER_REVIEW`.
- Previous blocked report: `diagnostics/vietnamese_engine_evaluation/vieneu_cpu_canary_20260719_005351/evaluation_report.json`.
- Requirement thay the blocker cu: `cpu_torch_frontend_required_for_fresh_reference_enrollment`.
- Production readiness khong thay doi: Vietnamese engine production integration, Generate execution va WAV output van BLOCKED.

## AVS-014.23 GPT-SoVITS Voice 0001 Training Readiness

- Voice `0001` duoc resolve qua `VoiceService.find_by_id()`; folder legacy `voices/Thu Minh/` khong duoc dung lam identity.
- Dataset source duoc chon tu metadata final da validate: `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`.
- Dataset gate PASS: 2329 rows, 2329 unique WAV, 0 duplicate, 0 missing, 0 empty transcript, language distribution `vi: 2329`, speaker distribution `Thu Minh: 2329`, duration min/median/max `2.0 / 5.62 / 9.98` giay.
- Runtime gate audit PASS o muc environment: Python 3.9.13, torch 2.0.0+cu118, CUDA true, GPU Quadro P1000 compute capability 6.1, driver 551.86.
- Machine resource baseline: available RAM khoang 16.29 GB, disk F free khoang 109.43 GB, GPU free VRAM khoang 4004 MiB, khong co GPU compute process.
- Power status khong doc duoc qua WMI trong luot audit, nen ghi warning thay vi PASS.
- Upstream source audit: `prepare_datasets/1-get-text.py` chi map `zh`, `ja/jp`, `en`, `ko`, `yue`; `text/cleaner.py` khong co Vietnamese cleaner va language khong ho tro se fallback sai sang `en` voi text trong.
- Preprocessing plan AVS-014.23 bi BLOCKED voi `PREPROCESS_CONFIG_INVALID`; khong chay stage preprocess that.
- `TrainingService.prepare_train(validation_only=True)` bi BLOCKED dung cach voi `preprocessing_not_ready`; khong goi `s1_train.py` hoac `s2_train.py`.
- Smoke Train, checkpoint validation va canary generation chua chay vi preflight khong PASS.

Status: GPT_SOVITS_TRAINING_READINESS_BLOCKED; FULL_TRAINING_BLOCKED_PENDING_USER_APPROVAL.

## Sprint tiep theo du kien

- Nguoi dung nghe manual package `diagnostics/vietnamese_engine_evaluation/vieneu_cpu_canary_20260719_012122/` va cham diem/confirm co tiep tuc production integration VieNeu hay khong.
- Publish/cau hinh trained assets per language cho GPT-SoVITS neu muon dung zh/en/ja/ko/yue.
- Sau khi co engine/assets that, chay Real Smoke theo language truoc khi nang Generate readiness.



























































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































## AVS-016 Sprint 5 Production Reference Selection Execution

- Sprint vua cap nhat: AVS-016 Sprint 5 Production Reference Selection Execution.
- Production run da chay `ReferenceSelectionService` tren Voice `0001` voi authority `cache/avs0145_full_dataset_thu_minh/alignment/metadata.list`.
- Evidence da load: alignment manifest/report, dataset report, transcript/quality evidence trong metadata/alignment va calibration-aware weighting AVS-014.24.
- Output run: `cache/avs016_sprint5_reference_selection_voice_0001/reference_selection_manifest.json`, `evaluation_holdout_manifest.json`, `selection_report.json`.
- Statistics: scanned 2329, accepted 2329, rejected 0, Top50 50, frozen Top20 20.
- Diversity Top20: 20 source MP3, 20 chapter.
- Calibration summary: `applied=true`, evidence source `AVS-014.24 calibration-aware weighting from current repository contract`.
- Holdout/frozen selected clips: tat ca 20/20 co `exclude_from_future_training=true`.
- Capability update: Production Reference Selection Execution = READY o muc cache/report artifact; Production Reference binding/inference consumer, Generate Preview, 40 WAV, Train, LoRA/fine-tune va Runtime inference binding khong thay doi.

### Capability Table Addendum

| Capability | Status | Ghi chu |
|---|---|---|
| Production Reference Selection Execution | READY | Da chay tren Voice `0001` production metadata 2329 clip va sinh frozen Top20/holdout/report trong cache Sprint 5. |
| Frozen Top20 Reference Selection | READY | 20 selected clips co `freeze_status=frozen` va `exclude_from_future_training=true`. |
| Reference Selection Report | READY | `selection_report.json` co accepted/rejected stats, diversity, score, duration va calibration summary. |
| Evaluation holdout manifest Sprint 5 | READY | `evaluation_holdout_manifest.json` co 20 item va tat ca `exclude_from_future_training=true`. |
| Production Reference binding/inference consumer | BLOCKED | Sprint 5 khong bind Generate/Engine/Runtime consumer va khong chay inference production. |
## AVS-016 Sprint 6 Preview Generation

- Sprint vua cap nhat: AVS-016 Sprint 6 Preview Generation.
- Da dung Frozen Top20 cua Sprint 5 tu `cache/avs016_sprint5_reference_selection_voice_0001/reference_selection_manifest.json` lam input bat bien.
- Output Round: `cache/avs016_sprint6_preview_generation_voice_0001/Round01/`.
- Da sinh dung 20 AI Preview va 20 Benchmark Preview WAV; moi Top20 co dung 1 cap preview.
- Manifest lien ket day du `reference`, `transcript`, `ai_preview`, `benchmark_preview` va `preview_id` trong tung `pair_manifest.json`.
- `preview_report.json` trang thai `READY`, pair_count 20, preview_count 40, ai_preview_count 20, benchmark_preview_count 20, transcript identity PASS.
- WAV policy PASS: mono, PCM16, 48000 Hz, duration duong, non-silent va output checksum khong trung reference audio checksum.
- Khong sua Frozen Top20, khong Train, khong LoRA, khong Runtime Binding va khong Production Inference.
- Production Generate/Preview readiness khong thay doi; artifact nay la diagnostic isolated generation bang VieNeu CPU/ONNX runtime.

### Capability Table Addendum

| Capability | Status | Ghi chu |
|---|---|---|
| AVS-016 Sprint 6 Preview Generation Artifacts | READY | Round01 co 20 Pair/40 WAV va `preview_report.json` READY. |
| AI Preview diagnostic WAV | READY | 20 WAV synthesized moi tu Top20 reference qua isolated VieNeu CPU/ONNX runtime. |
| Benchmark Preview diagnostic WAV | READY | 20 WAV synthesized moi voi cung transcript de doi chieu. |
| Transcript identity AI vs Benchmark | READY | Tat ca Pair co cung `transcript_sha256` cho AI Preview va Benchmark Preview. |
| Production Preview binding/inference | BLOCKED | Sprint 6 khong bind Generate/Engine/Runtime production va khong nang readiness production. |
