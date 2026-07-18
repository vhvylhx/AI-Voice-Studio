# Project Registry

Project Registry chỉ lưu metadata đủ để tìm và hiển thị Project:

- project_id;
- display_name;
- root_path;
- status;
- archive_state;
- last_opened_at;
- favorite;
- health_state;
- missing.

Registry không chứa toàn bộ Project data.

Ghi registry phải atomic. Project missing không bị tự xóa khỏi registry.
