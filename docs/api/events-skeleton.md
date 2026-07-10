# Event Schema Skeleton

Async messaging contracts for SentinelANPR AI.

**Status:** Skeleton — broker and serialization format TBD via ADR.

---

## Planned Topics / Queues

| Event | Producer | Consumer(s) |
|-------|----------|---------------|
| `PlateRecognized` | Recognition pipeline | Verification, persistence |
| `PlateVerified` | Verification use case | Clone detection, audit |
| `CloneSuspected` | Clone detection | Alerting |
| `AlertRaised` | Alerting | External notification systems |

---

## PlateRecognized (placeholder)

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Unique event ID |
| `occurred_at` | string | ISO-8601 |
| `plate_text` | string | Normalized |
| `confidence` | number | |
| `source_id` | string | |
| `sighting_id` | string | |

---

## CloneSuspected (placeholder)

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | |
| `plate_text` | string | |
| `risk_score` | number | |
| `correlated_sighting_ids` | array | |

---

## Infrastructure

Implementations: `src/sentinel_anpr/infrastructure/messaging/`
