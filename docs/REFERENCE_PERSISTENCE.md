# Reference Persistence

Các workflow chọn, ghép, validate hoặc chuẩn hóa reference phải ưu tiên lưu vào Reference Vault.

## Audio/Text Pair

`AudioTextPairService` giữ API cũ và có thêm `persist_manifest=True`.

Manifest lưu:

- manifest_id
- pair_id
- audio_asset_id
- text_asset_id
- checksum snapshot
- stem gốc
- normalized_stem
- validation summary
- missing/duplicate report

Nếu file gốc bị xóa nhưng managed asset còn, pair vẫn resolve được.

## Speaker Reference

`SpeakerReference` và `VoiceConfig.speaker_reference` ưu tiên:

- audio_asset_id
- text_asset_id
- selected_segment_id

Legacy `reference_audio` và `reference_text` vẫn load.

## Training Reference

`TrainingReferenceConfig` hỗ trợ:

- speaker_reference_asset_id
- speaker_reference_text_asset_id
- audio_text_manifest_id
- selected_segment_asset_ids
- dataset_id
- dataset_item_ids
- validation_report_ids

Resolver ưu tiên asset ID nếu có, fallback legacy path khi chưa migrate.
