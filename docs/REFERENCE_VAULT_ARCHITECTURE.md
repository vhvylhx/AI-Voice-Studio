# Reference Vault Architecture

Reference Vault là kho dữ liệu tham chiếu do AI Voice Studio quản lý.

Mục tiêu:

- giữ managed copy cho audio/text/manifest/report;
- liên kết bằng stable asset ID;
- không phụ thuộc filename, display name hoặc absolute path máy cũ;
- hỗ trợ checksum, deduplication, backup, export, import, restore và repair an toàn.

## Cấu trúc

Mặc định:

```text
workspace/reference_vault/
├── audio/
├── text/
├── manifests/
├── pairs/
├── segments/
├── reports/
├── style_sources/
├── speaker_references/
├── normalized/
├── registry/
└── temp/
```

Đường dẫn serialized trong config/registry ưu tiên relative path từ vault root.

## Nguyên tắc

- File gốc bên ngoài app chỉ là provenance.
- Managed copy là bản app dùng lâu dài.
- Rename Project/Voice/Style Profile không làm mất reference.
- Archive Project không xóa reference.
- Không thay asset bằng file cùng tên nếu checksum khác.
