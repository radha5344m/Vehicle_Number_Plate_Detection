# Architecture Decision Records (ADR)

Document significant architectural and technical decisions.

---

## Format

Use [Michael Nygard's ADR template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

| Section | Content |
|---------|---------|
| Title | Short noun phrase |
| Status | Proposed \| Accepted \| Deprecated \| Superseded |
| Context | Forces at play |
| Decision | What we decided |
| Consequences | Positive and negative outcomes |

---

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-clean-hexagonal-foundation.md) | Clean + Hexagonal foundation | Accepted |
| _0003+_ | _Technology choices (DB, ML, transport)_ | _Proposed at implementation_ |

---

## Process

1. Propose ADR in PR before major structural or technology change
2. Review with team
3. Merge when **Accepted**
4. Supersede rather than delete obsolete ADRs
