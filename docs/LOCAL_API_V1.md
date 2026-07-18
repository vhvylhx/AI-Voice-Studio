# AI Voice Studio Local API v1

Local API cho phép ứng dụng khác trên cùng máy, ví dụ app làm video, yêu cầu AI Voice Studio tạo audio và lấy kết quả.

MVP mặc định:

- Host: `127.0.0.1`
- Port: `8765`
- Base URL: `http://127.0.0.1:8765`
- Token: bắt buộc cho hầu hết endpoint.
- Header: `Authorization: Bearer <token>`

Không dùng API này như API Internet/public.

## Bật API

1. Mở Settings.
2. Mở nhóm API & Tích hợp.
3. Bật API nội bộ.
4. Kiểm tra Host là `127.0.0.1`.
5. Bấm Khởi động API.
6. Sao chép Token nếu app video cần gọi API.

## Health

Không cần token.

```http
GET /api/v1/health
```

Trả về trạng thái tối thiểu, không lộ token hoặc đường dẫn model.

## Readiness

Cần token.

```http
GET /api/v1/readiness
Authorization: Bearer <token>
```

Trả về trạng thái từng tính năng: app shell, DOCX, alignment, training, generation, local_api.

## Capabilities

```http
GET /api/v1/capabilities
Authorization: Bearer <token>
```

Cho app video biết định dạng, ngôn ngữ và giới hạn MVP.

## Voice Catalog

```http
GET /api/v1/voices
Authorization: Bearer <token>
```

Không trả checkpoint path, dataset path, runtime path hoặc pretrained path.

```http
GET /api/v1/voices/0001
Authorization: Bearer <token>
```

## Variant Catalog

```http
GET /api/v1/voices/0001/variants
Authorization: Bearer <token>
```

Variant là generate profile, không phải model. API không có endpoint `/variants/{id}/model`.

## Catalog gộp

```http
GET /api/v1/voice-catalog
Authorization: Bearer <token>
```

Trả về voices, variants, presets và capabilities.

## Tạo generation job

```http
POST /api/v1/generation/jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "voice_id": "0001",
  "variant_id": "default",
  "text": "Nội dung cần lồng tiếng.",
  "language": "vi",
  "output_format": "wav",
  "sample_rate": 32000,
  "speed": 1.0,
  "request_id": "video-app-unique-id"
}
```

Nếu Voice chưa có model/reference hợp lệ:

- API trả lỗi tiếng Việt rõ ràng.
- Không tạo audio giả.
- Không tự Train.

## Xem trạng thái job

```http
GET /api/v1/generation/jobs/<job_id>
Authorization: Bearer <token>
```

Status chuẩn:

- queued
- preparing
- generating
- post_processing
- completed
- failed
- cancelled

## Hủy job

```http
POST /api/v1/generation/jobs/<job_id>/cancel
Authorization: Bearer <token>
```

Nếu job đã hoàn thành hoặc thất bại, API trả trạng thái hiện tại và không xóa kết quả.

## Lấy kết quả

```http
GET /api/v1/generation/jobs/<job_id>/result
Authorization: Bearer <token>
```

MVP trả metadata kết quả nếu job đã hoàn thành. Nếu chưa hoàn thành, trả `result_not_ready`.

## Timeline

Kết quả sau này có thể chứa:

```json
{
  "segments": [
    {
      "segment_id": "001",
      "text": "...",
      "start_ms": 0,
      "end_ms": 4200,
      "duration_ms": 4200,
      "audio_url": "...",
      "status": "completed"
    }
  ]
}
```

MVP chưa bắt buộc word-level timestamp.

## Bảo mật

- Không bind `0.0.0.0` mặc định.
- Không bật CORS rộng.
- Không trả token qua endpoint thường.
- Không log token.
- Không cho path traversal.
- Không cho tải file ngoài output do app quản lý.
- Không cho chạy command tùy ý.

## Giới hạn MVP

- API dùng stdlib HTTP server để tránh thêm dependency bắt buộc khi Bootstrap/Main App chưa ổn định.
- OpenAPI tự động sẽ được bổ sung nếu sau này chuyển sang FastAPI.
- API không tự Train.
- API không Generate thật nếu Voice chưa generation-ready.
