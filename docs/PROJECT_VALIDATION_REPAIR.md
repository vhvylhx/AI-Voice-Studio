# Project Validation Repair

Validation kiểm tra:

- project folder;
- project.json;
- Project ID;
- registry mismatch;
- required folders.

Trạng thái:

- valid;
- warning;
- missing;
- invalid;
- blocked.

Repair chỉ sửa lỗi an toàn:

- tạo lại folder thiếu;
- backup trước repair.

Không repair bằng cách tạo Voice/Style/Dataset giả. Không sửa nội dung file người dùng.
# AVS-014.13.1 Reference validation

ProjectValidationService co hook kiem tra Reference Vault khi caller truyen `reference_vault`:

- registry doc duoc;
- asset ID khong collision;
- managed path khong vuot vault root;
- file managed ton tai;
- checksum khop.

Repair reference chi duoc lam cac thao tac an toan, khong tao audio/text/style gia.
