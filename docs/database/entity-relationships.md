# Entity-Relationship Model

Visual reference for SentinelANPR AI database design.

---

## Core ER Diagram

```mermaid
erDiagram
    STATIONS ||--o{ OFFICERS : "assigned to"
    OFFICERS ||--o{ SCAN_HISTORY : "performs"
    VEHICLES ||--o{ SCAN_HISTORY : "matched to"
    SCAN_HISTORY ||--|| VERIFICATION_RESULTS : "has"
    SCAN_HISTORY ||--o{ RISK_ASSESSMENTS : "assessed by"
    SCAN_HISTORY ||--o{ INVESTIGATION_REPORTS : "documented in"
    SCAN_HISTORY ||--o{ VEHICLE_ALERTS : "triggers"
    VEHICLES ||--o{ VEHICLE_ALERTS : "concerns"
    OFFICERS ||--o{ INVESTIGATION_REPORTS : "generates"
    OFFICERS ||--o{ VEHICLE_ALERTS : "acknowledges"
    OFFICERS ||--o{ AUDIT_LOGS : "acts as"
    SCAN_HISTORY ||--o{ AUDIT_LOGS : "referenced by"
    VEHICLES ||--o{ AUDIT_LOGS : "referenced by"
    INVESTIGATION_REPORTS ||--o{ AUDIT_LOGS : "referenced by"
    VEHICLE_ALERTS ||--o{ AUDIT_LOGS : "referenced by"

    STATIONS {
        uuid station_id PK
        string station_code UK
        string name
        string jurisdiction
    }

    OFFICERS {
        uuid officer_id PK
        uuid station_id FK
        string badge_number UK
        string rank
        string status
    }

    VEHICLES {
        uuid vehicle_id PK
        string plate_number UK
        string registration_status
        string jurisdiction
    }

    SCAN_HISTORY {
        uuid scan_id PK
        uuid officer_id FK
        uuid vehicle_id FK
        string normalized_plate_text
        timestamp scanned_at
        string processing_status
    }

    VERIFICATION_RESULTS {
        uuid verification_id PK
        uuid scan_id FK_UK
        string outcome_status
        timestamp verified_at
    }

    RISK_ASSESSMENTS {
        uuid assessment_id PK
        uuid scan_id FK
        decimal risk_score
        boolean clone_suspected
    }

    INVESTIGATION_REPORTS {
        uuid report_id PK
        uuid scan_id FK
        uuid officer_id FK
        string report_type
        string status
    }

    VEHICLE_ALERTS {
        uuid alert_id PK
        uuid scan_id FK
        uuid vehicle_id FK
        string alert_type
        string severity
        string status
    }

    AUDIT_LOGS {
        uuid audit_id PK
        string entity_type
        uuid entity_id
        uuid actor_officer_id FK
        timestamp occurred_at
    }
```

---

## Relationship Cardinalities

| Parent | Child | Cardinality | FK Location | On Delete |
|--------|-------|-------------|-------------|-----------|
| `stations` | `officers` | 1 : N | `officers.station_id` | RESTRICT |
| `officers` | `scan_history` | 1 : N | `scan_history.officer_id` | RESTRICT |
| `vehicles` | `scan_history` | 1 : N | `scan_history.vehicle_id` | SET NULL |
| `scan_history` | `verification_results` | 1 : 1 | `verification_results.scan_id` | CASCADE |
| `scan_history` | `risk_assessments` | 1 : N | `risk_assessments.scan_id` | CASCADE |
| `scan_history` | `investigation_reports` | 1 : N | `investigation_reports.scan_id` | RESTRICT |
| `scan_history` | `vehicle_alerts` | 1 : N | `vehicle_alerts.scan_id` | RESTRICT |
| `vehicles` | `vehicle_alerts` | 1 : N | `vehicle_alerts.vehicle_id` | SET NULL |
| `officers` | `investigation_reports` | 1 : N | `investigation_reports.officer_id` | RESTRICT |
| `officers` | `vehicle_alerts` | 1 : N | `vehicle_alerts.acknowledged_by_officer_id` | SET NULL |
| `officers` | `audit_logs` | 1 : N | `audit_logs.actor_officer_id` | SET NULL |

---

## Polymorphic References

`audit_logs` uses a **polymorphic association** (not enforced by a single FK):

| Field | Purpose |
|-------|---------|
| `entity_type` | Table name discriminator: `officer`, `vehicle`, `scan`, `report`, `alert` |
| `entity_id` | UUID of the referenced row |

Application layer validates entity existence. Future option: separate junction tables per entity type if strict FK enforcement is required.

---

## Data Flow (Write Path)

```
Scan created (scan_history)
    → Verification written (verification_results)
    → Risk assessed (risk_assessments)
    → Alert raised if needed (vehicle_alerts)
    → Report generated on demand (investigation_reports)
    → Every step appends audit_logs
```

---

## Related

- [Schema Design](schema-design.md)
