# Reference Backup / Restore

Project backup có hai mức:

## Metadata Backup

Chứa:

- project.json;
- reference registry/metadata.

Không được gọi là backup độc lập nếu không chứa media.

## Complete Backup

Chứa thêm managed reference assets cần thiết:

- audio/text reference;
- pair manifest;
- selected segment metadata;
- validation report;
- asset metadata và checksum.

Restore phải tạo safety backup trước khi ghi lại config/reference.
