# Reference Relink / Repair

Relink chỉ áp dụng cho external/provenance path bị mất.

Quy tắc:

- kiểm tra checksum nếu có;
- checksum mismatch chỉ warning/block, không tự nhận;
- không thay managed asset tốt bằng file cùng tên;
- original path mất không làm reference mất nếu managed asset còn.

Repair an toàn:

- verify checksum;
- rebuild registry từ metadata;
- normalize relative path;
- restore registry entry;
- restore từ backup.

Không repair bằng cách tạo audio/text/style giả.
