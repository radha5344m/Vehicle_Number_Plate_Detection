# Domain — Common (Shared Kernel)

Minimal shared concepts used across bounded contexts.

**Keep this package small** — resist turning it into a dumping ground.

---

## Planned Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| `DomainError` | `errors/` | Base domain exception |
| `PlateNumber` | `value_objects/` | Normalized plate value object |
| `SightingId` | `value_objects/` | Strongly typed identifier |
| `ConfidenceScore` | `value_objects/` | 0.0–1.0 validation |

---

## Placeholders

See `errors/`, `value_objects/` for `.placeholder` files.
