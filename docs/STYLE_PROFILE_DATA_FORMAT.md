# Style Profile Data Format

## Thư mục Style Profile

Mỗi Style Profile nằm trong:

```text
style_profiles/<style_profile_id>/
```

Cấu trúc chuẩn:

```text
style_profile.json
manifest.json
extraction_state.json
extraction_report.json
prosody/
  pause_profile.json
  rhythm_profile.json
  punctuation_profile.json
  intonation_profile.json
  emphasis_profile.json
  breathing_profile.json
  reading_fingerprint.json
indexes/
  reference_index.json
  sentence_index.json
  style_clusters.json
references/
  manifest.json
  optional_selected_clips/
cache/
export/
logs/
backups/
```

## style_profile.json

Các field chính:

- `schema_version`
- `style_profile_id`
- `display_name`
- `description`
- `language`
- `source_type`
- `status`
- `source_summary`
- `dataset_reference`
- `extraction_summary`
- `capabilities`
- `default_tags`
- `integrity`
- `portability`
- `metadata`

## Quy tắc portability

- Dữ liệu nội bộ app dùng path tương đối.
- Export mặc định không chứa MP3 gốc, dataset gốc, model, checkpoint, token hoặc absolute path.
- File phân tích chưa có analyzer thật được tạo placeholder JSON hợp lệ để migration an toàn.

## Variant style fields

Variant được mở rộng migration-safe:

- `style_profile_id`
- `style_mode`: `inherit_voice_default`, `explicit`, `disabled`
- `style_strength`

Các field này không biến Variant thành model.
