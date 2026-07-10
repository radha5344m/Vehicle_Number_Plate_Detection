# Domain — Alerting

Bounded context for alert generation rules and severity.

---

## Ubiquitous Language

- **Alert** — Notification-worthy event
- **Severity** — Critical, high, medium, low
- **Escalation** — Progressive notification policy

---

## Planned Artifacts

| Artifact | Path |
|----------|------|
| `Alert` entity | `entities/` |
| `AlertPolicy` service | `services/` |

**Note:** Actual message delivery is via `AlertPublisherPort` in infrastructure.
