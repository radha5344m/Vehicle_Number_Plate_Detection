# Authentication API

Base path: `/v1/auth`

---

## POST /v1/auth/login

Authenticate an officer and receive tokens.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/auth/login` |
| **Auth required** | None (public) |

### Request DTO — `LoginRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `badge_number` | string | yes | 1–32 chars, alphanumeric |
| `password` | string | yes | 8–128 chars |
| `station_code` | string | no | Valid station code if provided |

### Response DTO — `LoginResponse`

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `refresh_token` | string | JWT refresh token |
| `token_type` | string | Always `Bearer` |
| `expires_in` | integer | Access token TTL in seconds |
| `officer` | `OfficerSummary` | Authenticated officer profile |

#### OfficerSummary

| Field | Type |
|-------|------|
| `officer_id` | UUID |
| `badge_number` | string |
| `first_name` | string |
| `last_name` | string |
| `rank` | string |
| `station_id` | UUID |
| `station_code` | string |
| `roles` | string[] |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Missing/invalid fields |
| 401 | `AUTH_INVALID` | Wrong badge or password |
| 403 | `AUTH_FORBIDDEN` | Officer suspended/inactive |
| 429 | `RATE_LIMITED` | Brute-force protection |

---

## POST /v1/auth/refresh

Exchange refresh token for new access token.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/auth/refresh` |
| **Auth required** | None (refresh token in body) |

### Request DTO — `RefreshTokenRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `refresh_token` | string | yes | Valid non-expired refresh token |

### Response DTO — `RefreshTokenResponse`

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | New JWT access token |
| `token_type` | string | `Bearer` |
| `expires_in` | integer | TTL in seconds |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Missing refresh_token |
| 401 | `AUTH_INVALID` | Expired or revoked refresh token |

---

## POST /v1/auth/logout

Revoke refresh token and end session.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/auth/logout` |
| **Auth required** | Bearer access token |

### Request DTO — `LogoutRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `refresh_token` | string | yes | Token to revoke |

### Response DTO — `LogoutResponse`

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | `Logged out successfully` |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 401 | `AUTH_MISSING` | No token |
| 401 | `AUTH_INVALID` | Invalid access token |

---

## GET /v1/auth/me

Return current authenticated officer profile.

| Attribute | Value |
|-----------|-------|
| **Method** | `GET` |
| **Route** | `/v1/auth/me` |
| **Auth required** | Bearer access token |

### Request DTO

None.

### Response DTO — `MeResponse`

| Field | Type | Description |
|-------|------|-------------|
| `officer` | `OfficerSummary` | Current officer |
| `permissions` | string[] | Resolved permission codes |
| `session_id` | UUID | Active session identifier |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 401 | `AUTH_MISSING` | No token |
| 401 | `AUTH_INVALID` | Expired token |

---

## POST /v1/auth/api-keys (Admin)

Issue service API key for system integrations.

| Attribute | Value |
|-----------|-------|
| **Method** | `POST` |
| **Route** | `/v1/auth/api-keys` |
| **Auth required** | Bearer token, role `admin` |

### Request DTO — `CreateApiKeyRequest`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | string | yes | 3–64 chars |
| `scopes` | string[] | yes | Subset of allowed scopes |
| `expires_at` | timestamp | no | Future date |

### Response DTO — `CreateApiKeyResponse`

| Field | Type | Description |
|-------|------|-------------|
| `api_key_id` | UUID | Key identifier |
| `api_key` | string | **Shown once** — secret key |
| `name` | string | Key label |
| `scopes` | string[] | Granted scopes |
| `expires_at` | timestamp | Expiry (nullable) |

### Error Responses

| HTTP | Code | Condition |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Invalid scopes |
| 403 | `AUTH_FORBIDDEN` | Not admin |
