# Reference Migration

Migration mềm:

- legacy config vẫn load;
- không xóa field cũ;
- nếu legacy path còn, có thể import vào Vault;
- nếu chưa có xác nhận, không copy hàng loạt file lớn;
- sau migration ưu tiên asset ID;
- legacy path là fallback/provenance.

Không đổi:

- Project ID;
- Voice ID;
- Style Profile ID;
- Variant ID.
