# Schema Design — SentinelANPR AI

Complete database design for core and supporting entities. **No SQL — design specification only.**

---

## Conventions

| Convention | Choice | Rationale |
|------------|--------|-----------|
| Primary keys | `UUID` (`*_id`) | Globally unique; safe across services and sharding |
| Timestamps | `TIMESTAMP WITH TIME ZONE` | UTC storage; display in local TZ at application layer |
| Soft delete | `deleted_at` nullable on mutable tables | Preserve referential history; exclude from active queries |
| Status fields | `VARCHAR` + application enum | Avoid DB enum migration pain; validate in domain |
| Metadata | `JSON` document column | Forward-compatible extension without schema churn |
| Naming | `snake_case`, plural table names | Consistency with Python/SQLAlchemy infrastructure layer |

---

## 1. officers

### Description

Stores police officer identity and duty assignment. Used to attribute scans, reports, and audit actions. Authentication credentials are **not** stored here (→ Authentication module / identity provider).

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `officer_id` | UUID | NO | Primary key |
| `station_id` | UUID | NO | FK → `stations.station_id` |
| `badge_number` | VARCHAR(32) | NO | Unique badge identifier |
| `first_name` | VARCHAR(100) | NO | Given name |
| `last_name` | VARCHAR(100) | NO | Family name |
| `rank` | VARCHAR(64) | NO | e.g. Constable, SI, Inspector |
| `email` | VARCHAR(255) | YES | Contact email |
| `phone` | VARCHAR(20) | YES | Contact phone |
| `status` | VARCHAR(32) | NO | `active`, `inactive`, `suspended` |
| `metadata` | JSON | YES | Extensible attributes (photo ref, badge issue date) |
| `created_at` | TIMESTAMPTZ | NO | Record creation |
| `updated_at` | TIMESTAMPTZ | NO | Last modification |
| `deleted_at` | TIMESTAMPTZ | YES | Soft delete marker |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `officer_id` |
| **Unique** | `badge_number` (among non-deleted rows) |
| **Foreign Key** | `station_id` → `stations.station_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_officers_station_id` | `station_id` | Filter officers by station |
| `idx_officers_status` | `status` | Active officer lookups |
| `idx_officers_name` | `last_name`, `first_name` | Search by name |
| `uq_officers_badge_active` | `badge_number` WHERE `deleted_at IS NULL` | Partial unique (engine-specific) |

---

## 2. vehicles

### Description

