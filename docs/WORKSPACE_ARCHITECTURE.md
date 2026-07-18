# Workspace Architecture

Application Workspace là dữ liệu chung của app:

- registry;
- settings;
- cache;
- logs;
- temp;
- imports/exports;
- global libraries nếu có.

Project Workspace là dữ liệu thuộc một Project:

- project.json;
- text/;
- audio/;
- export/;
- cache/;
- logs/;
- backups/.

External Source là file người dùng chọn từ ngoài app:

- MP3;
- TXT;
- DOCX;
- reference audio;
- dataset folder.

App không tự sửa hoặc xóa External Source.
