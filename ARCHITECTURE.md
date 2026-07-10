# ARCHITECTURE.md

Quick reference — full documentation in [docs/architecture/overview.md](docs/architecture/overview.md).

---

## SentinelANPR AI — Frozen Architecture (v0.1.0)

### Layers

| Layer | Path | Depends On |
|-------|------|------------|
| Domain | `src/sentinel_anpr/domain/` | — |
| Application | `src/sentinel_anpr/application/` | Domain |
| Infrastructure | `src/sentinel_anpr/infrastructure/` | Application, Domain |
| Adapters | `src/sentinel_anpr/adapters/` | Application |
| Bootstrap | `src/sentinel_anpr/bootstrap/` | All (wiring) |

### Bounded Contexts

`ingestion` → `plate_recognition` → `plate_verification` → `clone_detection` → `alerting`

### Key Ports

**Inbound:** ProcessImage, VerifyPlate, DetectClone, HealthCheck  
**Outbound:** PlateRecognizer, PlateDetector, VehicleRegistry, SightingRepository, AlertPublisher, ImageStorage, Clock, Config

### Sign-Off

Architecture is **frozen** until checklist in [docs/architecture/overview.md](docs/architecture/overview.md) is complete.
