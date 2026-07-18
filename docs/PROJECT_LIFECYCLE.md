# Project Lifecycle

## Create

Tạo Project ID mới, folder ID-based, project.json và folder cần thiết.

## Open

Load Project, cập nhật `last_opened_at`, recent projects và `AppContext.current_project`.

## Close

Clear current project. Không xóa dữ liệu.

## Switch

Clear stale state rồi open Project mới.

## Rename

Chỉ đổi display name.

## Duplicate

Tạo Project ID mới. Mặc định chỉ copy cấu hình/metadata an toàn.

## Archive

Đổi status/archive_state, không xóa folder.

## Restore Archive

Đổi status/archive_state về active.
