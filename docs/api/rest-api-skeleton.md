# REST API Skeleton

Placeholder request/response shapes. **Not OpenAPI — to be generated at implementation.**

---

## POST `/v1/plates/recognize`

**Purpose:** Submit image for ANPR.

### Request (placeholder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_ref` | string | one of | URI or storage key |
| `image_base64` | string | one of | Base64-encoded image |
| `source_id` | string | no | Camera or upload source |
| `captured_at` | string (ISO-8601) | no | Capture timestamp |

### Response (placeholder)

| Field | Type | Description |
|-------|------|-------------|
| `plate_text` | string | Normalized plate |
| `confidence` | number | 0.0–1.0 |
| `bounding_box` | object | _TBD_ |
| `sighting_id` | string | If persisted |

---

## POST `/v1/plates/verify`

### Request (placeholder)

| Field | Type | Required |
|-------|------|----------|
| `plate_text` | string | yes |
| `jurisdiction` | string | no |

### Response (placeholder)

| Field | Type | Description |
|-------|------|-------------|
| `valid` | boolean | Registry match |
| `vehicle_summary` | object | _TBD — privacy filtered_ |
| `mismatch_reasons` | array | If invalid |

---

## POST `/v1/plates/clone-check`

### Request (placeholder)

| Field | Type | Required |
|-------|------|----------|
| `plate_text` | string | yes |
| `sighting_id` | string | no |
| `location` | object | no |

### Response (placeholder)

| Field | Type | Description |
|-------|------|-------------|
| `clone_risk_score` | number | 0.0–1.0 |
| `clone_suspected` | boolean | |
| `signals` | array | Explainability _TBD_ |

---

## GET `/v1/health`

### Response (placeholder)

| Field | Type |
|-------|------|
| `status` | string |
| `version` | string |