Authoritative local cache of registered vehicle master data synced from external registry (RTO). Source of truth for verification comparisons.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `vehicle_id` | UUID | NO | Primary key |
| `plate_number` | VARCHAR(16) | NO | Normalized plate (unique per jurisdiction) |
| `jurisdiction` | VARCHAR(8) | NO | State/region code (e.g. `AP`, `TS`) |
| `make` | VARCHAR(64) | YES | Manufacturer |
| `model` | VARCHAR(64) | YES | Model name |
| `color` | VARCHAR(32) | YES | Primary color |
| `year` | SMALLINT | YES | Manufacturing year |
| `vehicle_type` | VARCHAR(32) | YES | `car`, `motorcycle`, `truck`, `other` |
| `registration_status` | VARCHAR(32) | NO | `active`, `expired`, `suspended`, `stolen`, `unknown` |
| `registered_owner` | VARCHAR(200) | YES | Owner name (privacy-filtered at API layer) |
| `registry_external_id` | VARCHAR(64) | YES | ID in external RTO system |
| `registry_synced_at` | TIMESTAMPTZ | YES | Last sync from registry |
| `metadata` | JSON | YES | Extended registry fields |
| `created_at` | TIMESTAMPTZ | NO | Record creation |
| `updated_at` | TIMESTAMPTZ | NO | Last modification |
| `deleted_at` | TIMESTAMPTZ | YES | Soft delete marker |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `vehicle_id` |
| **Unique** | `(plate_number, jurisdiction)` among non-deleted |
| **Foreign Key** | — |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_vehicles_plate` | `plate_number` | Fast plate lookup |
| `idx_vehicles_jurisdiction` | `jurisdiction` | Filter by region |
| `idx_vehicles_status` | `registration_status` | Stolen/expired queries |
| `idx_vehicles_registry_sync` | `registry_synced_at` | Stale cache refresh jobs |
| `uq_vehicles_plate_jurisdiction` | `plate_number`, `jurisdiction` WHERE `deleted_at IS NULL` | Composite unique |

---

## 3. scan_history

### Description

Central fact table for every ANPR scan event. Records who scanned, what was detected, when and where, and processing lifecycle. Verification and risk details are **normalized** into child tables to avoid wide-row updates and support re-assessment.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `scan_id` | UUID | NO | Primary key |
| `officer_id` | UUID | NO | FK → `officers.officer_id` |
| `vehicle_id` | UUID | YES | FK → `vehicles.vehicle_id`; null until matched |
| `detected_plate_text` | VARCHAR(16) | YES | Raw OCR output |
| `normalized_plate_text` | VARCHAR(16) | YES | Domain-normalized plate |
| `ocr_confidence` | DECIMAL(5,4) | YES | 0.0000–1.0000 |
| `detection_confidence` | DECIMAL(5,4) | YES | YOLO confidence |
| `processing_status` | VARCHAR(32) | NO | `received`, `detecting`, `recognizing`, `completed`, `failed` |
| `failure_reason` | VARCHAR(255) | YES | Populated when `failed` |
| `image_storage_key` | VARCHAR(512) | YES | Object store key for full image |
| `crop_storage_key` | VARCHAR(512) | YES | Object store key for plate crop |
| `latitude` | DECIMAL(10,7) | YES | GPS latitude |
| `longitude` | DECIMAL(10,7) | YES | GPS longitude |
| `location_label` | VARCHAR(200) | YES | Human-readable location |
| `camera_id` | VARCHAR(64) | YES | Source camera/device ID |
| `ml_model_version` | VARCHAR(32) | YES | Detector + OCR model version tag |
| `correlation_id` | UUID | NO | Trace ID across pipeline |
| `scanned_at` | TIMESTAMPTZ | NO | Capture timestamp |
| `completed_at` | TIMESTAMPTZ | YES | Pipeline completion time |
| `metadata` | JSON | YES | Device info, exposure, lane ID, etc. |
| `created_at` | TIMESTAMPTZ | NO | Record insertion (immutable) |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `scan_id` |
| **Foreign Key** | `officer_id` → `officers.officer_id` |
| **Foreign Key** | `vehicle_id` → `vehicles.vehicle_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_scan_officer_id` | `officer_id` | Officer scan history |
| `idx_scan_vehicle_id` | `vehicle_id` | Vehicle sighting history |
| `idx_scan_normalized_plate` | `normalized_plate_text` | Clone detection correlation |
| `idx_scan_scanned_at` | `scanned_at DESC` | Time-range queries |
| `idx_scan_officer_scanned` | `officer_id`, `scanned_at DESC` | Officer dashboard |
| `idx_scan_plate_scanned` | `normalized_plate_text`, `scanned_at DESC` | Plate timeline |
| `idx_scan_correlation_id` | `correlation_id` | Distributed tracing |
| `idx_scan_processing_status` | `processing_status` | Pipeline monitoring |
| `idx_scan_location` | `latitude`, `longitude` | Geo queries (consider PostGIS later) |

### Notes

- **No `updated_at`** — scans are immutable after completion; corrections create new scan records + audit entry
- `vehicle_id` nullable: plate may not match any registry record at scan time

---

## 4. verification_results

### Description

Normalized 1:1 verification outcome per scan. Separated from `scan_history` so verification can be retried or updated without mutating the scan fact row.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `verification_id` | UUID | NO | Primary key |
| `scan_id` | UUID | NO | FK → `scan_history.scan_id` (unique) |
| `outcome_status` | VARCHAR(32) | NO | `valid`, `invalid`, `unknown`, `expired` |
| `vehicle_id` | UUID | YES | FK → matched `vehicles.vehicle_id` |
| `mismatch_reasons` | JSON | YES | Array of reason codes/messages |
| `verified_at` | TIMESTAMPTZ | NO | Verification timestamp |
| `registry_response_ref` | VARCHAR(64) | YES | External registry transaction ref |
| `metadata` | JSON | YES | Full comparison snapshot (privacy-controlled) |
| `created_at` | TIMESTAMPTZ | NO | Record creation |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `verification_id` |
| **Unique** | `scan_id` |
| **Foreign Key** | `scan_id` → `scan_history.scan_id` |
| **Foreign Key** | `vehicle_id` → `vehicles.vehicle_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_verification_scan_id` | `scan_id` | Join to scan |
| `idx_verification_outcome` | `outcome_status` | Failure rate analytics |
| `idx_verification_verified_at` | `verified_at DESC` | Time-series queries |

---

## 5. risk_assessments

### Description

Risk Engine output per scan. Supports **multiple assessments** per scan (re-evaluation when new sightings arrive).

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `assessment_id` | UUID | NO | Primary key |
| `scan_id` | UUID | NO | FK → `scan_history.scan_id` |
| `risk_score` | DECIMAL(5,4) | NO | 0.0000–1.0000 |
| `clone_suspected` | BOOLEAN | NO | Threshold breach flag |
| `signals` | JSON | NO | Explainability payload (signal name, weight, detail) |
| `policy_version` | VARCHAR(32) | NO | Risk policy version used |
| `assessed_at` | TIMESTAMPTZ | NO | Assessment timestamp |
| `metadata` | JSON | YES | Correlated scan IDs, model version |
| `created_at` | TIMESTAMPTZ | NO | Record creation |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `assessment_id` |
| **Foreign Key** | `scan_id` → `scan_history.scan_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_risk_scan_id` | `scan_id` | Latest assessment per scan |
| `idx_risk_clone_suspected` | `clone_suspected`, `assessed_at DESC` | Flagged scan triage |
| `idx_risk_score` | `risk_score DESC` | High-risk ordering |
| `idx_risk_assessed_at` | `assessed_at DESC` | Analytics time series |

---

## 6. investigation_reports

### Description

Formal investigation documents (PDF) generated from scan, verification, and risk data. Multiple reports per scan allowed (e.g. field summary vs. full investigation).

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `report_id` | UUID | NO | Primary key |
| `scan_id` | UUID | NO | FK → `scan_history.scan_id` |
| `officer_id` | UUID | NO | FK → generating officer |
| `report_type` | VARCHAR(64) | NO | `field_summary`, `full_investigation`, `incident` |
| `title` | VARCHAR(255) | NO | Report title |
| `template_version` | VARCHAR(16) | NO | PDF template version |
| `status` | VARCHAR(32) | NO | `draft`, `generated`, `archived`, `superseded` |
| `storage_key` | VARCHAR(512) | YES | Object store path to PDF |
| `file_size_bytes` | BIGINT | YES | PDF size |
| `checksum_sha256` | CHAR(64) | YES | File integrity |
| `generated_at` | TIMESTAMPTZ | YES | When PDF was produced |
| `metadata` | JSON | YES | Included sections, redaction flags |
| `created_at` | TIMESTAMPTZ | NO | Record creation |
| `updated_at` | TIMESTAMPTZ | NO | Status changes |
| `deleted_at` | TIMESTAMPTZ | YES | Soft delete |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `report_id` |
| **Foreign Key** | `scan_id` → `scan_history.scan_id` |
| **Foreign Key** | `officer_id` → `officers.officer_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_reports_scan_id` | `scan_id` | Reports for a scan |
| `idx_reports_officer_id` | `officer_id` | Officer-generated reports |
| `idx_reports_status` | `status` | Workflow filtering |
| `idx_reports_generated_at` | `generated_at DESC` | Recent reports list |
| `idx_reports_type` | `report_type` | Filter by report kind |

---

## 7. vehicle_alerts

### Description

Actionable alerts raised by verification failures, risk engine, or stolen vehicle matches. Supports officer acknowledgment and resolution workflow.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `alert_id` | UUID | NO | Primary key |
| `scan_id` | UUID | NO | FK → triggering scan |
| `vehicle_id` | UUID | YES | FK → concerned vehicle |
| `alert_type` | VARCHAR(64) | NO | `clone_suspected`, `verification_failed`, `stolen_vehicle`, `expired_registration` |
| `severity` | VARCHAR(16) | NO | `low`, `medium`, `high`, `critical` |
| `risk_score` | DECIMAL(5,4) | YES | Score at alert time |
| `status` | VARCHAR(32) | NO | `open`, `acknowledged`, `resolved`, `dismissed` |
| `summary` | VARCHAR(500) | NO | Human-readable alert summary |
| `acknowledged_by_officer_id` | UUID | YES | FK → acknowledging officer |
| `acknowledged_at` | TIMESTAMPTZ | YES | Acknowledgment time |
| `resolved_at` | TIMESTAMPTZ | YES | Resolution time |
| `resolution_notes` | TEXT | YES | Officer resolution comments |
| `metadata` | JSON | YES | Signal snapshot, notification refs |
| `created_at` | TIMESTAMPTZ | NO | Alert creation |
| `updated_at` | TIMESTAMPTZ | NO | Status updates |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `alert_id` |
| **Foreign Key** | `scan_id` → `scan_history.scan_id` |
| **Foreign Key** | `vehicle_id` → `vehicles.vehicle_id` |
| **Foreign Key** | `acknowledged_by_officer_id` → `officers.officer_id` |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_alerts_scan_id` | `scan_id` | Alerts for a scan |
| `idx_alerts_vehicle_id` | `vehicle_id` | Vehicle alert history |
| `idx_alerts_status_severity` | `status`, `severity`, `created_at DESC` | Triage queue |
| `idx_alerts_type` | `alert_type` | Filter by alert kind |
| `idx_alerts_open` | `created_at DESC` WHERE `status = 'open'` | Dashboard open alerts |
| `idx_alerts_officer_ack` | `acknowledged_by_officer_id` | Officer workload |

