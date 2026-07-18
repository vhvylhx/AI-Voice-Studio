# Reference Asset Identity

Reference asset dùng `asset_id` làm identity ổn định.

Không dùng làm identity nội bộ:

- display name;
- filename;
- list index;
- absolute path;
- folder name theo Project title.

## ReferenceAsset

Field chính:

- asset_id
- asset_type
- display_name
- storage_scope
- managed_relative_path
- original_path
- original_filename
- original_size
- checksum
- checksum_algorithm
- extension
- duration
- sample_rate
- channels
- text_encoding
- source_project_id
- source_voice_id
- source_style_profile_id
- source_dataset_id
- pair_group_id
- validation_state
- provenance
- is_managed
- is_external
- is_missing
- is_corrupt
- is_archived

`original_path` chỉ là provenance/fallback, không phải nguồn bền vững duy nhất.
