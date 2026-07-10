# History API

Base path: `/v1/history`

Immutable audit trail and scan event timelines.

---

## GET /v1/history/audit

Query system audit logs.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/history/audit` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `AuditLogQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `entity_type` | enum | no | `officer`, `vehicle`, `scan`, `report`, `alert`, `verification`, `risk` |
| `entity_id` | UUID | no | Filter by entity |
| `event_type` | string | no | e.g. `scan.created`, `decision.made` |
| `actor_officer_id` | UUID | no | Filter by acting officer |
| `correlation_id` | UUID | no | Pipeline trace filter |
| `from` | timestamp | no | Occurred after |
| `to` | timestamp | no | Occurred before |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 50, max 200 |

### Response DTO — `AuditLogListResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `AuditLogEntry[]` | Audit entries, newest first |
| `pagination` | object | Page metadata |

#### AuditLogEntry

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | UUID | Entry identifier |
| `event_type` | string | Event code |
| `entity_type` | enum | Entity discriminator |
| `entity_id` | UUID | Referenced entity |
| `actor_officer_id` | UUID | Acting officer (nullable) |
| `actor_name` | string | Officer display name (nullable) |
| `action` | enum | `create`, `update`, `verify`, `assess`, `acknowledge`, etc. |
| `payload_summary` | object | Redacted event detail |
| `correlation_id` | UUID | Trace ID (nullable) |
| `ip_address` | string | Client IP (nullable) |
| `occurred_at` | timestamp | Event time |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid date range |
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |

---

## GET /v1/history/audit/{audit_id}

Retrieve a single audit log entry.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/history/audit/{audit_id}` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `audit_id` | UUID | Valid UUID |

### Response DTO — `AuditLogDetailResponse`

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | UUID | Entry ID |
| `event_type` | string | Event code |
| `entity_type` | enum | Entity type |
| `entity_id` | UUID | Entity reference |
| `actor_officer_id` | UUID | Actor (nullable) |
| `action` | enum | Action performed |
| `payload` | object | Full event payload (privacy-filtered) |
| `correlation_id` | UUID | Trace ID |
| `ip_address` | string | Client IP |
| `user_agent` | string | Client user agent |
| `occurred_at` | timestamp | Event time |
| `created_at` | timestamp | Log write time |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Audit entry not found |
| 403 | `AUTH_FORBIDDEN` | Insufficient role |

---

## GET /v1/history/scans

Scan event timeline with optional plate filter.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/history/scans` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `ScanHistoryQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `plate` | string | no | Normalized plate filter |
| `vehicle_id` | UUID | no | Vehicle filter |
| `officer_id` | UUID | no | Officer filter |
| `station_id` | UUID | no | Station filter (supervisor+) |
| `decision` | enum | no | Decision filter |
| `clone_suspected` | boolean | no | Clone filter |
| `from` | timestamp | no | Scanned after |
| `to` | timestamp | no | Scanned before |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `ScanHistoryResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `ScanHistoryItem[]` | Scan timeline |
| `pagination` | object | Page metadata |

#### ScanHistoryItem

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan ID |
| `plate_text` | string | Normalized plate |
| `vehicle_id` | UUID | Matched vehicle (nullable) |
| `officer_id` | UUID | Scanning officer |
| `officer_name` | string | Officer name |
| `station_id` | UUID | Station |
| `decision` | enum | Pipeline decision |
| `outcome_status` | enum | Verification outcome |
| `risk_score` | decimal | Risk score |
| `clone_suspected` | boolean | Clone flag |
| `location_label` | string | Location |
| `scanned_at` | timestamp | Scan time |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer accessing out-of-scope station data |

---

## GET /v1/history/scans/{scan_id}/timeline

Full event timeline for a single scan (audit entries + stage transitions).

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/history/scans/{scan_id}/timeline` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `scan_id` | UUID | Must reference existing scan |

### Response DTO — `ScanTimelineResponse`

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan identifier |
| `correlation_id` | UUID | Pipeline trace ID |
| `events` | `TimelineEvent[]` | Ordered events |

#### TimelineEvent

| Field | Type | Description |
|-------|------|-------------|
| `sequence` | integer | Order in pipeline |
| `stage` | string | `ingestion`, `detection`, `ocr`, `lookup`, `verification`, `risk`, `decision`, `report` |
| `event_type` | string | Audit event code |
| `status` | enum | `success`, `failed`, `degraded` |
| `duration_ms` | integer | Stage duration (nullable) |
| `summary` | string | Human-readable summary |
| `occurred_at` | timestamp | Event time |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Scan not found |
| 403 | `AUTH_FORBIDDEN` | Scope violation |

---

## GET /v1/history/plate/{plate}/sightings

All historical sightings for a plate (clone detection support).

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/history/plate/{plate}/sightings` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `plate` | string | 1–16 chars; URL-encoded |

### Query Parameters

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | no | Default 30 days ago |
| `to` | timestamp | no | Default now |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `PlateSightingsResponse`

| Field | Type | Description |
|-------|------|-------------|
| `plate_text` | string | Normalized plate |
| `total_sightings` | integer | Count in range |
| `items` | `SightingItem[]` | Sighting list |
| `pagination` | object | Page metadata |

#### SightingItem

| Field | Type |
|-------|------|
| `scan_id` | UUID |
| `scanned_at` | timestamp |
| `location_label` | string |
| `latitude` | decimal |
| `longitude` | decimal |
| `officer_name` | string |
| `vehicle_id` | UUID |
| `decision` | enum |
| `risk_score` | decimal |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid plate format |
