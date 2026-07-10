# Vehicle Lookup API

Base path: `/v1/vehicles`

Read-only registry and local vehicle cache queries. Does not run the full scan pipeline.

---

## GET /v1/vehicles/lookup

Look up a vehicle by plate number.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/vehicles/lookup` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Query Parameters — `VehicleLookupQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `plate` | string | yes | 1–16 chars; normalized on server |
| `jurisdiction` | string | no | 2–8 char region code; default from officer station |
| `force_refresh` | boolean | no | Default `false`; bypass local cache |

### Request DTO

Query parameters only (no body).

### Response DTO — `VehicleLookupResponse`

| Field | Type | Description |
|-------|------|-------------|
| `lookup_status` | enum | `found`, `not_found`, `registry_unavailable` |
| `vehicle` | `VehicleRecord` | Present when `found` |
| `registry_synced_at` | timestamp | Cache freshness |
| `registry_external_id` | string | External RTO reference |

#### VehicleRecord

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_id` | UUID | Local record ID |
| `plate_number` | string | Normalized plate |
| `jurisdiction` | string | Region code |
| `make` | string | Manufacturer |
| `model` | string | Model |
| `color` | string | Primary color |
| `year` | integer | Manufacturing year |
| `vehicle_type` | enum | `car`, `motorcycle`, `truck`, `other` |
| `registration_status` | enum | `active`, `expired`, `suspended`, `stolen`, `unknown` |
| `registered_owner` | string | Privacy-filtered owner name |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Missing or invalid plate |
| 401 | `AUTH_INVALID` | Invalid token |
| 503 | `SERVICE_UNAVAILABLE` | Registry unreachable after retries |

---

## GET /v1/vehicles/{vehicle_id}

Retrieve a vehicle record by ID.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/vehicles/{vehicle_id}` |
| **Auth required** | Bearer token, role `officer` \| `supervisor` \| `admin` |

### Path Parameters

| Param | Type | Validation |
|-------|------|------------|
| `vehicle_id` | UUID | Valid UUID |

### Response DTO — `VehicleDetailResponse`

| Field | Type | Description |
|-------|------|-------------|
| `vehicle` | `VehicleRecord` | Full vehicle record |
| `scan_count` | integer | Total scans linked to this vehicle |
| `last_scanned_at` | timestamp | Most recent scan (nullable) |
| `active_alerts_count` | integer | Open alerts for this vehicle |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 404 | `NOT_FOUND` | Vehicle ID does not exist |

---

## GET /v1/vehicles

Search and list vehicles in local cache.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/vehicles` |
| **Auth required** | Bearer token, role `supervisor` \| `admin` |

### Query Parameters — `VehicleSearchQuery`

| Param | Type | Required | Validation |
|-------|------|----------|------------|
| `plate` | string | no | Partial plate match |
| `registration_status` | enum | no | Filter by status |
| `jurisdiction` | string | no | Region code |
| `make` | string | no | Partial make match |
| `page` | integer | no | Default 1 |
| `page_size` | integer | no | Default 20, max 100 |

### Response DTO — `VehicleListResponse`

| Field | Type | Description |
|-------|------|-------------|
| `items` | `VehicleRecord[]` | Matching vehicles |
| `pagination` | object | Page metadata |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 403 | `AUTH_FORBIDDEN` | Officer role not permitted |
