# Job Queue

Persistent Queue ton tai qua restart.

Ho tro enqueue, dequeue, list, priority, idempotency_key, dependency waiting/blocked va mac dinh mot job tai mot thoi diem.

Sprint nay chua chay parallel GPU task.
# AVS-014.15 Resource-aware Queue

- `queued` job duoc kiem tra dependency truoc, resource sau.
- Neu dependency chua xong: `waiting_dependency`.
- Neu resource chua du: `waiting_resource`.
- Neu resource unsupported: `blocked`.
- Queue khong duoc dua workflow nang vao chay neu workflow chua khai bao handler va requirement ro rang.
- Lease giup tranh chay trung GPU job theo policy.

---
