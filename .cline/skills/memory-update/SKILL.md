---
name: memory-update
description: Update the project Memory Bank from verified repository state, current decisions, completed validation, and confirmed user instructions without guessing or changing source code.
---

# Memory Bank Update

Skill này chỉ cập nhật `memory-bank/` từ trạng thái repository đã được xác minh. Không dùng để “đồng bộ theo suy đoán”, sửa source/test, đổi Rules, hoặc che khoảng trống validation bằng documentation.

Áp dụng Shared Framework ở chế độ documentation-only:

- [Operating Modes](../shared/operating-modes.md)
- [Decision Gates](../shared/decision-gates.md)
- [Validation Contract](../shared/validation-contract.md)
- [Reporting Contract](../shared/reporting.md)

## Scope and Source of Truth

Nguồn cho Memory Bank chỉ gồm:

1. User instruction/approval đã xác nhận.
2. Source, tests, configuration và architecture hiện tại đã đọc.
3. Command/test/validation result đã chạy thật.
4. Decision hiện có trong docs/Memory Bank nếu không mâu thuẫn source.
5. Git diff/status read-only để xác định thay đổi thuộc scope.

Khi nguồn mâu thuẫn, source hiện tại có ưu tiên theo project Rules. Không dùng conversation summary, TODO, intended work, fake/mock pass hoặc runtime discovery làm fact production.

## Workflow

```text
1. Define requested Memory Bank scope and excluded files
   ↓
2. Read current Memory Bank, Rules and evidence source
   ↓
3. Classify facts, decisions, unknowns and stale/conflicting statements
   ↓
4. Identify exact Memory Bank files requiring minimal updates
   ↓
5. Apply documentation-only changes with provenance
   ↓
6. Validate UTF-8, internal consistency, links and no source changes
   ↓
7. Report verified updates, unresolved conflicts and limitations
```

## Update Rules

- Chỉ sửa file `memory-bank/` được chứng minh cần cập nhật.
- Giữ Markdown/UTF-8/tiếng Việt và cấu trúc file hiện có.
- Mỗi capability phải mô tả trạng thái thực tế (`READY`, `BLOCKED`, `UNAVAILABLE`, `TEST_ONLY`, v.v.) cùng evidence/blocker khi cần.
- Không nâng production readiness từ fake engine, mock runtime, fixture, asset cache, executable discovery hoặc test-only smoke.
- Không ghi “đã hoàn thành” nếu implementation/test/validation không có evidence.
- Không ghi secret, token, path nhạy cảm, dữ liệu user source hoặc nội dung không cần thiết.
- Không tự chỉnh docs source-of-truth ngoài Memory Bank, trừ khi task yêu cầu rõ.
- Không đổi product/architecture decision; nếu evidence chỉ ra quyết định mới cần thiết, báo Decision Gate thay vì tự ghi thành decision.

## Conflict and Staleness Handling

Khi Memory Bank khác source:

```text
MEMORY CONFLICT
Memory statement: <file/section + nội dung>
Repository evidence: <source/test/command>
Priority: <lý do source hiện tại được ưu tiên>
Safe update: <thay đổi Memory Bank tối thiểu>
Unresolved impact: <nếu có>
```

Không xoá historical decision chỉ vì source đã thay đổi; ghi rõ trạng thái superseded/outdated khi cấu trúc Memory Bank hỗ trợ và task cho phép.

## Validation

- Đọc lại toàn bộ file đã sửa.
- Kiểm tra UTF-8, heading/link/reference integrity và terminology consistency.
- Đảm bảo chỉ `memory-bank/` thay đổi trong scope của Skill.
- Chạy `git diff --check` và `git status --short` read-only.
- Không chạy test/source mutation chỉ để cập nhật Memory Bank; report validation evidence đã có thay vì tạo evidence giả.

## Required Report

```text
## MEMORY UPDATE SCOPE
## VERIFIED SOURCES
## UPDATED FACTS AND DECISIONS
## CONFLICTS / STALE STATEMENTS
## UNVERIFIED OR EXCLUDED ITEMS
## FILES CHANGED
## VALIDATION
## FINAL STATUS
```

Final Status dùng vocabulary được `AGENTS.md` cho phép.