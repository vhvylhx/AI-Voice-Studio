# Project Import Export

Export khác Backup.

Export tạo package portable an toàn. Mặc định package nhẹ gồm:

- manifest.json;
- project.json.

Không export mặc định:

- cache;
- temp;
- output lớn;
- checkpoint/model lớn;
- secret/token;
- runtime command;
- absolute path nhạy cảm.

Import phải validate manifest và chặn:

- path traversal;
- absolute path injection;
- zip slip;
- ghi đè Project hiện có.

Mặc định import as new Project.
# AVS-014.13.1 Reference export/import modes

Export mode:

- lightweight: project.json + metadata reference;
- standard: gom managed reference can thiet;
- full: gom toan bo managed reference lien quan khi user chon.

Import phai validate manifest, chan path traversal/absolute path va co the restore reference_vault vao workspace moi.