---

## 8. audit_logs

### Description

Append-only system audit trail. Records all significant mutations and business events. **Never updated or deleted** — retention managed by archival policy.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `audit_id` | UUID | NO | Primary key |
| `event_type` | VARCHAR(64) | NO | `scan.created`, `verification.completed`, `alert.raised`, etc. |
| `entity_type` | VARCHAR(32) | NO | `officer`, `vehicle`, `scan`, `report`, `alert`, `verification`, `risk` |
| `entity_id` | UUID | NO | Polymorphic reference to entity PK |
| `actor_officer_id` | UUID | YES | FK → officer who performed action; null for system |
| `action` | VARCHAR(32) | NO | `create`, `update`, `delete`, `verify`, `assess`, `acknowledge`, `generate` |
| `payload` | JSON | YES | Event detail (diff, before/after summary) |
| `ip_address` | INET | YES | Client IP if applicable |
| `user_agent` | VARCHAR(512) | YES | Client user agent |
| `correlation_id` | UUID | YES | Pipeline trace ID |
| `occurred_at` | TIMESTAMPTZ | NO | When event happened |
| `created_at` | TIMESTAMPTZ | NO | When log was written (≈ `occurred_at`) |

### Keys

| Key | Columns |
|-----|---------|
| **Primary Key** | `audit_id` |
| **Foreign Key** | `actor_officer_id` → `officers.officer_id` (nullable) |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `idx_audit_entity` | `entity_type`, `entity_id` | Audit trail per entity |
| `idx_audit_actor` | `actor_officer_id` | Officer action history |
| `idx_audit_occurred_at` | `occurred_at DESC` | Time-range audit queries |
| `idx_audit_event_type` | `event_type` | Filter by event |
| `idx_audit_correlation_id` | `correlation_id` | End-to-end trace |
| `idx_audit_entity_occurred` | `entity_type`, `entity_id`, `occurred_at DESC` | Entity timeline |

