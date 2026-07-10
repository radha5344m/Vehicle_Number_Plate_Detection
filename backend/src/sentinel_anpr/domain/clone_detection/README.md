# Domain — Clone Detection

Bounded context for identifying potentially cloned plates.

---

## Ubiquitous Language

- **Sighting** — Observed plate at time/place
- **CloneRisk** — Scored suspicion level
- **Correlation** — Linking sightings across sources

---

## Planned Artifacts

| Artifact | Path |
|----------|------|
| `CloneRiskAssessment` entity | `entities/` |
| `CloneDetectionPolicy` service | `services/` |
