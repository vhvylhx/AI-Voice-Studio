# Technical Context — AI Voice Studio

## Stack và cấu trúc

- Python, PySide6, Windows desktop.
- Engine chính hiện tại: GPT-SoVITS; kiến trúc phải cho phép adapter/engine khác.
- Source chính nằm trong `src/`, với các nhóm `core/`, `services/`, `models/`, `engines/`, `repositories/`, `pages/`, `widgets/`, `api/`.
- Tests nằm trong `tests/`.

## Luồng dependency cần giữ

```text
UI → Page/Controller → Service → Job Queue → Engine Manager → Engine Adapter → Runtime
```

- Widget không chứa business logic.
- Service là application contract cho UI/API.
- Repository chỉ persistence; Engine không quản lý Project/Voice/Variant/Style/UI state.
- Worker không phụ thuộc Project đang mở trên UI.

## Contracts cần lưu ý

- Job mang `project_id`, `session_id` và các immutable IDs cần thiết; job nặng cần `ResourceRequirement`.
- Generate dùng Request, Session, frozen Plan, Unit, Attempt và Artifact lineage riêng.
- Artifact chỉ thành công sau validation và lineage hợp lệ; job thành công hoặc file tồn tại không đủ.
- Runtime và engine production chỉ được khai báo READY khi integration/asset/validation/real smoke tương ứng đều đạt.

## Các source được nêu trong Sprint

- Training/runtime: `src/services/training_service.py`, `src/services/runtime_service.py`, `src/engines/gpt_sovits_adapter.py`, `src/engines/gpt_sovits_engine.py`.
- Engine management: `src/core/engine_manager.py`, `src/core/app_context.py`.
- Voice: `src/services/voice_service.py`, `src/models/voice_config.py`, `src/models/voice_model.py`.
- Adapter contracts: `src/engines/adapter/base_adapter.py`, `src/engines/adapter/runtime.py`.