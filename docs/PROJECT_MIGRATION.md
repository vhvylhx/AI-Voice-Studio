# Project Migration

Migration mềm:

- Project legacy thiếu display_name sẽ dùng folder name làm display_name.
- Project legacy thiếu project_id sẽ được sinh ID mới khi load.
- Folder legacy theo tên không bị rename.
- Project mới dùng folder ID-based.

Không tự đổi Project ID nếu đã có.

Không tự đổi path thật.

Không xóa project/workspace/cache thật khi migration.
