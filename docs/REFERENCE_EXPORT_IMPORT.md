# Reference Export / Import

Project export có ba mode:

- lightweight: project config + reference metadata;
- standard: gồm managed reference cần thiết;
- full: gồm toàn bộ managed reference liên quan khi người dùng chọn.

Không export:

- API key;
- token;
- credential;
- temp/cache;
- runtime command;
- absolute original path nhạy cảm.

Import phải validate manifest, chặn path traversal và ghi reference vào vault mới khi có `reference_vault`.
