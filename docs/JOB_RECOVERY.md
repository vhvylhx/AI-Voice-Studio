# Job Recovery

Khi app startup:

- queued giu queued;
- paused giu paused;
- running/pause_requested/resume_requested/cancel_requested/cancelling thanh interrupted;
- corrupt record duoc quarantine;
- auto-resume interrupted mac dinh tat.
# AVS-014.15 Resource Lease Recovery

- Resource lease het han duoc danh dau stale khi startup/snapshot.
- Running job bi shutdown thanh interrupted va release lease.
- Paused job release lease de job khac co the chay; resume se vao queue va cap lease moi.
- Khong auto-resume job nang neu nguoi dung chua xac nhan.

---
