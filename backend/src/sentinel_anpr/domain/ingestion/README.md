# Domain — Ingestion

Bounded context for accepting and validating incoming media and metadata.

---

## Ubiquitous Language

- **Capture** — A single image or frame
- **MediaSource** — Camera, upload, or API origin
- **Stream** — Continuous video feed reference

---

## Planned Artifacts

| Artifact | Path |
|----------|------|
| `Capture` entity | `entities/` |
| `MediaSource` entity | `entities/` |
| `CaptureReceived` event | `events/` |
