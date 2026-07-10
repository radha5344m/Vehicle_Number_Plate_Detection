# Domain — Plate Verification

Bounded context for validating plates against registry rules.

---

## Ubiquitous Language

- **Registry** — Authoritative vehicle registration source
- **VerificationOutcome** — Valid, invalid, or unknown
- **Mismatch** — Plate does not match vehicle attributes

---

## Planned Artifacts

| Artifact | Path |
|----------|------|
| `VerificationOutcome` entity | `entities/` |
| `VerificationPolicy` service | `services/` |

**Note:** External registry API access is **not** in domain — lives behind `VehicleRegistryPort`.
