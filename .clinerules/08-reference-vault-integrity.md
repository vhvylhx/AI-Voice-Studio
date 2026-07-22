# Reference Vault và Speaker Reference — AI Voice Studio

## Identity và ownership

- Mỗi Reference Asset phải dùng `reference_id` bất biến làm identity. Không dùng display name, filename, checksum đơn lẻ hoặc path làm khóa thay thế khi `reference_id` đã tồn tại.
- Đổi tên metadata Reference không được đổi `reference_id`, vị trí asset đã quản lý, liên kết Voice/Project, pair manifest hoặc lineage đã frozen.
- Reference Asset, audio gốc, transcript gốc và metadata nguồn là dữ liệu người dùng; không tự sửa, ghi đè, đổi tên, di chuyển hoặc xóa.
- Không suy diễn ownership từ folder hiện tại, tên người nói hoặc tên file. Mọi liên kết phải qua immutable ID và persistence contract hiện có.
- Reference dùng cho Preview, Generate, Training hoặc Speaker DNA phải được resolve từ snapshot/ID đã persist, không từ state tạm hoặc lựa chọn hiển thị trên UI.

## Import, validation và persistence

- Import phải đi qua Service/Repository và validation workflow hiện có; Widget/Page không được ghi trực tiếp vào Reference Vault, manifest hay registry.
- Chỉ persist asset sau khi các gate bắt buộc theo contract đã pass, gồm định dạng, khả năng đọc, duration, audio/text pairing và policy liên quan.
- Asset file tồn tại, tên hợp lệ hoặc metadata có mặt không tự chứng minh Reference hợp lệ hoặc sẵn sàng dùng cho engine.
- Khi validation lỗi, giữ evidence/blocker có thể hành động và không tạo Reference giả ở trạng thái usable.
- Không silent overwrite Reference, pair manifest, derived cache hoặc bản export đã tồn tại.

## Deduplication, pairing và lineage

- Deduplication chỉ xác định quan hệ theo policy hiện có; không tự xóa, merge hoặc thay thế asset gốc chỉ vì có checksum/tín hiệu tương tự.
- Khi phát hiện duplicate/suspicious/collision, phải lưu kết quả phân loại và để workflow/policy quyết định hành động tiếp theo.
- Audio-text pair phải giữ lineage đến `reference_id`, source asset và transcript/version phù hợp; không ghép theo filename nếu immutable mapping đã tồn tại.
- Derived transcript, waveform, normalized sample, alignment hoặc feature cache phải nằm trong workspace/cache được quản lý, tách khỏi source bất biến.
- Không promote derived cache thành source Reference hoặc production artifact nếu validation/provenance chưa hoàn tất.

## Backup, export, restore và relink

- Backup/export phải giữ immutable ID, metadata và lineage theo contract; không tái tạo ID chỉ để khớp display name hoặc path trên máy khác.
- Restore/import/relink phải validate mapping, integrity và collision trước khi persist; không ghi đè vault/registry hiện có một cách im lặng.
- Relink chỉ sửa liên kết được workflow cho phép, không được làm thay đổi `reference_id`, source evidence hoặc lineage của Session/Plan đã frozen.
- Recovery chỉ phân loại và báo cáo asset orphan/missing/suspicious theo policy; không tự xóa, tự tạo thay thế hoặc tự promote asset.
- Test fixture, audio giả và mock resolver chỉ được dùng trong temporary directory/test composition; không được đưa vào Reference Vault production.