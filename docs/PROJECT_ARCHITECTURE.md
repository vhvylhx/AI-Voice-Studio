# Project Architecture

Project Manager quản lý vòng đời Project:

- create;
- open;
- close;
- switch;
- recent;
- rename;
- duplicate;
- archive;
- restore archive;
- export/import;
- backup/restore;
- validation/repair.

Service chính hiện là `ProjectService`.

Các service hỗ trợ:

- `ProjectRegistryService`;
- `ProjectValidationService`;
- `ProjectBackupService`;
- `ProjectPackageService`.

## Project jobs

Job co scope `project` chi tham chieu Project bang Project ID. Rename Project chi doi display name, khong lam mat job history.

Project backup/validate co the duoc goi thong qua Job adapter an toan, nhung Sprint AVS-014.14 khong tu dong chuyen tat ca workflow vao Queue va khong dung Project that lam smoke target.

UI chỉ gọi service. Repository/service không gọi UI.
