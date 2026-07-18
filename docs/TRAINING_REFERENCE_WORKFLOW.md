# Training Reference Workflow

Training Reference la cau hinh workflow tren TrainingPage de nguoi dung chon dung loai du lieu tham chieu truoc khi train.

## Ba mode

1. `app_style_profile`
   - Dung Style Profile co san.
   - Chi luu `style_profile_id`, `style_strength`.
   - Khong copy Style Profile vao Dataset.

2. `create_style_profile_from_audio_text`
   - Dung audio + text de tao draft Style Profile.
   - Goi extraction state hien co.
   - Khi chua co analyzer that, state phai la pending/blocked/degraded.
   - Khong tao Voice DNA gia.

3. `speaker_reference_only`
   - Dung audio/transcript tham chieu de clone chat giong.
   - Khong tao Style Profile.
   - Khong thay the Training Dataset.

## Resolve precedence

Chi mode active duoc resolve. Mode inactive co the giu draft nhung khong gui vao engine.

Speaker Reference uu tien:

1. manual selected file/folder;
2. training dataset segment neu nguoi dung bat;
3. voice default reference;
4. none -> invalid/pending.
# AVS-014.13.1 Stable Training Reference

TrainingReferenceConfig uu tien stable IDs:

- speaker_reference_asset_id;
- speaker_reference_text_asset_id;
- audio_text_manifest_id;
- selected_segment_asset_ids;
- dataset_id va dataset_item_ids.

Legacy path van load va duoc xem la fallback/provenance.
