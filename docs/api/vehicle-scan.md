# Vehicle Scan API

Base path: `/v1/scans`

Triggers the full AI pipeline (detection → OCR → lookup → verification → risk → decision).

---

## POST /v1/scans

Submit a vehicle image and run the ANPR pipeline.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/scans` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |
| **Content-Type** | `multipart/form-data` |

### Request DTO — `CreateScanRequest` (multipart)

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `image` | file | one of | JPEG/PNG; max 10 MB; min 640×480 px |
| `image_storage_key` | string | one of | Pre-uploaded object key |
| `scanned_at` | timestamp | no | ISO-8601; default `now`; not future |
| `latitude` | decimal | no | -90.0 to 90.0 |
| `longitude` | decimal | no | -180.0 to 180.0 |
| `location_label` | string | no | Max 200 chars |
| `camera_id` | string | no | Max 64 chars |
| `jurisdiction` | string | no | 2–8 char region code |
| `async` | boolean | no | Default `false`; if `true`, return 202 with scan_id |

### Response DTO — `ScanResponse` (sync, HTTP 201)

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan identifier |
| `processing_status` | enum | `completed` or `failed` (sync mode) |
| `detected_plate_text` | string | Raw OCR output |
| `normalized_plate_text` | string | Normalized plate |
| `ocr_confidence` | decimal | 0.0–1.0 |
| `detection_confidence` | decimal | 0.0–1.0 |
| `verification` | `VerificationSummary` | Embedded verification outcome |
| `risk` | `RiskSummary` | Embedded risk assessment |
| `decision` | enum | `clear`, `monitor`, `investigate`, `detain`, `escalate` |
| `decision_reasons` | string[] | Human-readable justifications |
| `alert_ids` | UUID[] | Alerts raised |
| `scanned_at` | timestamp | Capture time |
| `completed_at` | timestamp | Pipeline completion time |
| `correlation_id` | UUID | Trace ID |

#### VerificationSummary (embedded)

| Field | Type |
|-------|------|
| `outcome_status` | enum |
| `attribute_match_score` | decimal |
| `mismatch_reasons` | object[] |

#### RiskSummary (embedded)

| Field | Type |
|-------|------|
| `risk_score` | decimal |
| `clone_suspected` | boolean |
| `signals` | object[] |

### Response DTO — `ScanAcceptedResponse` (async, HTTP 202)

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan identifier |
| `processing_status` | enum | `received` |
| `poll_url` | string | `/v1/scans/{scan_id}` |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid image, missing image, bad coordinates |
| 401 | `AUTH_MISSING` | No token |
| 403 | `AUTH_FORBIDDEN` | Officer inactive or wrong role |
| 422 | `UNPROCESSABLE` | Officer not on active duty |
| 503 | `SERVICE_UNAVAILABLE` | ML service unavailable |

---

## GET /v1/scans/{scan_id}

Retrieve scan status and full pipeline result.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/scans/{scan_id}` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `scan_id` | UUID | Valid UUID v4 |

### Request DTO

None.

### Response DTO — `ScanDetailResponse`

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan identifier |
| `officer_id` | UUID | Scanning officer |
| `vehicle_id` | UUID | Matched vehicle (nullable) |
| `processing_status` | enum | Pipeline status |
| `failure_reason` | string | If `failed` |
| `detected_plate_text` | string | Raw OCR |
| `normalized_plate_text` | string | Normalized plate |
| `ocr_confidence` | decimal | OCR confidence |
| `detection_confidence` | decimal | Detection confidence |
| `image_storage_key` | string | Full image reference |
| `crop_storage_key` | string | Plate crop reference |
| `latitude` | decimal | GPS |
| `longitude` | decimal | GPS |
| `location_label` | string | Location name |
| `camera_id` | string | Device ID |
| `verification` | `VerificationSummary` | Verification outcome |
| `risk` | `RiskSummary` | Risk assessment |
| `decision` | enum | Pipeline decision |
| `decision_reasons` | string[] | Justifications |
| `alert_ids` | UUID[] | Linked alerts |
| `scanned_at` | timestamp | Capture time |
| `completed_at` | timestamp | Completion time |
| `correlation_id` | UUID | Trace ID |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 401 | `AUTH_INVALID` | Invalid token |
| 403 | `AUTH_FORBIDDEN` | Officer cannot access other station's scan |
| 404 | `NOT_FOUND` | Scan does not exist |

---

## GET /v1/scans

List scans with filters.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/scans` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `ScanListQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `officer_id` | UUID | no | Filter by officer |
| `station_id` | UUID | no | Filter by station (supervisor+) |
| `plate` | string | no | Partial plate match |
| `decision` | enum | no | Filter by decision |
| `processing_status` | enum | no | Filter by status |
| `clone_suspected` | boolean | no | Filter flagged scans |
| `from` | timestamp | no | Start of date range |
| `to` | timestamp | no | End of date range; must be ≥ `from` |
| `page` | integer | no | Default 1, min 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `ScanListResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `ScanListItem[]` | Scan summaries |
| `pagination` | object | Page metadata |

#### ScanListItem

| Field | Type |
|-------|------|
| `scan_id` | UUID |
| `normalized_plate_text` | string |
| `processing_status` | enum |
| `decision` | enum |
| `clone_suspected` | boolean |
| `officer_id` | UUID |
| `scanned_at` | timestamp |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid date range or enum |
| 403 | `AUTH_FORBIDDEN` | Officer querying other station without permission |

---

## POST /v1/scans/{scan_id}/retry

Retry a failed scan pipeline from last successful stage.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/scans/{scan_id}/retry` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `scan_id` | UUID | Must reference a `failed` scan |

### Request DTO

None (empty body).

### Response DTO — `ScanResponse`

Same as `POST /v1/scans` sync response.

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Scan not found |
| 422 | `UNPROCESSABLE` | Scan not in `failed` state or not retry-eligible |
| 503 | `SERVICE_UNAVAILABLE` | ML service down |
