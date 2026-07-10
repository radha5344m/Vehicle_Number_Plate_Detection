# SentinelANPR AI — Architecture Overview

**Version:** 0.1.0 (Foundation)  
**Status:** Frozen — pending stakeholder sign-off before implementation

---

## 1. Vision

SentinelANPR AI ingests vehicle imagery (still frames or video), recognizes number plates, verifies them against registry data, and flags potential **cloned plates** when multiple vehicles or inconsistent signals suggest fraud.

---

## 2. Architectural Style

The system combines three complementary approaches:

| Style | Role in SentinelANPR AI |
|-------|-------------------------|
| **Clean Architecture** | Concentric layers: Domain → Application → Infrastructure/Adapters |
| **Hexagonal (Ports & Adapters)** | Explicit ports; technology-agnostic core |
| **SOLID** | Single-responsibility use cases, interface segregation on ports, dependency inversion |

---

## 3. High-Level Component View

```
                    ┌─────────────────────────────────────────┐
                    │           Driving Adapters              │
                    │  HTTP │ CLI │ gRPC │ Message Consumer   │
                    └───────────────────┬─────────────────────┘
                                        │ inbound ports
                    ┌───────────────────▼─────────────────────┐
                    │            Application Layer            │
                    │   Use Cases │ DTOs │ Port Interfaces    │
                    └───────────────────┬─────────────────────┘
                                        │
                    ┌───────────────────▼─────────────────────┐
                    │              Domain Layer               │
                    │ Entities │ Value Objects │ Domain Svc   │
                    └───────────────────┬─────────────────────┘
                                        │ outbound ports
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
┌───────▼────────┐            ┌─────────▼─────────┐            ┌────────▼───────┐
│  Persistence   │            │   ML Inference    │            │ External APIs  │
│  (Driven)      │            │   (Driven)        │            │ Registry/RTO   │
└────────────────┘            └───────────────────┘            └────────────────┘
```

---

## 4. Core Workflows (Conceptual)

### 4.1 Plate Recognition Pipeline

1. Ingest image/stream metadata
2. Localize plate region (ML — driven adapter)
3. Extract plate text (OCR/ANPR — driven adapter)
4. Normalize plate string (domain value object)
5. Persist sighting (optional — driven adapter)

### 4.2 Verification Pipeline

1. Accept normalized plate + jurisdiction context
2. Query vehicle registry (outbound port)
3. Apply domain verification rules
4. Return verification result DTO

### 4.3 Clone Detection Pipeline

1. Correlate sightings across time/location/cameras
2. Score fraud signals (domain service)
3. Raise alert if threshold exceeded (outbound port)

---

## 5. Layer Responsibilities

| Layer | Location | May Depend On |
|-------|----------|---------------|
| Domain | `src/sentinel_anpr/domain/` | Nothing outside domain |
| Application | `src/sentinel_anpr/application/` | Domain only |
| Infrastructure | `src/sentinel_anpr/infrastructure/` | Application, Domain |
| Adapters (inbound) | `src/sentinel_anpr/adapters/` | Application, Domain |

---

## 6. Non-Functional Requirements (Planned)

| NFR | Target (TBD at implementation) |
|-----|--------------------------------|
| Latency | Real-time stream processing _TBD_ |
| Availability | _TBD_ |
| Auditability | All verification and clone decisions logged |
| Privacy | PII/plate data handling per policy _TBD_ |
| Scalability | Horizontal scaling of ingestion and inference _TBD_ |

---

## 7. Technology Neutrality

The foundation **does not** prescribe:

- Web framework (no FastAPI, Django, etc. in foundation)
- UI framework (no React in foundation)
- Database engine
- Message broker
- ML runtime

Technology choices will be recorded as ADRs before implementation.

---

## 8. Sign-Off Checklist

- [ ] Bounded contexts approved
- [ ] Port inventory approved
- [ ] Dependency rules acknowledged by team
- [ ] ADR process agreed
- [ ] Implementation may begin

---

## Related Documents

- [Clean Architecture Layers](clean-architecture-layers.md)
- [Hexagonal Ports & Adapters](hexagonal-ports-adapters.md)
- [Bounded Contexts](bounded-contexts.md)
