# Reference Data Safety

Nguyên tắc an toàn:

- không sửa file gốc;
- không xóa dữ liệu thật;
- không Train/Generate khi chỉ quản lý reference;
- không tạo Voice DNA giả;
- không tự chọn segment khác nếu segment cũ mất;
- không thay asset bằng file cùng tên.

Managed copy là bản app quản lý. File gốc ngoài app là nguồn ban đầu và provenance.
## Reference jobs

Reference Verify Job chi doc va verify checksum. Job khong thay asset ID, khong thay managed copy bang file cung ten va khong tu relink neu checksum khac.