### Partitioning (Future)

Partition by `occurred_at` monthly for retention and query performance at scale.

---

## 9. stations (Supporting — Normalized)

### Description

Reference table for police stations and checkpoints. Normalizes officer assignment.

### Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `station_id` | UUID | NO | Primary key |
| `station_code` | VARCHAR(16) | NO | Unique short code |
| `name` | VARCHAR(200) | NO | Station name |
| `jurisdiction` | VARCHAR(8) | NO | State/region |
| `address` | TEXT | YES | Physical address |
| `metadata` | JSON | YES | Contact, geo boundary |
| `created_at` | TIMESTAMPTZ | NO | Record creation |
| `updated_at` | TIMESTAMPTZ | NO | Last modification |

### Keys & Indexes

| Key / Index | Columns |
|-------------|---------|
| **PK** | `station_id` |
| **UK** | `station_code` |
| `idx_stations_jurisdiction` | `jurisdiction` |

---

## Relationship Summary

```
stations (1) ──< (N) officers
officers (1) ──< (N) scan_history
vehicles (1) ──< (N) scan_history          [optional FK]
scan_history (1) ── (1) verification_results
scan_history (1) ──< (N) risk_assessments
scan_history (1) ──< (N) investigation_reports
scan_history (1) ──< (N) vehicle_alerts
vehicles (1) ──< (N) vehicle_alerts        [optional FK]
officers (1) ──< (N) investigation_reports
officers (1) ──< (N) vehicle_alerts        [acknowledgment]
officers (1) ──< (N) audit_logs             [actor, optional]

audit_logs ──> (polymorphic) officers | vehicles | scan_history | investigation_reports | vehicle_alerts
```

