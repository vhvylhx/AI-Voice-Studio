# Speaker Reference Architecture

Speaker Reference la du lieu tham chieu de clone chat giong/timbre.

No khong phai:

- Training Dataset;
- Voice DNA;
- Variant;
- checkpoint.

## Compatibility

`VoiceConfig.reference_audio` va `VoiceConfig.reference_text` van duoc giu de tuong thich GPT-SoVITS/Generate hien tai.

`VoiceConfig.speaker_reference` bo sung contract ro hon:

- source_mode;
- audio_path;
- text;
- folder;
- source_origin;
- state;
- messages;
- metadata.

Voice cu khi load co the mirror legacy reference vao `speaker_reference`, nhung khong xoa field cu.
# AVS-014.13.1 Speaker Reference persistence

Speaker Reference uu tien:

- audio_asset_id;
- text_asset_id;
- selected_segment_id;
- checksum_snapshot.

`VoiceConfig.reference_audio` va `VoiceConfig.reference_text` van load de tuong thich legacy.
