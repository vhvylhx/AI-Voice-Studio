# UI Design System

## AVS-014.13 Project Manager UI

Project Manager la trang quan ly vong doi Project, khong phai Dashboard va khong phai Settings.

Quy tac:

- PageHeader phai hien "Du an", Project hien tai, Project ID va health state khi co.
- Action nguy hiem mac dinh dung Archive thay vi Delete.
- Khong expose Delete vinh vien trong Sprint nay.
- Project card hien display name la chinh, Project ID la thong tin phu.
- Path hien rut gon/word-wrap de khong ep ngang cua so.
- Dialog/action phai khong tu Train, Generate hoac scan nang.
- Page dai phai dung scroll foundation.

## AVS-014.12 Scroll / responsive foundation

AVS-014.12 bo sung:

- `ContentScrollArea`
- `ScrollablePage`

Page dai phai dung scroll foundation de noi dung khong ep MainWindow giu kich thuoc lon. TrainingPage la page dau tien dung nen chung nay.

Quy tac:

- scroll area `widgetResizable=True`;
- mac dinh khong can horizontal scrollbar;
- nut cuoi trang phai truy cap duoc bang wheel/scroll;
- layout phai uu tien word wrap va section/card lon thay vi nhieu dong mong.

## Mục tiêu

AVS-014.11 bắt đầu chuyển UI từ các form dài sang bố cục desktop dễ đọc hơn:

- sidebar rõ nhóm chức năng;
- page header;
- card/section;
- empty state;
- status badge;
- settings row có label, control và hint.

## Component nền

Các component dùng chung nằm trong `src/widgets/ui_components.py`:

- `PageHeader`
- `SectionCard`
- `StatusBadge`
- `EmptyState`
- `SettingsRow`

## Quy tắc layout

- Page quan trọng cần có title/subtitle.
- Không nhồi tất cả setting vào một hàng mỏng kéo dài.
- Section nên gom theo mục đích nghiệp vụ.
- Empty state phải nói rõ người dùng cần làm gì tiếp theo.
- UI chỉ gọi Service, không đọc/ghi repository trực tiếp.

## Trang Phong cách đọc

Trang Style Profile cần có:

- danh sách Style Profile;
- chi tiết readiness;
- trạng thái extraction;
- thao tác tạo từ Dataset;
- import/export `.avstyle`;
- kiểm tra dữ liệu;
- backup.

## Trang Cong viec / Hang doi

- Hien summary queued, running, paused, failed va completed.
- Job list hien display name, job type, state, priority va progress.
- Detail panel hien Job ID, owner IDs, dependencies, progress, error, result va log tail.
- Action Pause/Resume/Cancel/Retry/Change priority phai goi service, khong sua state truc tiep trong UI.
- UI khong chay Train/Generate/analyzer that trong sprint Job foundation.

Sprint này chưa làm analyzer thật và chưa gọi Generate thật bằng Style Profile.
# AVS-014.15 Resource Monitor UI

- Resource Monitor hien snapshot CPU/RAM/Disk/GPU/VRAM, pressure_state, lease dang active va job dang `waiting_resource`.
- UI chi doc ResourceMonitorService, khong tu quet hardware va khong kill process.
- Dashboard chi hien pressure summary ngan.
- JobsPage hien Resource Policy, Resource Pressure, Resource Wait, Resource Lease va GPU selected trong detail panel.
- Settings hien Resource Policy hien hanh; editor day du se lam o sprint sau.

---
