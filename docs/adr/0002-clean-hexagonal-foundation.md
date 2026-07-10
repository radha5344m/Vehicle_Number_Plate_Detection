# ADR 0002: Clean Architecture + Hexagonal Foundation

**Status:** Accepted  
**Date:** 2026-07-06

## Context

SentinelANPR AI must support swappable ML backends, registry integrations, and multiple entry points (HTTP, CLI, messaging) while keeping business rules testable and independent of frameworks.

## Decision

Adopt **Clean Architecture** with **Hexagonal (Ports & Adapters)** as the structural foundation:

- `domain/` — enterprise rules
- `application/` — use cases and ports
- `infrastructure/` — driven adapters
- `adapters/` — driving adapters

No framework application code (React, FastAPI, etc.) in the foundation phase.

## Consequences

- **Positive:** Testable core; technology choices deferred via ADRs; clear dependency direction
- **Negative:** More folders and indirection than a monolith; team must enforce boundaries

## References

- [Architecture Overview](../architecture/overview.md)
- [Dependency Direction](../architecture/dependency-direction.md)
