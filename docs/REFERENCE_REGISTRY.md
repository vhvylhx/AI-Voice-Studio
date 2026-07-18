# Reference Registry

Reference Registry lưu metadata tối thiểu để tìm và kiểm tra asset.

Registry gồm:

- asset_id
- asset_type
- managed_relative_path
- checksum
- checksum_algorithm
- original_filename
- storage_scope
- validation_state
- last_verified_at
- archive state
- usage mapping

Registry được ghi atomic. Nếu registry JSON hỏng, app backup file hỏng và dùng registry rỗng thay vì crash.

Registry không xóa asset khi Project close, rename hoặc archive.
