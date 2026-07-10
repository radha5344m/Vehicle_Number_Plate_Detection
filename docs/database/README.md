# Database Design — SentinelANPR AI

**Version:** 0.1.0 (Foundation)  
**Status:** Design only — no migrations or SQL

---

## Design Principles

| Principle | Application |
|-----------|-------------|
| **Normalization** | Core entities in 3NF; denormalized read models deferred to analytics layer |
| **Clean Architecture** | ORM models live in `infrastructure/database/models/` only — never in domain |
| **Audit integrity** | `audit_logs` is append-only; no updates or deletes |
| **Extensibility** | UUID primary keys, nullable FKs where matching is async, metadata envelopes for evolution |
| **Indexing** | Optimize for scan lookup by plate, time range, officer, and alert triage |

---

## Documents

| File | Description |
|------|-------------|
| [schema-design.md](schema-design.md) | Full entity specifications |
| [entity-relationships.md](entity-relationships.md) | ER diagram and relationship cardinalities |

---

## Entity Summary

| Entity | Purpose |
|--------|---------|
| `officers` | Police officer identity and duty context |
| `vehicles` | Registered vehicle master records |
| `scan_history` | Immutable record of each ANPR scan event |
| `investigation_reports` | Generated PDF/formal investigation documents |
| `vehicle_alerts` | Actionable alerts from verification and risk engine |
| `audit_logs` | System-wide immutable audit trail |

### Supporting Entities (Normalized)

| Entity | Purpose |
|--------|---------|
| `stations` | Police station / checkpoint reference data |
| `verification_results` | 1:1 verification outcome per scan (normalized from scan) |
| `risk_assessments` | Risk engine output per scan (supports re-assessment) |

---

## Technology

Database engine _TBD via ADR_. Design is engine-agnostic (PostgreSQL recommended for JSONB and indexing).

---

## Related

- [Module Architecture](../architecture/modules.md)
- [History Module](../architecture/modules.md#12-history)
- `infrastructure/database/` in source tree
