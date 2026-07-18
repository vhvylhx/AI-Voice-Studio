# Job Worker Contract

Worker phai ho tro execute, request_pause, request_resume, request_cancel, report_progress, write_log, heartbeat, checkpoint va cleanup.

Worker khong sua UI truc tiep. UI nhan event/progress thread-safe.
# AVS-014.15 Resource Requirement Contract

- Worker class co the khai bao `resource_requirement`.
- Requirement phai JSON-safe va mo ta CPU/RAM/Disk/GPU/VRAM can thiet.
- Worker khong tu cap phat GPU/VRAM lease; Queue/Resource Manager lam viec nay truoc khi Worker chay.
- Worker van phai cooperative pause/cancel tai safe point.

---
