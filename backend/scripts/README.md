# Scripts

Operational and development helper scripts.

**Status:** Placeholders only — no executable scripts in foundation phase.

---

## Structure

| Directory | Purpose |
|-----------|---------|
| `setup/` | Environment bootstrap, DB init _TBD_ |
| `ci/` | Local CI simulation, lint runners _TBD_ |
| `ops/` | Backup, migration helpers _TBD_ |

---

## Guidelines (Future)

- Scripts are **not** part of the hexagonal core
- May invoke adapters/CLI entry points
- Document usage in script header or `docs/development/`
