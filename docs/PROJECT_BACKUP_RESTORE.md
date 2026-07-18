# Project Backup Restore

Backup dùng để khôi phục cùng môi trường, khác Export portable.

Backup hiện lưu:

- backup_manifest.json;
- project.json;
- reason;
- timestamp;
- schema/project metadata.

Restore phải:

1. validate backup;
2. tạo safety backup hiện tại;
3. restore file;
4. giữ Project ID nếu backup thuộc cùng Project.

Không restore chồng nếu chưa có safety backup.
# AVS-014.13.1 Reference backup modes

Project backup co hai muc:

- Metadata backup: project config + reference registry/metadata/manifest.
- Complete backup: gom them managed reference media de restore doc lap.

Khong goi metadata backup la doc lap neu thieu media reference.
