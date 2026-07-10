# Verification API

Base path: `/v1/verification`

Standalone plate verification without submitting a new image. Uses OCR text or existing scan.

---

## POST /v1/verification

Verify a plate number against the registry and run attribute analysis.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/verification` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Request DTO — `VerifyPlateRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `plate_text` | string | yes | 1–16 chars; normalized server-side |
| `jurisdiction` | string | no | 2–8 char region code |
| `scan_id` | UUID | no | Link verification to existing scan |
| `observed_attributes` | object | no | `{ color, vehicle_type, make }` for mismatch check |
| `force_refresh` | boolean | no | Bypass vehicle cache |

#### observed_attributes

| Field | Type | Validation |
|-------|------|------------|
| `color` | string | Max 32 chars |
| `vehicle_type` | enum | `car`, `motorcycle`, `truck`, `other` |
| `make` | string | Max 64 chars |

### Response DTO — `VerificationResponse` (HTTP 201)

| Field | Type | Description |
|-------|------|-------------|
| `verification_id` | UUID | Verification record ID |
| `scan_id` | UUID | Linked scan (nullable) |
| `plate_text` | string | Normalized plate verified |
| `outcome_status` | enum | `valid`, `invalid`, `unknown`, `expired`, `not_found` |
| `vehicle_id` | UUID | Matched vehicle (nullable) |
| `vehicle` | `VehicleRecord` | Registry record (nullable) |
| `attribute_match_score` | decimal | 0.0–1.0 |
| `mismatch_reasons` | `MismatchReason[]` | Empty if valid |
| `verified_at` | timestamp | Completion time |

#### MismatchReason

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | e.g. `COLOR_MISMATCH`, `REGISTRATION_STOLEN` |
| `field` | string | Attribute compared |
| `expected` | string | Registry value |
| `observed` | string | Observed value |
| `severity` | enum | `low`, `medium`, `high`, `critical` |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid plate format |
| 404 | `NOT_FOUND` | `scan_id` does not exist |
| 422 | `UNPROCESSABLE` | Plate fails domain format rules |
| 503 | `SERVICE_UNAVAILABLE` | Registry unavailable |

---

## GET /v1/verification/{verification_id}

Retrieve a verification result by ID.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/verification/{verification_id}` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `verification_id` | UUID | Valid UUID |

### Response DTO — `VerificationResponse`

Same as `POST /v1/verification`.

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Verification not found |
| 403 | `AUTH_FORBIDDEN` | Officer cannot access other station's record |

---

## GET /v1/verification/by-scan/{scan_id}

Retrieve verification outcome for a specific scan.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/verification/by-scan/{scan_id}` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `scan_id` | UUID | Must reference existing scan |

### Response DTO — `VerificationResponse`

Same as `POST /v1/verification`.

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Scan or verification not found |

---

## GET /v1/verification

List verification records with filters.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/verification` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `VerificationListQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `outcome_status` | enum | no | Filter by outcome |
| `plate` | string | no | Partial plate match |
| `from` | timestamp | no | Date range start |
| `to` | timestamp | no | Date range end |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `VerificationListResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `VerificationListItem[]` | Summaries |
| `pagination` | object | Page metadata |

#### VerificationListItem

| Field | Type |
|-------|------|
| `verification_id` | UUID |
| `scan_id` | UUID |
| `plate_text` | string |
| `outcome_status` | enum |
| `attribute_match_score` | decimal |
| `verified_at` | timestamp |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |
