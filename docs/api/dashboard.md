# Dashboard API

Base path: `/v1/dashboard`

Real-time operational summaries for officers and supervisors.

---

## GET /v1/dashboard/summary

Operational counters for the authenticated officer's scope.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/dashboard/summary` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `DashboardSummaryQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `station_id` | UUID | no | Required for supervisor/admin; defaults to officer's station |
| `date` | date | no | ISO date; default today (UTC) |

### Request DTO

Query parameters only.

### Response DTO — `DashboardSummaryResponse`

| Field | Type | Description |
|-------|------|-------------|
| `station_id` | UUID | Scope station |
| `station_name` | string | Station display name |
| `date` | date | Summary date |
| `scans_today` | integer | Total scans in scope |
| `scans_completed` | integer | Successfully completed |
| `scans_failed` | integer | Failed scans |
| `verifications_failed` | integer | Invalid/expired/not_found count |
| `clones_flagged` | integer | Clone-suspected count |
| `alerts_open` | integer | Unresolved alerts |
| `decisions` | object | `{ clear, monitor, investigate, detain, escalate }` counts |
| `last_updated_at` | timestamp | Data freshness |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid date |
| 403 | `AUTH_FORBIDDEN` | Officer accessing another station |

---

## GET /v1/dashboard/recent-flags

Recent high-priority flagged scans for triage.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/dashboard/recent-flags` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `RecentFlagsQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `station_id` | UUID | no | Scope; default officer station |
| `limit` | integer | no | Default 10, max 50 |
| `min_risk_score` | decimal | no | 0.0–1.0; default 0.5 |

### Response DTO — `RecentFlagsResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `FlaggedScanItem[]` | Flagged scans, newest first |

#### FlaggedScanItem

| Field | Type | Description |
|-------|------|-------------|
| `scan_id` | UUID | Scan identifier |
| `plate_text` | string | Normalized plate |
| `risk_score` | decimal | Risk score |
| `clone_suspected` | boolean | Clone flag |
| `decision` | enum | Pipeline decision |
| `outcome_status` | enum | Verification outcome |
| `officer_id` | UUID | Scanning officer |
| `officer_name` | string | Officer display name |
| `location_label` | string | Scan location |
| `alert_id` | UUID | Linked alert (nullable) |
| `alert_status` | enum | Alert status (nullable) |
| `scanned_at` | timestamp | Scan time |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid limit or risk score |
| 403 | `AUTH_FORBIDDEN` | Scope violation |

---

## GET /v1/dashboard/alerts

Open alert queue for dashboard triage.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/dashboard/alerts` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `DashboardAlertsQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `station_id` | UUID | no | Scope filter |
| `status` | enum | no | `open`, `acknowledged`; default `open` |
| `severity` | enum | no | `low`, `medium`, `high`, `critical` |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 50 |

### Response DTO — `DashboardAlertsResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `AlertSummary[]` | Alert items |
| `pagination` | object | Page metadata |

#### AlertSummary

| Field | Type |
|-------|------|
| `alert_id` | UUID |
| `scan_id` | UUID |
| `plate_text` | string |
| `alert_type` | enum |
| `severity` | enum |
| `status` | enum |
| `risk_score` | decimal |
| `summary` | string |
| `created_at` | timestamp |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Insufficient role or scope |

---

## PATCH /v1/dashboard/alerts/{alert_id}/acknowledge

Acknowledge an open alert.

| Attribute | Value |
|-----------|-------|
| **Method** | `PATCH` |
| **Route** | `/v1/dashboard/alerts/{alert_id}/acknowledge` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `alert_id` | UUID | Must be `open` status |

### Request DTO — `AcknowledgeAlertRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `notes` | string | no | Max 500 chars |

### Response DTO — `AlertDetailResponse`

| Field | Type | Description |
|-------|------|-------------|
| `alert_id` | UUID | Alert ID |
| `status` | enum | `acknowledged` |
| `acknowledged_by_officer_id` | UUID | Acting officer |
| `acknowledged_at` | timestamp | Acknowledgment time |
| `notes` | string | Officer notes |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Alert not found |
| 422 | `UNPROCESSABLE` | Alert not in `open` state |
