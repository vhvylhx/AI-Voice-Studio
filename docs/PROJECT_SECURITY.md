# Project Security

Project import/export phải chống:

- zip slip;
- path traversal;
- absolute path injection;
- overwrite ngoài destination;
- malformed manifest;
- duplicate ID collision;
- secret leakage.

Không thực thi file trong package import.

Không chạy script từ Project.
