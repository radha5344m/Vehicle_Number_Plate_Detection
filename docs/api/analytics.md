# Analytics API

Base path: `/v1/analytics`

Historical trends and statistical insights. Read-only. Supervisor and admin access.

---

## GET /v1/analytics/scan-volume

Scan volume time series over a date range.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/analytics/scan-volume` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `ScanVolumeQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | yes | Range start |
| `to` | timestamp | yes | Range end; max 365 days span |
| `group_by` | enum | no | `hour`, `day`, `week`, `month`; default `day` |
| `station_id` | UUID | no | Filter by station |
| `officer_id` | UUID | no | Filter by officer |

### Response DTO — `AnalyticsTimeSeriesResponse`

| Field | Type | Description |
|-------|------|-------------|
| `metric` | string | `scan_volume` |
| `group_by` | enum | Aggregation period |
| `from` | timestamp | Range start |
| `to` | timestamp | Range end |
| `labels` | string[] | Time bucket labels |
| `values` | integer[] | Scan counts per bucket |
| `total` | integer | Sum across range |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Missing dates, range too large, invalid group_by |
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |

---

## GET /v1/analytics/verification-failures

Verification failure rate time series.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/analytics/verification-failures` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `VerificationFailuresQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | yes | Range start |
| `to` | timestamp | yes | Range end; max 365 days |
| `group_by` | enum | no | `day`, `week`, `month`; default `day` |
| `station_id` | UUID | no | Station filter |
| `outcome_status` | enum | no | Filter specific outcome |

### Response DTO — `AnalyticsTimeSeriesResponse`

| Field | Type | Description |
|-------|------|-------------|
| `metric` | string | `verification_failures` |
| `group_by` | enum | Aggregation period |
| `from` | timestamp | Range start |
| `to` | timestamp | Range end |
| `labels` | string[] | Time buckets |
| `values` | integer[] | Failure counts |
| `rates` | decimal[] | Failure rate 0.0–1.0 per bucket |
| `total_failures` | integer | Sum of failures |
| `total_verifications` | integer | Total verifications in range |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid range |
| 403 | `AUTH_FORBIDDEN` | Insufficient role |

---

## GET /v1/analytics/clone-detection-rate

Clone detection rate over time.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/analytics/clone-detection-rate` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `CloneDetectionQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | yes | Range start |
| `to` | timestamp | yes | Range end |
| `group_by` | enum | no | `day`, `week`, `month` |
| `station_id` | UUID | no | Station filter |

### Response DTO — `AnalyticsTimeSeriesResponse`

| Field | Type | Description |
|-------|------|-------------|
| `metric` | string | `clone_detection_rate` |
| `labels` | string[] | Time buckets |
| `values` | integer[] | Clones flagged per bucket |
| `rates` | decimal[] | Rate per bucket |
| `total_flagged` | integer | Total clone flags |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid parameters |
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |

---

## GET /v1/analytics/risk-distribution

Distribution of risk scores across scans in a range.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/analytics/risk-distribution` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `RiskDistributionQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | yes | Range start |
| `to` | timestamp | yes | Range end |
| `station_id` | UUID | no | Station filter |
| `buckets` | integer | no | Histogram buckets; default 10, max 20 |

### Response DTO — `RiskDistributionResponse`

| Field | Type | Description |
|-------|------|-------------|
| `from` | timestamp | Range start |
| `to` | timestamp | Range end |
| `total_scans` | integer | Scans with risk assessment |
| `buckets` | `RiskBucket[]` | Histogram |
| `mean_score` | decimal | Average risk score |
| `median_score` | decimal | Median risk score |
| `p95_score` | decimal | 95th percentile |

#### RiskBucket

| Field | Type | Description |
|-------|------|-------------|
| `range_start` | decimal | Bucket lower bound |
| `range_end` | decimal | Bucket upper bound |
| `count` | integer | Scans in bucket |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid range or buckets |
| 403 | `AUTH_FORBIDDEN` | Insufficient role |

---

## GET /v1/analytics/decision-breakdown

Pipeline decision distribution.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/analytics/decision-breakdown` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `DecisionBreakdownQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `from` | timestamp | yes | Range start |
| `to` | timestamp | yes | Range end |
| `station_id` | UUID | no | Station filter |

### Response DTO — `DecisionBreakdownResponse`

| Field | Type | Description |
|-------|------|-------------|
| `from` | timestamp | Range start |
| `to` | timestamp | Range end |
| `total` | integer | Total decisions |
| `breakdown` | object | `{ clear, monitor, investigate, detain, escalate }` counts |
| `percentages` | object | Same keys as percentages 0.0–100.0 |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |
