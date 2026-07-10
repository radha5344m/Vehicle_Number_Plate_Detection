# SentinelANPR — Source Package

Root package for SentinelANPR AI application code.

---

## Layer Overview

```
sentinel_anpr/
├── domain/           # Enterprise business rules (innermost)
├── application/      # Use cases + ports
├── infrastructure/   # Driven adapters (outbound implementations)
├── adapters/         # Driving adapters (inbound entry points)
└── bootstrap/        # Composition root (dependency wiring) — TBD
```

---

## Dependency Flow

```
adapters → application → domain
infrastructure → application → domain
bootstrap → all layers (wiring only)
```

---

## Placeholder Policy

Files named `*.placeholder` describe planned modules. They contain **no implementation code**.

Replace with real modules only after architecture sign-off.

---

## Subpackages

| Package | README |
|---------|--------|
| Domain | [domain/README.md](domain/README.md) |
| Application | [application/README.md](application/README.md) |
| Infrastructure | [infrastructure/README.md](infrastructure/README.md) |
| Adapters | [adapters/README.md](adapters/README.md) |
| Bootstrap | [bootstrap/README.md](bootstrap/README.md) |
