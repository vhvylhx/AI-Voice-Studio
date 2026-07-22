# Planning Checklist

Dùng checklist này trước khi công bố implementation plan. Không đặt `READY FOR IMPLEMENTATION` nếu bất kỳ mục bắt buộc nào chưa có evidence đủ.

## Scope and Evidence

- [ ] User intent, desired outcome, scope và non-goals đã rõ.
- [ ] Allowed paths và files/modules không được sửa đã xác định.
- [ ] Đã đọc Rules, status/sprint/roadmap, Architecture/Decisions và Memory Bank theo thứ tự áp dụng.
- [ ] Đã đọc current source/configuration trực tiếp liên quan.
- [ ] Đã đọc caller/entry point và dependency/extension point liên quan.
- [ ] Đã đọc targeted tests/fixtures và phân biệt fake/mock/test-only với production evidence.
- [ ] Current state được gắn evidence; fact, inference và unknown được phân biệt.

## Contract and Risk

- [ ] Acceptance criteria user-observable và có thể kiểm chứng.
- [ ] Public/internal API, default/error/state semantics và caller compatibility đã được đánh giá.
- [ ] Identity, ownership, persistence, frozen snapshot/lineage hoặc state machine đã được đánh giá khi áp dụng.
- [ ] Data safety, artifact/output collision và recovery risk đã được đánh giá khi áp dụng.
- [ ] Resource/queue/lease/cancel/retry/resume risk đã được đánh giá khi áp dụng.
- [ ] Runtime/language/asset/readiness/security/UI-responsiveness risk đã được đánh giá khi áp dụng.
- [ ] UTF-8/Vietnamese text/line-ending impact đã được xác định khi source/UI/docs bị chạm.

## Decision and Implementation Strategy

- [ ] Decision đã có được liên kết tới evidence.
- [ ] `USER DECISION REQUIRED` được nêu nếu phát hiện quyết định mới chưa được phê duyệt.
- [ ] Không có plan detail dựa trên decision chưa được phê duyệt.
- [ ] Files to modify và files not to modify đã được liệt kê cùng lý do.
- [ ] Implementation slices dependency-safe, minimal và không có scope growth/refactor không cần thiết.
- [ ] Mỗi slice nêu extension point, invariant, caller impact, failure behavior và validation.

## Validation and Output

- [ ] Validation plan liên kết từng acceptance criterion/risk với test, compile, smoke hoặc diff evidence.
- [ ] Prerequisite/environment và limitation của từng validation đã được nêu.
- [ ] `git diff --check` và `git status --short` read-only được đưa vào final validation plan.
- [ ] Report dùng đúng template và chỉ một final status:
  - `READY FOR IMPLEMENTATION`
  - `BLOCKED`
  - `USER DECISION REQUIRED`