# Reports API

Base path: `/v1/reports`

Investigation report generation and retrieval.

---

## POST /v1/reports

Generate an investigation report for a scan.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/reports` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Request DTO — `GenerateReportRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `scan_id` | UUID | yes | Must reference completed scan |
| `report_type` | enum | yes | `field_summary`, `full_investigation`, `incident` |
| `title` | string | no | Max 255 chars; auto-generated if omitted |
| `template_version` | string | no | Default from config |
| `include_images` | boolean | no | Default `true` |

### Response DTO — `ReportResponse` (HTTP 201)

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | UUID | Report identifier |
| `scan_id` | UUID | Source scan |
| `officer_id` | UUID | Generating officer |
| `report_type` | enum | Report type |
| `title` | string | Report title |
| `status` | enum | `generated` or `draft` |
| `template_version` | string | Template used |
| `file_size_bytes` | integer | PDF size |
| `checksum_sha256` | string | File integrity hash |
| `generated_at` | timestamp | Generation time |
| `download_url` | string | Signed download URL (expires _TBD_) |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid report_type |
| 404 | `NOT_FOUND` | Scan not found |
| 422 | `UNPROCESSABLE` | Scan not completed; insufficient data |
| 503 | `SERVICE_UNAVAILABLE` | PDF generation failure |

---

## GET /v1/reports/{report_id}

Retrieve report metadata.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/reports/{report_id}` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `report_id` | UUID | Valid UUID |

### Response DTO — `ReportDetailResponse`

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | UUID | Report ID |
| `scan_id` | UUID | Source scan |
| `officer_id` | UUID | Generator |
| `officer_name` | string | Generator display name |
| `report_type` | enum | Type |
| `title` | string | Title |
| `status` | enum | `draft`, `generated`, `archived`, `superseded` |
| `template_version` | string | Template version |
| `file_size_bytes` | integer | PDF size |
| `checksum_sha256` | string | Integrity hash |
| `generated_at` | timestamp | Generation time |
| `scan_summary` | object | `{ plate, decision, risk_score, scanned_at }` |
| `download_url` | string | Signed URL |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Report not found |
| 403 | `AUTH_FORBIDDEN` | Scope violation |

---

## GET /v1/reports/{report_id}/download

Download report PDF binary.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/reports/{report_id}/download` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `report_id` | UUID | Must have `generated` status |

### Response

| Attribute | Value |
|-----------|-------|
| Content-Type | `application/pdf` |
| Body | PDF binary stream |
| Header | `Content-Disposition: attachment; filename="report_{report_id}.pdf"` |
| Header | `ETag: {checksum_sha256}` |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Report not found |
| 422 | `UNPROCESSABLE` | Report not yet generated |

---

## GET /v1/reports

List investigation reports.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/reports` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `ReportListQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `scan_id` | UUID | no | Filter by scan |
| `officer_id` | UUID | no | Filter by generator |
| `report_type` | enum | no | Filter by type |
| `status` | enum | no | Filter by status |
| `from` | timestamp | no | Generated after |
| `to` | timestamp | no | Generated before |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `ReportListResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `ReportListItem[]` | Report summaries |
| `pagination` | object | Page metadata |

#### ReportListItem

| Field | Type |
|-------|------|
| `report_id` | UUID |
| `scan_id` | UUID |
| `title` | string |
| `report_type` | enum |
| `status` | enum |
| `generated_at` | timestamp |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer listing other station's reports |

---

## PATCH /v1/reports/{report_id}/archive

Archive a generated report.

| Attribute | Value |
|-----------|-------|
| **Method** | `PATCH` |
| **Route** | `/v1/reports/{report_id}/archive` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Request DTO

Empty body.

### Response DTO — `ReportResponse`

Updated report with `status: archived`.

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |
| 422 | `UNPROCESSABLE` | Report not in `generated` state |