---

## Normalization Decisions

| Decision | Rationale |
|----------|-----------|
| `verification_results` separate from `scan_history` | Avoid updating immutable scan facts; support verification retry |
| `risk_assessments` separate from `scan_history` | Multiple re-assessments as new sightings arrive |
| `stations` separate from `officers` | Reuse station reference; avoid duplicated station strings |
| `mismatch_reasons` and `signals` as JSON | Variable-length structured data; schema-stable |
| No officer credentials in `officers` | Authentication is a separate concern (identity provider) |
| Polymorphic `audit_logs.entity_*` | Single append-only log table; avoids 6+ audit child tables |

### Intentional Denormalization (Acceptable)

| Location | Field | Why |
|----------|-------|-----|
| `scan_history` | `normalized_plate_text` | Fast correlation without joining verification |
| `vehicle_alerts` | `risk_score` | Point-in-time snapshot at alert creation |
| `risk_assessments` | `signals` JSON | Explainability bundle stored atomically |

---

## Future Extensibility

### Phase 2 Tables (Planned)

| Table | Module | Purpose |
|-------|--------|---------|
| `notification_deliveries` | Notification | SMS/email/push delivery tracking |
| `scan_images` | Vehicle Scan | Multiple images per scan (burst mode) |
| `plate_sightings` | Risk Engine | Denormalized sighting index for fast correlation |
| `registry_sync_log` | Vehicle | External registry sync audit |
| `feature_flags` | Configuration | Runtime toggles |
| `api_keys` | Authentication | Service-to-service credentials |

### Extension Patterns

| Pattern | Application |
|---------|-------------|
| **`metadata` JSON column** | Add fields without migration; domain validates known keys |
| **UUID primary keys** | Merge databases, federated IDs, event sourcing ready |
| **`policy_version` / `template_version`** | Reproduce historical decisions with correct rule version |
| **`correlation_id` on scans and audits** | OpenTelemetry / distributed tracing integration |
| **Soft deletes** | `officers`, `vehicles`, `investigation_reports` — hard delete only via archival job |
| **Read replicas** | `scan_history` + `audit_logs` feed Analytics module without touching primary |
| **Multi-tenancy hook** | Add `organization_id` or `tenant_id` to all tables when expanding beyond single jurisdiction |
| **PostGIS** | Replace `latitude`/`longitude` indexes with spatial index for geo-fencing |
| **Event sourcing** | `audit_logs.payload` becomes event store; projections rebuild read models |
| **Partitioning** | `scan_history` by `scanned_at` month; `audit_logs` by `occurred_at` month |

### Module-to-Table Mapping

| Module | Primary Tables |
|--------|----------------|
| Officer | `officers`, `stations` |
| Vehicle | `vehicles` |
| Vehicle Scan | `scan_history` |
| Vehicle Verification | `verification_results` |
| Risk Engine | `risk_assessments`, `vehicle_alerts` |
| Reports | `investigation_reports` |
| History / Audit | `audit_logs` |
| Dashboard | Reads `scan_history`, `vehicle_alerts`, aggregates |
| Analytics | Reads all fact tables; future materialized views |

---

## Data Integrity Rules (Application-Enforced)

| Rule | Enforcement |
|------|-------------|
| `scan_history` immutable after `completed` | Application + DB trigger _optional_ |
| `audit_logs` append-only | No UPDATE/DELETE grants on application role |
| `verification_results.scan_id` unique | One active verification per scan |
| `vehicle_alerts.status` transitions | `open` → `acknowledged` → `resolved` \| `dismissed` |
| Plate normalization | Domain `PlateNumber` VO before insert |

---

## Related

- [Entity Relationships](entity-relationships.md)
- [Module Architecture](../architecture/modules.md)
