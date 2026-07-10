# Bounded Contexts

Domain-Driven Design bounded contexts for SentinelANPR AI.

---

## Context Map

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Ingestion     │────▶│ Plate Recognition │────▶│ Plate Verification│
│  (images/meta)  │     │  (ANPR/OCR)       │     │  (registry)      │
└─────────────────┘     └────────┬─────────┘     └────────┬────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌────────────────────────────────────┐
                        │         Clone Detection            │
                        │  (correlation, fraud scoring)      │
                        └────────────────┬───────────────────┘
                                         │
                                         ▼
                        ┌────────────────────────────────────┐
                        │            Alerting                │
                        │  (notifications, audit)          │
                        └────────────────────────────────────┘

        ┌──────────────────────────────────────────┐
        │              Common (Shared Kernel)       │
        │  IDs, base errors, PlateNumber VO, etc.   │
        └──────────────────────────────────────────┘
```

---

## Context Descriptions

### Ingestion (`domain/ingestion/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Accept and validate incoming media and metadata |
| Ubiquitous Language | Capture, Frame, Stream, Source, Timestamp |
| Upstream | Cameras, uploads, API clients |
| Downstream | Plate Recognition |

### Plate Recognition (`domain/plate_recognition/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Detect plate region and extract alphanumeric text |
| Ubiquitous Language | Detection, Recognition, Confidence, Normalization |
| Collaborators | ML outbound ports (detector, recognizer) |
| Downstream | Verification, Clone Detection |

### Plate Verification (`domain/plate_verification/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Validate plate against registry; vehicle attributes |
| Ubiquitous Language | Registry, Registration, Validity, Mismatch |
| Collaborators | Vehicle registry outbound port |
| Downstream | Clone Detection, Alerting |

### Clone Detection (`domain/clone_detection/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Identify duplicate plates across inconsistent contexts |
| Ubiquitous Language | Clone, Sighting, Correlation, Risk Score |
| Collaborators | Sighting repository, verification results |
| Downstream | Alerting |

### Alerting (`domain/alerting/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Domain rules for when and what to alert |
| Ubiquitous Language | Alert, Severity, Escalation, Audit Event |
| Collaborators | Alert publisher outbound port |

### Common (`domain/common/`)

| Aspect | Detail |
|--------|--------|
| Responsibility | Minimal shared kernel only — avoid anemic shared model |
| Contents | Base identifiers, cross-cutting value objects, domain error base |

---

## Context Integration Patterns

| From | To | Pattern |
|------|-----|---------|
| Ingestion | Recognition | Local call via orchestration use case |
| Recognition | Verification | Sequential pipeline in application layer |
| Verification | Clone Detection | Domain events or orchestrated use case _TBD_ |
| Clone Detection | Alerting | Outbound port + domain policy |

---

## Package Placement

Each context has mirrored folders:

```
domain/<context>/
application/use_cases/<context>/
application/ports/... (shared across contexts)
tests/unit/domain/<context>/
```

---

## Related

- [Overview](overview.md)
- [Module Map](module-map.md)
