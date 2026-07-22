# Generate Pipeline Foundation

Sprint: AVS-014.16

## Muc tieu

Tao nen Generate Pipeline co the mo rong cho UI, Local API va Job Queue truoc khi chay Generate that.

Foundation nay khong goi GPT-SoVITS, khong synthesize audio va khong tao WAV/MP3 gia.

## Thanh phan

- `GenerateRequestRecord`: yeu cau generate da validate.
- `GenerateSessionRecord`: session persistent cho mot lan generate.
- `GenerateSourceSnapshot`: snapshot text nguon, checksum va provenance.
- `GenerateDocumentRecord`: tai lieu da normalize.
- `GenerateChapterRecord`: cau truc chuong.
- `GenerateUnitRecord`: don vi text train/generate sau nay.
- `GenerateAttemptRecord`: attempt state cho tung unit.
- `GeneratePlanRecord`: plan gom chapter/unit/attempt.
- `GenerateManifestRecord`: manifest artifact, planned artifact records va output spec.
- `GenerateArtifactRecord`: planned/reserved/valid artifact, lineage, reservation va validation co ban cho WAV.
- `GenerateRegistryEntry`: index session de UI/API list nhanh.
- `GenerateSettings`: cau hinh splitter/output/temp policy tap trung.

## Storage

Mac dinh repository nam o:

`workspace/generate/`

Moi session nam o:

`workspace/generate/sessions/<session_id>/`

File chinh:

- `session.json`
- `request.json`
- `document.json`
- `plan.json`
- `manifest.json`
- `source/source_snapshot.txt`
- `source/normalized.txt`
- `artifacts/`: planned unit WAV sau nay.
- `temp/`: temp output/unit path sau nay.
- `artifacts.json`: artifact lifecycle registry cua session.
- `reservations/`: output reservation theo artifact.

Registry:

`workspace/generate/registry.json`

Tat ca JSON duoc ghi atomic bang file `.tmp` roi replace.

## Text source

Ho tro:

- pasted text
- TXT
- DOCX

Quy tac:

- Khong sua file goc.
- Chi doc file goc.
- Snapshot va normalized text nam trong session folder.
- DOCX can `python-docx`; neu thieu thi bao loi ro.
- Unit giu `separator_after` de reconstruct normalized text khong mat title/intro/outro.
- Plan chi frozen khi reconstruction verifier pass.

## Frozen Plan

- Plan co `frozen`, `freeze_version`, `frozen_at`, `immutable_checksum_sha256` va `plan_checksum_sha256`.
- Semantic mutation sau freeze bi tu choi khi save plan.
- Unit runtime status/attempt state duoc phep cap nhat ma khong lam doi immutable checksum.
- Resume/retry khong chay lai normalizer, structure detector hoac splitter.

## Artifact lifecycle

- Artifact ID bat bien.
- Artifact co lineage: Project, Session, Plan ID/checksum, Unit, Attempt, format, role va input fingerprint.
- Output path validation chan traversal, Windows reserved names, case collision, path length va Unicode non-NFC.
- Output reservation dung reservation ID va file reservation de tranh nhieu writer.
- Temp output khong duoc xem la valid artifact.
- Promotion temp -> final recheck collision, validate WAV co ban roi moi danh dau `valid`.
- Existing valid output khong bi overwrite silent.
- Invalid/superseded/temp/orphan file khong tu xoa trong foundation.

## Attempt / Resume / Retry

- Unit la planned work.
- Attempt la mot lan thuc hien, attempt number do service cap.
- Job la ha tang execution.
- Unit khong co hai active attempt.
- Attempt success chi sau khi artifact validation pass.
- Resume/retry execution trong production tra `UNAVAILABLE` neu chua co provider/handler that.
- Test-only provider chi dung trong tests de chung minh orchestration qua artifact validation.

## Job Queue

Job type:

`generate_prepare`

Worker:

`GeneratePrepareJobWorker`

ResourceRequirement:

- CPU-light.
- RAM thap.
- Khong GPU.
- Khong goi engine.

Ket qua job:

- `session_id`
- `manifest`
- `status = ready`

Khong co audio output that trong sprint nay.

## Local API

Endpoint foundation:

- `GET /api/v1/generate/readiness`
- `POST /api/v1/generate/requests/validate`
- `GET /api/v1/generate/sessions`
- `POST /api/v1/generate/sessions`
- `GET /api/v1/generate/sessions/{session_id}`
- `GET /api/v1/generate/sessions/{session_id}/plan`
- `GET /api/v1/generate/sessions/{session_id}/chapters`
- `GET /api/v1/generate/sessions/{session_id}/units`
- `GET /api/v1/generate/sessions/{session_id}/attempts`
- `GET /api/v1/generate/sessions/{session_id}/artifacts`
- `GET /api/v1/generate/sessions/{session_id}/manifest`
- `GET /api/v1/generate/sessions/{session_id}/resume`
- `POST /api/v1/generate/sessions/{session_id}/resume`
- `GET /api/v1/generate/sessions/{session_id}/units/{unit_id}/retry`
- `POST /api/v1/generate/sessions/{session_id}/units/{unit_id}/retry`
- `POST /api/v1/generate/sessions/{session_id}/chapters/{chapter_id}/retry`
- `GET /api/v1/generate/recovery`
- `POST /api/v1/generate/sessions/{session_id}/manifest/rebuild`

