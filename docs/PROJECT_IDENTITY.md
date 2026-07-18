# Project Identity

Project có ba lớp tên:

- Project ID: định danh kỹ thuật bất biến.
- Display name: tên người dùng nhìn thấy, được phép đổi.
- Storage folder: nơi lưu Project trên đĩa.

Project mới ưu tiên storage folder ID-based:

```text
projects/project_000001/
```

Project legacy đang dùng folder theo tên vẫn được load bằng resolver mềm. App không tự rename folder legacy.

Rename Project chỉ đổi display name, không đổi Project ID, không đổi folder, không đổi Voice ID, Style Profile ID hoặc Variant ID.
