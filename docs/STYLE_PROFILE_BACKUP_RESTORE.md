# Style Profile Backup / Restore

## Định dạng `.avstyle`

`.avstyle` là ZIP package dùng để backup/import Reading Style Profile.

Package gồm:

```text
manifest.json
checksums.json
style_profile.json
prosody/
indexes/
references/manifest.json
```

`references/optional_selected_clips/` chỉ được export khi người dùng bật tùy chọn rõ ràng.

## Export mặc định

Mặc định export chỉ chứa dữ liệu phân tích:

- schema;
- prosody profile;
- indexes;
- reference manifest;
- checksums.

Không export mặc định:

- MP3 gốc;
- dataset gốc;
- model/checkpoint;
- token;
- absolute path máy cá nhân.

## Import

Khi import:

- kiểm tra path traversal;
- kiểm tra manifest;
- kiểm tra checksum nếu có;
- chặn package schema mới hơn app;
- chặn trùng ID nếu `keep_id=True` và ID đã tồn tại;
- có thể cấp ID mới khi import nếu cần.

## Backup khi ghi

Repository backup `style_profile.json` trước khi update nếu file cũ tồn tại. Backup nằm trong `backups/` của chính Style Profile.