API foundation khong expose runtime/model/checkpoint path.

Readiness tra dung trang thai:

- Planning/session/source/manifest: `READY`.
- Reconstruction/frozen plan/artifact lifecycle/recovery/API foundation: `READY`.
- Preview audio, resume execution, retry execution, WAV output, MP3 output: `UNAVAILABLE`.
- Full audio validation: `DEGRADED`.
- Basic WAV validation: `READY`.

## Migration

Khong can migration bat buoc cho du lieu cu.

Generate pipeline cu van ton tai. Foundation moi chay song song va chi tao data moi khi nguoi dung/API/job tao session.

## Gioi han

- Chua Generate that.
- Chua Train.
- Chua analyzer/context AI moi.
- Chua merge/chuyen doi audio that qua foundation endpoint.
- Chua danh dau completed neu khong co audio that.
- UI Generate co foundation box toi thieu tren trang Tao Audio; session detail polish van thuoc sprint UI sau.
- Chua co production execution worker de tao unit audio that.
- Resume/retry execution production tra UNAVAILABLE khi khong co handler/provider that.
- Path privacy cua API khong tra `original_path` va artifact path absolute; mot so session ID/path ref noi bo van la reference an toan.

## Capability truth

| Hang muc | Trang thai | Ghi chu |
| --- | --- | --- |
| Request/Session model | READY | Co revision, checksum, materialized_at va persistent session. |
| Source snapshot | READY | Pasted/TXT/DOCX duoc snapshot; file goc khong bi sua. |
| Text normalization/plan | READY | Co reconstruction verifier, checksum va separator policy. |
| Frozen plan | READY | Co immutable checksum va guard semantic mutation sau freeze. |
| Manifest | READY | Co unit count, source/output va planned artifact records. |
| Basic WAV artifact validation | READY | Dung Python `wave` de validate doc duoc, mono va sample rate hop le. |
| Artifact repository/output lifecycle | READY | Co artifact registry, reservation, temp-to-final promote va validation gate. |
| Generate prepare job | READY | CPU-light, plan-only. |
| Real generate execution | UNAVAILABLE | Chua goi GPT-SoVITS/engine synthesize. |
| Resume/retry inspection | READY | Doc state va tra kha nang inspect. |
| Resume/retry execution foundation | READY | Co orchestration va test-only provider; production handler van UNAVAILABLE. |
| Recovery foundation | READY | Co startup light scan, manifest rebuild va temp classification; khong load engine. |
| Local API foundation | READY | Co route cho sessions, plan, units, attempts, artifacts, resume/retry/recovery. |
| Generate foundation UI | DEGRADED | Co controls toi thieu tren AudioPage; chua polish session detail rieng. |

---

## AVS-014.17 Runtime Integration Delta

AVS-014.17 giu nguyen foundation contract va bo sung production path co gate:

- `RuntimeProfileService.validate(..., require_generate=True)` dong vai tro Runtime Doctor cho Generate.
- `GET /api/v1/generate/runtime/doctor` tra trang thai runtime/profile/script/pretrained/FFmpeg/FFprobe.
- `GenerateUnitJobWorker` la worker production cho mot unit, co ResourceRequirement GPU va khong CPU fallback mac dinh.
- `GPTSoVITSGenerateProvider` resolve request/plan/unit/voice, validate Voice model va goi EngineManager -> GPTSoVITS Engine/Adapter.
- `POST /api/v1/generate/sessions/{session_id}/units/{unit_id}/execute` chi enqueue job khi Runtime Doctor san sang.
- Provider/engine loi se mark Attempt/Unit/Artifact `failed`; khong de ket `running` hoac `reserved`.
- `inference_cli.py` la script Generate CLI bat buoc. `inference_webui.py` duoc report rieng va khong duoc gia dinh la CLI tuong duong.

Capability truth sau delta:

| Hang muc | Trang thai | Ghi chu |
| --- | --- | --- |
| Runtime Doctor Generate | READY | Co service/API report; status cu the phu thuoc profile hien tai. |
| Generate unit production worker | READY | Worker/job/resource/provider path da co. |
| Real GPT-SoVITS execution | DEGRADED | Chi chay khi Runtime Doctor va Voice model hop le; chua smoke runtime that trong validation mac dinh. |
| WAV output qua foundation | DEGRADED | Co temp/reservation/WAV validation/promotion; chua nang READY neu chua co real smoke. |
| MP3 output qua foundation | UNAVAILABLE | Chua noi trong AVS-014.17. |
