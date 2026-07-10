# Application — Ports

Interface definitions for hexagonal architecture.

---

## Inbound Ports (`inbound/`)

Driving interfaces — what the outside world can invoke.

| Placeholder File | Use Case Area |
|------------------|---------------|
| `process_image_command_port.placeholder` | Ingestion + recognition |
| `verify_plate_query_port.placeholder` | Verification |
| `detect_clone_command_port.placeholder` | Clone detection |
| `health_check_port.placeholder` | Operations |

---

## Outbound Ports (`outbound/`)

Driven interfaces — what the application needs from outside.

| Placeholder File | Infrastructure Adapter |
|------------------|------------------------|
| `plate_recognizer_port.placeholder` | `infrastructure/ml/` |
| `plate_detector_port.placeholder` | `infrastructure/ml/` |
| `vehicle_registry_port.placeholder` | `infrastructure/external/` |
| `sighting_repository_port.placeholder` | `infrastructure/persistence/` |
| `alert_publisher_port.placeholder` | `infrastructure/messaging/` |
| `image_storage_port.placeholder` | `infrastructure/persistence/` |
| `clock_port.placeholder` | `infrastructure/common/` |
| `config_port.placeholder` | `infrastructure/config/` |

---

## SOLID

Each port is **small and focused** (Interface Segregation Principle).
