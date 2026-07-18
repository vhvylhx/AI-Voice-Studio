# Reference Deduplication

Deduplication dựa trên:

- checksum;
- asset_type;
- extension.

Không dedupe chỉ bằng tên file.

Quy tắc:

- cùng file nhập lại: dùng lại asset cũ;
- cùng tên khác nội dung: tạo asset khác;
- cùng nội dung khác tên: dùng lại asset nếu asset_type/extension phù hợp;
- asset ID collision: tạo ID mới, không ghi đè.
