# Completion

## Điều kiện trước khi completion

Chỉ completion sau khi implementation, validation và Git diff review đã hoàn tất theo phạm vi task.

Không dùng `READY` nếu Definition of Done chưa đủ điều kiện.

Definition of Done tối thiểu gồm:

- Acceptance criteria đã được xác minh bằng evidence hoặc được nêu là blocker/limitation.
- Validation bắt buộc theo scope đã đạt; mọi `FAIL`, `BLOCKED` hoặc `NOT RUN` được báo trung thực.
- Git diff đã được review về scope, correctness, safety, compatibility và unexpected change.
- Scope thay đổi đã được kiểm tra và tách biệt với dirty worktree tồn tại trước.
- Encoding/UTF-8 đã được xác minh khi có file sửa/tạo.
- Capability, blocker, phần không kiểm tra được và rủi ro được báo trung thực.
- Không có claim production/readiness nào chỉ dựa trên fake, mock, test-only, cache, file tồn tại hoặc process exit code.

## Cấu trúc report bắt buộc

Dùng đúng các mục sau:

### KEEP

Nêu các behavior, public/default/error contract, identity/persistence/lineage, data hoặc capability được giữ nguyên.

### NEW

Nêu file hoặc behavior mới được tạo. Nếu không có, ghi `Không có`.

### REPLACE

Nêu nội dung đã thay thế, caller/contract impact và compatibility behavior, nếu có. Nếu không có, ghi `Không có`.

### DELETE

Nêu file/nội dung đã xóa, nếu có. Nếu không có, ghi `Không có`.

### TESTED

Với từng check, liệt kê command/check, kết quả thực tế, criterion/risk đã đánh giá và giới hạn evidence. Không ghi pass cho command chưa chạy.

### NOT TESTED

Liệt kê chính xác kiểm tra chưa chạy, lý do, ảnh hưởng, blocker và residual risk. Ghi `Không có` khi tất cả required checks đã chạy.

### PRE-EXISTING ISSUES

Liệt kê vấn đề, dirty worktree hoặc failure đã tồn tại trước task và không do thay đổi hiện tại gây ra. Không suy đoán ownership nếu không có evidence.

### RISKS

Nêu rủi ro còn lại, blocker, assumption chưa xác minh, recovery implication hoặc giới hạn môi trường.

### FILES CHANGED

Liệt kê đầy đủ file đã tạo/sửa/xóa bởi task hiện tại; phân biệt rõ với thay đổi tồn tại trước đó.

### CAPABILITY TABLE

Liệt kê capability bị ảnh hưởng và trạng thái thực tế, evidence/blocker. Phân biệt rõ `READY`, `DEGRADED`, `TEST_ONLY`, `UNAVAILABLE`, `BLOCKED`, `NOT_IMPLEMENTED`, `MISSING` hoặc `NOT_APPLICABLE` theo contract áp dụng. Nếu không chạm capability, ghi `Không áp dụng`.

### FINAL STATUS

Chỉ dùng một trạng thái được `AGENTS.md` cho phép và phù hợp Definition of Done/kết quả validation thực tế:

- `READY_FOR_GITHUB_REVIEW`
- `SOURCE_DOCS_TESTS_READY`
- `WORKTREE_NOT_CLEAN_DUE_TO_REAL_USER_DATA`
- `NOT_READY`

Không dùng trạng thái sẵn sàng khi còn validation bắt buộc chưa đạt/chưa chạy, scope chưa phân loại, hoặc capability chỉ được chứng minh bằng test/fake. Khi source, docs và tests phù hợp nhưng worktree vẫn dirty do dữ liệu thật có sẵn không được phép chạm, dùng `WORKTREE_NOT_CLEAN_DUE_TO_REAL_USER_DATA`.