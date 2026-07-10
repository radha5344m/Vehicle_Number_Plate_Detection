# Product Requirements Document

# SentinelANPR AI  
**AI-Powered Smart Vehicle Verification & Investigation Platform**

| Field | Value |
|-------|-------|
| **Product Name** | SentinelANPR AI |
| **Version** | 2.0 |
| **Document Type** | Product Requirements Document (PRD) |
| **Status** | Approved for Hackathon Delivery |
| **Domain** | Artificial Intelligence · Computer Vision · Public Safety · Smart Policing |
| **Event** | Prakasam Police Hackathon |
| **Primary AI Provider** | Google Gemini Vision API (`gemini-2.5-flash`) |
| **Document Owner** | Product & Engineering Leadership |
| **Classification** | Internal — Law Enforcement Technology |
| **Last Updated** | 2026-07-08 |

---

## Document Control

| Version | Date | Author Role | Summary of Changes |
|---------|------|-------------|--------------------|
| 1.0 | 2026-Q2 | Architecture | Foundation: Clean Architecture + YOLO/OCR design |
| 1.5 | 2026-Q2 | Product + Eng | Migration to single OpenAI Vision workflow |
| **2.0** | **2026-07** | **PM + Architect** | **Production Vision path = Google Gemini; full PRD rewrite** |

**Reviewers:** Technical Lead · Software Architect · AI Solution Architect · Hackathon Mentors  
**Approvers:** Product Owner · Police Domain Sponsor (Hackathon)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)  
2. [Problem Statement](#2-problem-statement)  
3. [Vision](#3-vision)  
4. [Objectives](#4-objectives)  
5. [Stakeholders](#5-stakeholders)  
6. [User Personas](#6-user-personas)  
7. [User Stories](#7-user-stories)  
8. [Functional Requirements](#8-functional-requirements)  
9. [Non-Functional Requirements](#9-non-functional-requirements)  
10. [Product Workflow](#10-product-workflow)  
11. [System Workflow](#11-system-workflow)  
12. [AI Workflow](#12-ai-workflow)  
13. [Use Case Diagram](#13-use-case-diagram)  
14. [Feature Specifications](#14-feature-specifications)  
15. [UI Requirements](#15-ui-requirements)  
16. [Backend Requirements](#16-backend-requirements)  
17. [Database Requirements](#17-database-requirements)  
18. [API Requirements](#18-api-requirements)  
19. [AI Design](#19-ai-design)  
20. [Risk Assessment Engine](#20-risk-assessment-engine)  
21. [Report Generation](#21-report-generation)  
22. [Analytics Module](#22-analytics-module)  
23. [Security Requirements](#23-security-requirements)  
24. [Performance Requirements](#24-performance-requirements)  
25. [Deployment Requirements](#25-deployment-requirements)  
26. [Testing Strategy](#26-testing-strategy)  
27. [Risks & Mitigations](#27-risks--mitigations)  
28. [Assumptions](#28-assumptions)  
29. [Future Scope](#29-future-scope)  
30. [Mapping to the 10 Engineering Pillars](#30-mapping-to-the-10-engineering-pillars)  
31. [Project Timeline](#31-project-timeline)  
32. [Acceptance Criteria](#32-acceptance-criteria)  
33. [Appendix](#33-appendix)

---

# 1. Executive Summary

**SentinelANPR AI** is an intelligent, end-to-end **vehicle verification and investigation platform** built for frontline policing and traffic enforcement. An officer uploads a single photograph of a vehicle; the platform uses **Google Gemini Vision AI** to extract the registration number and vehicle attributes, verifies them against a vehicle registry, assesses fraud and mismatch risk, and produces a downloadable investigation report—within a single, audited workflow.

### Strategic Context

Traditional Automatic Number Plate Recognition (ANPR) stacks rely on a brittle chain of **object detection (YOLO) → plate crop → OCR (PaddleOCR) → manual/registry steps**. Each hop introduces latency, integration cost, and failure modes under Indian field conditions (angled plates, glare, night cuts, low resolution phone captures).  

**Version 2.0** replaces that multi-model pipeline with a **single multimodal Vision AI stage (Google Gemini)**, preserving Clean Architecture so the Vision provider remains swappable without changing domain rules or officer-facing workflows.

### Value Proposition

| Dimension | Outcome |
|-----------|---------|
| **Time** | Minutes of manual multi-tool work → one upload → structured investigation |
| **Accuracy** | Multimodal understanding of plate + brand/model/color/type in one pass |
| **Accountability** | JWT-authenticated officers, audit logs, scan history, PDF evidence trail |
| **Operations** | Dashboard, analytics, and risk distribution for supervisory insight |
| **Architecture** | Production-grade Clean / Hexagonal backend; modern React command-center UI |

### Product Scope (v2.0)

**In scope:** Secure officer login · Operations dashboard · Full vehicle verification workflow · Registry lookup · Scan history · Analytics · PDF investigation reports · Gemini Vision integration · Risk engine · Role-aware UI.

**Out of scope (v2.0):** Live CCTV / multi-camera grids · National VAHAN live API · Face recognition · Automatic FIR filing · Drone feeds · Offline-first mobile SDKs (roadmap).

### Success Snapshot

For the Prakasam Police Hackathon, success means a **demonstrable, architecture-correct product** that: (1) authenticates officers, (2) analyzes real vehicle images via Gemini, (3) verifies against seeded/demo registry data, (4) scores risk, (5) emits a PDF report, and (6) updates dashboard and history—under the **Ten Engineering Pillars** defined in this PRD.

---

# 2. Problem Statement

### 2.1 Operational Reality

Police officers in traffic checkpoints, highway patrols, and investigations routinely must answer:

> *Is this vehicle what it claims to be? Does the plate match the registered make, model, and color? Is there a clone or fraud signal?*

Today that answer often requires **multiple systems and manual effort**: capture → separate ANPR tool → separate registry lookup → mental comparison → handwritten or disparate digital notes.

### 2.2 Limitations of Legacy ANPR Chains

| Pain Point | Impact |
|------------|--------|
| Multi-stage ML (detect → OCR) | Cascading failures; poor plate crops kill OCR |
| Phone / mobile imagery | Variable resolution, orientation, lighting |
| Tool fragmentation | High cognitive load; slow decision cycles |
| Weak audit trail | Hard to defend actions in court or internal review |
| Limited attribute cross-check | Plate may be correct while vehicle identity is wrong (clone plates) |

### 2.3 Opportunity

A **single Vision AI model** can jointly reason over the full vehicle frame—plate text and visual attributes—then feed a **deterministic verification and risk policy** in software. That combination is ideally suited to hackathon-to-pilot delivery and to later national-registry integration.

### 2.4 Problem Statement (Formal)

**Police officers lack a unified, trustworthy, and fast platform that converts one vehicle photograph into a complete, auditable investigation outcome (identity, verification, risk, and report).** Existing approaches are too fragmented, too fragile under field imagery, and too slow for continuous checkpoint operations.

---

# 3. Vision

### 3.1 Product Vision Statement

> **Empower every authorized officer to turn one vehicle image into a defensible digital investigation—in seconds—using trustworthy AI, clean engineering, and police-grade accountability.**

### 3.2 North-Star Experience

1. Officer opens Verify Vehicle.  
2. Captures or uploads a photo.  
3. Sees progress: Upload → Vision Analysis → Registry → Risk → Save → Report.  
4. Reviews registration, attributes, registry match, risk level, and AI explanation.  
5. Downloads a PDF investigation report.  
6. Supervisor later reviews dashboards, history, and analytics.

### 3.3 Design Principles

| Principle | Meaning |
|-----------|---------|
| **Officer-first** | Field time and clarity beat feature density |
| **One upload, full outcome** | Avoid multi-tool loops |
| **AI for perception; rules for judgment** | Gemini extracts; domain policies decide risk |
| **Provider-agnostic core** | Ports allow Gemini today, other Vision APIs tomorrow |
| **Evidence by default** | Every scan is persisted and reportable |
| **Architecture as product** | Maintainability is a police IT requirement, not a luxury |

### 3.4 Positioning

| Competitor Class | SentinelANPR Differentiation |
|------------------|------------------------------|
| Pure ANPR cameras | Software investigation workspace, not only plate string |
| Generic OCR apps | Registry + risk + report + officer auth |
| Spreadsheet / paper logs | Structured digital evidence trail |

---

# 4. Objectives

### 4.1 Business / Mission Objectives

| ID | Objective | Measurable Target (Hackathon / Pilot) |
|----|-----------|----------------------------------------|
| O1 | Reduce vehicle verification time | Median workflow &lt; 60s (network &amp; Gemini permitting) |
| O2 | Improve investigation completeness | 100% completed scans produce structured result + optional PDF |
| O3 | Detect suspicious vehicles | Risk engine flags MEDIUM/HIGH with explanation |
| O4 | Assist field inspections | End-to-end UI usable by non-technical officers |
| O5 | Generate digital investigation reports | PDF downloadable per completed investigation |

### 4.2 Product Objectives (v2.0)

- Replace YOLO+OCR runtime dependency with **Google Gemini Vision**.  
- Keep **Clean Architecture** and dependency direction intact.  
- Deliver **dashboard, history, analytics, reports** on the same data model.  
- Ensure **JWT security**, input validation, and audit-friendly logging.  
- Ship a **professional police command-center UI** (light, blue/white).

### 4.3 Non-Goals (v2.0)

- Replacing national VAHAN as system-of-record.  
- Court-certified forensic imaging suite.  
- Autonomous enforcement without human officer.

---

# 5. Stakeholders

| Stakeholder | Interest | Influence | Engagement |
|-------------|----------|-----------|------------|
| Police Officers (End Users) | Speed, clarity, trust | High | Daily users |
| Traffic / Highway Patrol | Checkpoint throughput | High | Core personas |
| Investigation Officers | Evidence quality | High | Deep-dive users |
| RTO Officials | Registry integrity | Medium | Lookup consumers / partners |
| Station / District Leadership | Oversight, analytics | High | Dashboard consumers |
| Hackathon Mentors / Jury | Innovation + engineering rigor | High | Evaluators |
| Product Manager | Scope, value, timeline | High | Owner of PRD |
| Technical Lead / Architects | Feasibility, quality | High | Solution design |
| Security / IT (future) | Compliance, hosting | Medium | Post-hackathon |

### RACI (Selected Decisions)

| Decision | PM | Arch | Eng | Domain Sponsor |
|----------|----|------|-----|----------------|
| Feature scope v2.0 | **A** | C | C | C |
| AI provider (Gemini) | C | **A** | R | I |
| Risk policy thresholds | C | C | R | **A** |
| Security baseline | C | **A** | R | I |
| Demo data / registry seed | C | I | R | **A** |

*(R = Responsible, A = Accountable, C = Consulted, I = Informed)*

---

# 6. User Personas

### 6.1 Persona A — “Checkpoint Constable” (Primary)

| Attribute | Detail |
|-----------|--------|
| **Name / Role** | Arjun, Traffic Constable |
| **Goals** | Clear vehicles quickly; escalate only true risks |
| **Environment** | Roadside, mobile connectivity, phone camera |
| **Pain** | Typing plate numbers; slow OCR tools; paper notes |
| **Needs** | One-tap upload, clear RISK badge, offline FAQ later |
| **Success** | Knows match / mismatch in under a minute |

### 6.2 Persona B — “Investigation Officer”

| Attribute | Detail |
|-----------|--------|
| **Name / Role** | Meena, IO |
| **Goals** | Build evidence packs; clone-plate patterns |
| **Pain** | Scattered photos and unverifiable AI “guesses” |
| **Needs** | PDF reports, history search, attribute vs registry diffs |
| **Success** | Court-ready narrative with timestamps and officer ID |

### 6.3 Persona C — “Station House Supervisor”

| Attribute | Detail |
|-----------|--------|
| **Name / Role** | Inspector Rao |
| **Goals** | Monitor volume, risk mix, officer activity |
| **Needs** | Dashboard KPIs, analytics trends |
| **Success** | Spot spike in HIGH risk verifications within a shift |

### 6.4 Persona D — “RTO / Registry Liaison”

| Attribute | Detail |
|-----------|--------|
| **Goals** | Ensure lookup fidelity |
| **Needs** | Clear FOUND / NOT_FOUND messaging; future VAHAN bridge |
| **Success** | No false “verified” without registry hit |

### 6.5 Anti-Personas

- Unauthenticated public users (no public plate lookup portal in v2.0).  
- Automated ticket cameras without human-in-the-loop (roadmap only).

---

# 7. User Stories

### 7.1 Authentication

| ID | As a… | I want to… | So that… | Priority |
|----|-------|------------|----------|----------|
| US-AUTH-01 | Officer | Log in with badge & password | Access only authorized tools | P0 |
| US-AUTH-02 | Officer | Stay logged in with refresh tokens | Work a shift without constant re-login | P0 |
| US-AUTH-03 | Officer | Log out securely | End device sessions | P0 |
| US-AUTH-04 | Officer | See my profile | Confirm badge/rank on reports | P1 |

### 7.2 Verification Workflow

| ID | As a… | I want to… | So that… | Priority |
|----|-------|------------|----------|----------|
| US-WF-01 | Officer | Upload a vehicle photo | Start verification | P0 |
| US-WF-02 | Officer | See staged progress | Understand system activity | P0 |
| US-WF-03 | Officer | Get registration number from AI | Avoid typing plates | P0 |
| US-WF-04 | Officer | See brand/model/color/type | Compare with physical vehicle | P0 |
| US-WF-05 | Officer | See confidence & explanation | Calibrate trust | P0 |
| US-VF-06 | Officer | Auto registry lookup | Confirm legal vehicle identity | P0 |
| US-WF-07 | Officer | See risk level & recommendation | Decide next action | P0 |
| US-WF-08 | Officer | Download PDF report | Preserve evidence | P0 |

### 7.3 History, Dashboard, Analytics

| ID | As a… | I want to… | So that… | Priority |
|----|-------|------------|----------|----------|
| US-HIST-01 | Officer | Search prior scans by plate | Follow-up cases | P0 |
| US-HIST-02 | Officer | Filter by risk level | Triage backlog | P1 |
| US-DASH-01 | Supervisor | View total/verified scans | Cap shifts | P0 |
| US-AN-01 | Supervisor | View risk distribution | Detect anomaly days | P1 |
| US-AN-02 | Supervisor | View verification trends | Plan staffing | P2 |

### 7.4 Negative / Edge Stories

| ID | Story | Priority |
|----|-------|----------|
| US-EDGE-01 | If AI cannot read plate → fail with clear message, no false registry hit | P0 |
| US-EDGE-02 | If registry missing → NOT_FOUND, not “verified” | P0 |
| US-EDGE-03 | If Gemini key missing → fail fast at startup / clear UI error | P0 |
| US-EDGE-04 | Reject undersized / invalid images at upload | P0 |

Acceptance criteria for stories are aggregated in **Section 32**.

---

# 8. Functional Requirements

### 8.1 FR — Authentication & Session

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SEC-01 | System shall authenticate officers via badge number + password | Must |
| FR-SEC-02 | System shall issue JWT access tokens and refresh tokens | Must |
| FR-SEC-03 | Protected APIs shall reject missing/invalid/expired tokens | Must |
| FR-SEC-04 | System shall expose current officer profile endpoint | Should |
| FR-SEC-05 | Logout shall invalidate refresh session (as implemented) | Should |

### 8.2 FR — Image Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ING-01 | Accept JPEG/PNG vehicle images via authenticated upload or workflow multipart | Must |
| FR-ING-02 | Validate content type, size limits, and minimum resolution | Must |
| FR-ING-03 | Persist upload metadata and storage key | Must |

### 8.3 FR — Vision AI Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AI-01 | Analyze full vehicle image using **Google Gemini Vision** | Must |
| FR-AI-02 | Return structured fields: registration_number, brand, model, color, type, confidence, explanation | Must |
| FR-AI-03 | Parse model JSON robustly (including fenced markdown strip) | Must |
| FR-AI-04 | On failure, return graceful explanation; do not crash process | Must |
| FR-AI-05 | Support `stub` provider for tests/local without cloud key | Must |
| FR-AI-06 | Never require or validate `OPENAI_API_KEY` when provider=gemini | Must |

### 8.4 FR — Registry Verification

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-REG-01 | Normalize plate text before lookup | Must |
| FR-REG-02 | Lookup vehicle record by registration | Must |
| FR-REG-03 | Return FOUND / NOT_FOUND with message | Must |
| FR-REG-04 | Surface owner, make, model, color, type, registration status when FOUND | Must |

### 8.5 FR — Attribute Comparison & Risk

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RISK-01 | Compare Vision attributes to registry attributes | Must |
| FR-RISK-02 | Compute risk score and level: LOW / MEDIUM / HIGH (CRITICAL if policy defines) | Must |
| FR-RISK-03 | Produce human-readable explanation and recommendation | Must |
| FR-RISK-04 | Persist risk assessment with scan outcome | Must |

### 8.6 FR — Persistence & Reports

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PER-01 | Persist completed (and failed) workflow outcomes to scan history | Must |
| FR-REP-01 | Generate PDF investigation report for completed investigations | Must |
| FR-REP-02 | Include officer, date/time, location (if provided), plate, owner, details, verification, risk, recommendation | Must |
| FR-REP-03 | Allow download of PDF by authenticated user | Must |

### 8.7 FR — Dashboard, History, Analytics

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DASH-01 | Dashboard summary: totals, verified counts, risk snapshots | Must |
| FR-DASH-02 | Recent activity feed | Must |
| FR-HIST-01 | Paginated/filterable scan history | Must |
| FR-AN-01 | Analytics overview: daily volume, risk distribution, trends | Should |

### 8.8 FR — Configuration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CFG-01 | Vision provider selected via `SENTINEL_VISION_PROVIDER` | Must |
| FR-CFG-02 | Gemini key via `GEMINI_API_KEY`; model via `SENTINEL_GEMINI_MODEL` | Must |
| FR-CFG-03 | Fail fast at startup if provider=gemini and key missing | Must |

---

# 9. Non-Functional Requirements

| Category | ID | Requirement |
|----------|-----|-------------|
| **Performance** | NFR-PERF-01 | API health responds &lt; 200ms locally |
| | NFR-PERF-02 | Upload validation &lt; 2s for ≤5MB images |
| | NFR-PERF-03 | End-to-end verification target &lt; 60s typical (Gemini latency dominant) |
| **Scalability** | NFR-SCL-01 | Architecture supports horizontal API replicas behind load balancer |
| | NFR-SCL-02 | Stateless JWT allows multi-instance auth |
| **Security** | NFR-SEC-01 | Secrets only in env / secret manager—never in source |
| | NFR-SEC-02 | TLS in production; CORS explicitly configured |
| **Reliability** | NFR-REL-01 | Graceful degradation messages when Vision API fails |
| | NFR-REL-02 | Structured logging with correlation IDs on HTTP requests |
| **Availability** | NFR-AVL-01 | Hackathon demo SLA: single-node uptime during presentation window |
| | NFR-AVL-02 | Health endpoint for liveness checks |
| **Maintainability** | NFR-MNT-01 | Clean Architecture layers enforced; domain purity |
| | NFR-MNT-02 | Tests mirror `src/` layout |
| **Extensibility** | NFR-EXT-01 | VisionAiService port allows new providers without domain changes |
| | NFR-EXT-02 | Config-driven provider switch (`gemini` \| `stub`) |
| **Usability** | NFR-UX-01 | Progress stages visible; errors in plain language |
| **Compliance (future)** | NFR-CMP-01 | Design ready for audit log retention policies |

---

# 10. Product Workflow

### 10.1 Officer Journey (Happy Path)

```
Login → Dashboard (optional) → Verify Vehicle
  → Select / Capture Image
  → Confirm Location Label (optional)
  → Submit
  → Observe Progress Tracker
  → Review Investigation Result
  → Download PDF / Navigate to History
```

### 10.2 Progress Stages (Product Copy)

| Stage Key | Officer-Facing Label |
|-----------|----------------------|
| `upload` | Image Upload |
| `vision_analysis` | Vision AI Analysis |
| `registry_verification` | Registry Verification |
| `risk_assessment` | Risk Assessment |
| `save_investigation` | Save Investigation |
| `report_generation` | Report Generation |

### 10.3 Alternate Flows

| Flow | Trigger | Product Behavior |
|------|---------|------------------|
| Auth failure | Bad credentials | 401 + clear message |
| Invalid image | Too small / wrong type | Block with validation error |
| No plate | Vision empty registration | Failed workflow; no fake registry match |
| Not in registry | Plate unknown | NOT_FOUND; elevated risk policy as defined |
| Provider outage | Gemini error | Fail stage with explanation; log error |

---

# 11. System Workflow

### 11.1 Logical System Sequence

```
[React SPA] --JWT--> [FastAPI Interfaces]
                       |
                       v
              [Application Use Case:
               RunVisionVerificationWorkflow]
                       |
         +-------------+-------------+
         |             |             |
         v             v             v
   Upload/Store   VisionAiService  Domain Policies
         |         (Gemini/Stub)   (compare/risk)
         |             |             |
         +-------> Registry Repo <---+
                       |
                       v
              Persist Outcome + PDF Store
                       |
                       v
              History / Dashboard / Analytics reads
```

### 11.2 Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Interfaces** | HTTP schemas, auth middleware, DI wiring |
| **Application** | Orchestration use cases, ports, DTOs |
| **Domain** | Plate normalization, comparison, risk policy, report policy |
| **Infrastructure** | Gemini client, SQLite/Postgres, PDF, JWT, filesystem |

### 11.3 Composition Root

Concrete adapters are wired **only** in `bootstrap` / dependency injection. Domain and application never import FastAPI, SQLAlchemy, or Gemini SDK.

---

# 12. AI Workflow

### 12.1 Stage Diagram

```
Image Upload
     │
     ▼
Vision AI Analysis (Google Gemini)
     │
     ├─► Registration Extraction
     └─► Vehicle Attribute Extraction
              │
              ▼
     Registry Verification
              │
              ▼
     Risk Assessment
              │
              ▼
     Investigation Report
```

### 12.2 Vision Output Contract

| Field | Type | Description |
|-------|------|-------------|
| `registration_number` | string \| null | Plate text (Indian formats preferred) |
| `vehicle_color` | string \| null | Observed color |
| `vehicle_type` | string \| null | e.g., car, bike, truck |
| `brand` | string \| null | Make / manufacturer |
| `model` | string \| null | Model name |
| `confidence` | float 0–1 | Model self-estimated confidence |
| `explanation` | string | Short rationale for officers |

### 12.3 Prompt Strategy (Infrastructure)

Gemini is instructed to return **ONLY valid JSON** matching the schema above—no markdown (with server-side fence stripping as defense in depth).

### 12.4 Provider Modes

| `SENTINEL_VISION_PROVIDER` | Behavior |
|----------------------------|----------|
| `gemini` (default) | Live Google GenAI client; requires `GEMINI_API_KEY` |
| `stub` | Deterministic demo analysis; no cloud key |

---

# 13. Use Case Diagram

```
                    ┌─────────────────────────────────────┐
                    │         SentinelANPR AI             │
                    │                                     │
  Officer ─────────►│ «use case» Authenticate             │
     │              │ «use case» Upload Vehicle Image     │
     │              │ «use case» Run Full Verification    │
     │              │ «use case» Lookup Vehicle Registry  │
     │              │ «use case» Assess Risk              │
     │              │ «use case» Generate Report          │
     │              │ «use case» Query Scan History       │
     │              │ «use case» View Dashboard           │
     │              │ «use case» View Analytics           │
     │              └──────────────┬──────────────────────┘
     │                             │
     │                             ▼
     │                    ┌─────────────────┐
     └───────────────────►│ Google Gemini   │
                          │ Vision API      │
                          └─────────────────┘
                                   ▲
  Supervisor ──► Dashboard / Analytics / Oversight History
  RTO Liaison ─► Registry data stewardship (external)
```

### Primary Use Cases (brief)

1. **Authenticate** — establish trusted officer session.  
2. **Run Full Verification** — includes Vision, registry, risk, persist, report.  
3. **Query History** — retrieve prior investigations.  
4. **View Dashboard / Analytics** — supervisory awareness.

---

# 14. Feature Specifications

### 14.1 Secure Login

- Badge + password form.  
- Demo credentials for hackathon (documented; change in production).  
- Token storage on client with protected route guards.  
- Error states for invalid credentials / network.

### 14.2 Dashboard

- KPI cards: total scans, verified vehicles, risk highlights.  
- Recent activity list with plate and risk cues.  
- Navigation into verification and history.

### 14.3 Full Vehicle Verification

- Image picker / drag-drop.  
- Optional location label.  
- Multi-stage progress tracker (Vision AI terminology—not YOLO/OCR).  
- Result panel: registration, attributes, confidence, explanation, registry block, risk badge, report download.

### 14.4 Vehicle Registry Lookup

- Invoked automatically by workflow.  
- Discrete API available for plate query (configured routes).  
- Clear FOUND vs NOT_FOUND.

### 14.5 Scan History

- List / filter / search by plate and risk.  
- Links to investigation artifacts where available.

### 14.6 Analytics Dashboard

- Daily verification counts.  
- Risk distribution.  
- Vehicle type / trend placeholders as data allows.  
- Officer performance aggregates (pilot-grade).

### 14.7 Report Generation

- Server-side PDF.  
- Download via authenticated endpoint.  
- Content: see Section 21.

---

# 15. UI Requirements

### 15.1 Technology

| Item | Choice |
|------|--------|
| Framework | React |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Routing | React Router |
| Build | Vite |

### 15.2 Visual Design System

| Token | Guidance |
|-------|----------|
| Theme | **Light** |
| Palette | Professional **blue & white**; high-contrast text |
| Metaphor | Police **command center** — calm, authoritative, sparse chrome |
| Density | Comfortable for tablet + desktop; usable on large phones |
| Iconography | Lucide (or equivalent) consistent set |
| Motion | Subtle progress animations; no distracting video |

### 15.3 Responsiveness

- Desktop-first for station ops; usable on officer tablet (≥768px).  
- Touch targets ≥ 40px where primary actions are COA buttons.

### 15.4 Accessibility (Pragmatic v2.0)

- Semantic headings, labeled form controls.  
- Color not sole risk indicator (text label + badge).  
- Keyboard-focusable primary actions.

### 15.5 Page Inventory

| Page | Purpose |
|------|---------|
| Login | Auth |
| Dashboard | KPIs / recent |
| Verify Vehicle / Workflow | Core job-to-be-done |
| Result | Investigation detail |
| History | Searchable scans |
| Analytics | Trends |
| Reports (if separate) | Download / list |

### 15.6 Terminology Rules

- Prefer **Vision AI Analysis**—never expose YOLO, PaddleOCR, or OpenAI in UI copy.  
- Risk levels in plain language with color coding.

---

# 16. Backend Requirements

### 16.1 Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI |
| Language | Python 3.11+ |
| Architecture | Clean Architecture + Hexagonal Ports & Adapters |
| DI | Composition root (`bootstrap` / `dependency_injection`) |
| Persistence | SQLAlchemy + SQLite (dev) / PostgreSQL (prod target) |
| Auth | JWT (access + refresh) |
| PDF | Server-side PDF generator adapter |
| Vision | `google-genai` → `GeminiVisionService` |

### 16.2 Architectural Rules (Non-Negotiable)

1. Domain has **zero** framework / DB / Vision SDK imports.  
2. Application depends on **ports**, not adapters.  
3. Interfaces remain **thin**—no business rules or SQL in routes.  
4. Errors: domain errors mapped to HTTP only at interface edge.  
5. One responsibility per module; mirror tests under `tests/`.

### 16.3 Core Use Cases

- `Login` / `Logout` / `GetCurrentOfficer`  
- `UploadVehicleImage`  
- `RunVisionVerificationWorkflow`  
- `LookupVehicle`  
- `AssessRisk`  
- `PersistWorkflowOutcome`  
- `GenerateInvestigationReport`  
- `QueryScanHistory`  
- `GetDashboardSummary` / `GetRecentActivity`  
- `GetAnalyticsOverview`

---

# 17. Database Requirements

### 17.1 Platforms

| Environment | Engine |
|-------------|--------|
| Development / Hackathon | **SQLite** |
| Production target | **PostgreSQL** |

Schema design remains engine-agnostic where practical (types/indexes documented in `docs/database/`).

### 17.2 Conceptual Entities

| Entity | Purpose |
|--------|---------|
| Officers / Credentials | Auth |
| Vehicles (Registry) | Authoritative attributes |
| Uploads / Images | Binary metadata |
| Scan History | Investigation spine |
| Verifications | Registry outcome |
| Risk Assessments | Scores / levels |
| Reports | PDF metadata / checksums |
| Audit Logs | Security & ops trail |

### 17.3 Data Rules

- Prefer UUID / opaque IDs for scans and reports.  
- Normalize plate text for lookup indexes.  
- Soft failure states recorded—do not delete evidence on AI miss.  
- No secrets in DB (tokens hashed/store patterns as implemented).

### 17.4 Demo Seed (Hackathon)

Seed registry with known plates (e.g., `AP09*` series) for FOUND demonstrations. Real Gemini extractions for unknown plates must show **NOT_FOUND**, proving live Vision is not stubbed.

---

# 18. API Requirements

### 18.1 Style

- Versioned REST under `/v1`.  
- JSON envelopes with `success` / `data` / `error` conventions.  
- Bearer JWT for protected routes.  
- Multipart for image upload & verification workflow.

### 18.2 Endpoint Groups (Illustrative)

| Group | Examples |
|-------|----------|
| Auth | `POST /v1/auth/login`, `refresh`, `logout`, `GET /me` |
| Uploads | `POST /v1/uploads/vehicle-image` |
| Workflow | `POST /v1/workflow/vehicle-verification` |
| Vehicles | Lookup by plate |
| History | `GET /v1/history/scans` |
| Dashboard | `GET /v1/dashboard/summary`, `recent-activity` |
| Analytics | Overview endpoints |
| Reports | Download by id |
| Health | `GET /v1/health` |

### 18.3 Workflow Response (Key Fields)

Must include: `status`, staged `steps`, `registration_number`, vision confidence/attributes/explanation, registry projection, `risk_level` / score, `scan_id`, `report_id`, recommendation / investigation summary.

### 18.4 Error Model

| HTTP | Typical Code | Meaning |
|------|--------------|---------|
| 400 | VALIDATION_ERROR | Image/input invalid |
| 401 | AUTH_* | Missing/invalid token or login |
| 404 | NOT_FOUND | Resource missing |
| 500 | INTERNAL | Unexpected; logged with correlation id |

---

# 19. AI Design

### 19.1 Architectural Placement

Vision sits in **Infrastructure**, behind application port:

```
VisionAiService (port)
    ├── GeminiVisionService   ← production default
    └── StubVisionService     ← tests / offline demo
```

Domain remains unaware of Gemini.

### 19.2 Runtime Configuration

| Variable | Purpose |
|----------|---------|
| `SENTINEL_VISION_PROVIDER` | `gemini` \| `stub` |
| `GEMINI_API_KEY` | Google AI Studio / Gemini API key |
| `SENTINEL_GEMINI_MODEL` | Default `gemini-2.5-flash` |

Startup validates **only** Gemini key when provider=`gemini`. **`OPENAI_API_KEY` is not used.**

### 19.3 Model Behavior Requirements

- Multimodal image + text prompt.  
- Strict JSON schema output.  
- Logging: request start/complete metrics **without** logging secrets or full raw keys.  
- Timeouts / error surfaces for quota, network, parse failures.

### 19.4 Accuracy / Trust Model

| Element | Approach |
|---------|----------|
| Perception | Gemini probabilistic |
| Judgment | Deterministic domain comparison + risk policy |
| Human | Officer always reviews HIGH cases before enforcement action |

### 19.5 Evaluation Harness (Recommended)

- Golden image set (day/night/angle/close crop).  
- Track plate exact-match rate vs human labels.  
- Track attribute match rate vs registry when FOUND.  
- Stub path CI; optional nightly live-Gemini smoke (secret-gated).

---

# 20. Risk Assessment Engine

### 20.1 Purpose

Convert **Vision observations + registry facts** into an actionable risk posture for officers.

### 20.2 Inputs

- Registration match status (FOUND / NOT_FOUND).  
- Attribute diffs: color, type, brand/make, model.  
- Confidence score from Vision.  
- Policy version identifier.

### 20.3 Risk Levels

| Level | Typical Meaning | Officer Guidance (example) |
|-------|-----------------|----------------------------|
| **LOW** | Strong alignment | Proceed / routine |
| **MEDIUM** | Partial mismatch or low confidence | Verify physically; secondary check |
| **HIGH** | Strong mismatch / missing registry / fraud signals | Escalate; detain for verification per SOP |
| **CRITICAL** (if enabled) | Explicit watchlist / severe clone indicators | Immediate escalation |

Exact thresholds live in domain policy (versioned)—tuned with sponsors.

### 20.4 Outputs

- `risk_score` (numeric)  
- `risk_level` (enum)  
- `explanation`  
- `recommendation`  
- `signals[]` (structured reasons)

### 20.5 Governance

Risk policy is **software law**—not prompt text—so legal/ops owners can change rules without retraining a model.

---

# 21. Report Generation

### 21.1 Artifact

**PDF Investigation Report** generated server-side and stored with checksum metadata.

### 21.2 Mandatory Content Blocks

| Block | Content |
|-------|---------|
| Header | Product name, “Investigation Report”, report id |
| Officer | Name, badge, rank |
| Temporal | Date/time (UTC or configured timezone) |
| Location | Label if provided |
| Vehicle Image | Reference / embedded where size permits |
| Registration | Extracted plate |
| Owner | From registry when FOUND |
| Vehicle Details | Make/model/color/type (registry + observed) |
| Verification Result | FOUND / NOT_FOUND / mismatch summary |
| Risk | Score + level |
| Recommendation | Policy text |
| Footer | Disclaimer: AI-assisted; officer judgment final |

### 21.3 Product Rules

- Only authenticated officers download.  
- Failed workflows may omit PDF or produce limited failure reports (implementation choice; v2.0 prefers PDF on successful completion path).  
- Reports appear in history / workflow result deep links.

---

# 22. Analytics Module

### 22.1 Purpose

Give supervisors **situational awareness** without opening every scan.

### 22.2 Metrics (v2.0)

| Metric | Description |
|--------|-------------|
| Daily Verifications | Count of completed workflows per day |
| Risk Distribution | Share of LOW / MEDIUM / HIGH |
| Vehicle Types | Aggregate observed or registry types |
| Verification Trends | Time series of volume |
| Officer Performance | Scans per officer (pilot ethics: coaching, not punishment alone) |

### 22.3 UX

- Charts/cards on Analytics page.  
- Filters by date range (stretch).  
- Consistent with light blue/white theme.

### 22.4 Data Freshness

Near-real-time from DB aggregates for hackathon scale; later materialize if load grows.

---

# 23. Security Requirements

| Area | Requirement |
|------|-------------|
| **Authentication** | JWT access + refresh; password hashing (bcrypt or equivalent) |
| **Authorization** | Role-based hooks (officer/admin readiness); protect all mutations |
| **Input Validation** | Image MIME, size, resolution; string length limits |
| **API Security** | CORS allowlist; no stack traces to clients; rate-limit roadmap |
| **Secrets** | Env-only (`GEMINI_API_KEY`, JWT secret); `.env` gitignored |
| **Audit** | Structured logs for login, workflow start/fail, report downloads (as feasible) |
| **Data** | Minimize PII in client logs; owner names treated carefully |
| **Transport** | HTTPS in production |
| **Dependency** | Pin Vision SDK; no unused OpenAI runtime dependency |

### Explicit Non-Requirement (v2.0)

Public open registration or anonymous plate search—**prohibited**.

---

# 24. Performance Requirements

| Scenario | Target |
|----------|--------|
| Health check | &lt; 200 ms |
| Login | &lt; 1 s typical |
| Image upload persistence | &lt; 2 s (≤5 MB, local disk) |
| Gemini call | Budget 5–45 s depending on network/model |
| Full workflow | &lt; 60 s typical; UI timeout ≥ 120 s |
| History/dashboard queries | &lt; 1 s on SQLite demo scale |
| PDF generation | &lt; 3 s for standard one-page report |

### Capacity (Hackathon)

Support concurrent demo users (≈5–10) on a single backend instance. Production capacity sizing is out of scope pending infra choice.

---

# 25. Deployment Requirements

### 25.1 Hackathon Topology

```
Officer Browser
    → Frontend (Vite/React :5173)
    → Backend API (FastAPI/Uvicorn :8080)
        → SQLite file
        → Local upload/report dirs
        → Google Gemini API (egress HTTPS)
```

### 25.2 Configuration

Copy `backend/.env.example` → `backend/.env`. Required for live Vision:

```env
SENTINEL_VISION_PROVIDER=gemini
GEMINI_API_KEY=<secret>
SENTINEL_GEMINI_MODEL=gemini-2.5-flash
```

### 25.3 Production Target (Post-Hackathon)

| Concern | Guidance |
|---------|----------|
| Compute | Containerized API + static web (CDN) |
| DB | Managed PostgreSQL |
| Secrets | Cloud secret manager |
| Observability | Centralized logs + metrics |
| Network | Private link / egress controls for Gemini |

### 25.4 Operational Commands (Dev)

- Backend: `python main.py` (port 8080)  
- Frontend: `npm run dev` (port 5173)  
- Prefer `VITE_API_BASE_URL=http://127.0.0.1:8080` on Windows to avoid large upload proxy issues.

---

# 26. Testing Strategy

### 26.1 Test Pyramid

| Layer | Focus | Notes |
|-------|-------|-------|
| Domain unit | Policies, normalizers | Zero mocks preferred |
| Application unit | Workflow orchestration with fakes | Vision/registry/risk stubs |
| Infrastructure unit | Gemini JSON parse, config validation | Fake GenAI client |
| API integration | Auth, upload, workflow, history, dashboard, reports | Stub Vision via conftest |
| Frontend | Build/typecheck; critical component tests as added | |

### 26.2 Mandatory Suites (v2.0 Gate)

- Vision configuration: Gemini key required only when provider=gemini; no OpenAI fields.  
- Gemini adapter: valid JSON, markdown fences, empty image.  
- Workflow: stages include `vision_analysis`; no detection/OCR stages.  
- Risk / registry / report / dashboard / history integration green.

### 26.3 Live Gemini Testing

Optional manual: set real `GEMINI_API_KEY`, upload known vehicles, confirm non-stub plates and attributes. CI remains on stub to avoid secret leakage and flaky quotas.

### 26.4 Quality Gates

- All unit/integration tests pass before demo freeze.  
- Lint/typecheck on frontend.  
- Architecture checks: no illegal imports into domain.

---

# 27. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API quota / billing | Med | High | Monitor usage; stub fallback for demos; clear UI errors |
| Key leaked in chat/repo | Med | High | `.env` only; rotate keys; never commit secrets |
| Hallucinated plates | Med | High | Confidence + registry gate; officer confirmation |
| Registry incomplete | High | Med | Explicit NOT_FOUND; seed demo data for pitch |
| Network latency at venue | Med | Med | Increase client timeouts; pre-warm server |
| Scope creep (CCTV, face) | High | Med | Strict v2.0 non-goals; backlog in Future Scope |
| Architecture drift | Med | High | PRD pillars + Cursor/agent rules; code review |
| SQLite concurrency | Low | Med | Demo single writer; Postgres for production |

---

# 28. Assumptions

1. Officers have authorized accounts; demo badge credentials are acceptable for hackathon only.  
2. Registry dataset for demo is a **local seed**, not live national VAHAN.  
3. Images are captured with officer consent under policing SOP; privacy policies are sponsor-owned.  
4. Internet egress to Google Gemini is available during demo.  
5. English (+ Indian plate alphanumeric) is sufficient for v2.0 UI/AI prompts.  
6. A human officer remains decision-maker; software advises.  
7. Clock sync on host is reasonable for audit timestamps.  
8. Frontend and backend are co-deployed for the hackathon on a single workstation or small VM.

---

# 29. Future Scope

| Theme | Capability |
|-------|------------|
| Sensing | Live CCTV integration; multi-camera investigation |
| Aerial | Drone vehicle monitoring |
| Identity | Face recognition (separate legal track) |
| Threat intel | Criminal vehicle watchlist |
| Mobility | Real-time GPS tracking of patrols / intercepts |
| National data | VAHAN / state RTO live integration |
| Casework | Automatic FIR suggestion drafts (human-approved) |
| Edge | Offline/queue mode for low connectivity |
| Multilingual | Telugu / Hindi UI & prompts |
| MLOps | Continuous evaluation dashboards for Vision quality |

Each item requires **new ADRs**, privacy impact assessment, and explicit sponsorship—**not** in v2.0 acceptance.

---

# 30. Mapping to the 10 Engineering Pillars

### Pillar 1 — Architecture

- Clean Architecture + Hexagonal Ports & Adapters.  
- Layers: Domain → Application → Infrastructure + Interfaces.  
- Documented in `docs/architecture/` and enforced via project rules.

### Pillar 2 — Modularity

- Bounded contexts (verification, risk, ingestion, reporting, auth).  
- Vision provider isolated as a single infrastructure module.  
- Frontend feature folders for workflow, dashboard, history, analytics.

### Pillar 3 — Separation of Concerns

- Perception (Gemini) ≠ judgment (risk policy) ≠ presentation (React) ≠ persistence (repositories).  
- No business rules in route handlers or ORM models.

### Pillar 4 — Dependency Direction

- Dependencies point **inward** only.  
- Composition root wires `GeminiVisionService` to `VisionAiService` port.  
- Domain never imports FastAPI, SQLAlchemy, or `google-genai`.

### Pillar 5 — Interfaces & Contracts

- Application ports for Vision, logging, storage, repositories.  
- REST contracts under `/v1` with shared error envelope.  
- VisionAnalysisResult is the stable multimodal contract.

### Pillar 6 — Configuration Management

- 12-factor env configuration.  
- `SENTINEL_*` settings + `GEMINI_API_KEY`.  
- Fail-fast validation for Gemini provider.  
- `.env.example` as the contract of required variables.

### Pillar 7 — Security

- JWT auth, password hashing, CORS, input validation, secret hygiene, audit-oriented logs.  
- Removal of unused OpenAI key surface reduces attack/confusion surface.

### Pillar 8 — Observability

- Structured JSON logs; HTTP middleware with correlation IDs.  
- Startup diagnostics: provider, model, key existence (never key value).  
- Workflow stage logging (start/fail/complete).

### Pillar 9 — Testing & QA

- Mirrored unit/integration tests; stub Vision in CI.  
- Domain tests without mocks where possible.  
- Explicit Gemini adapter + config tests.

### Pillar 10 — Deployment & Operations

- Simple local runbook (main.py + npm).  
- Health endpoint.  
- Path to containers + PostgreSQL + secret manager for production.  
- Clear separation of stub vs live AI for ops safety.

---

# 31. Project Timeline

### 31.1 Hackathon Delivery Plan (Indicative)

| Phase | Duration | Outcomes |
|-------|----------|----------|
| **P0 Foundation** | Week 0–1 | Architecture freeze, ADRs, skeleton |
| **P1 Vertical Slice** | Week 1–2 | Auth + upload + registry + risk + PDF stubs |
| **P2 Vision Migration** | Week 2–3 | YOLO/OCR removed; Vision workflow; OpenAI interim |
| **P3 Gemini Cutover** | Week 3–4 | `GeminiVisionService`, env, DI, docs, UI terminology |
| **P4 Hardening** | Final days | Tests green, demo script, seed data, runbook |
| **P5 Showcase** | Demo day | Live verification + dashboard + report |

### 31.2 Milestones

| Milestone | Exit Criteria |
|-----------|---------------|
| M1 Architecture Sign-off | Pillars documented; dependency rules agreed |
| M2 Workflow Demoable | Stub path end-to-end |
| M3 Live Vision | Gemini analyzes real image |
| M4 Ops Surface | Dashboard + history + analytics populated |
| M5 Freeze | Tests pass; PRD v2.0 accepted |

### 31.3 Roles Across Timeline

PM owns scope; Architect owns pillars; Tech Lead owns delivery quality; Engineers implement; Domain sponsor validates risk language and demo plates.

---

# 32. Acceptance Criteria

### 32.1 Product Acceptance (Demo-Ready)

| # | Criterion | Pass Condition |
|---|-----------|----------------|
| A1 | Secure login | Valid badge/password obtains JWT; invalid rejected |
| A2 | Dashboard loads | Summary KPIs and recent activity render |
| A3 | Verification works | Upload → Gemini analysis → registry → risk → IDs returned |
| A4 | Structured AI output | Registration + attributes + confidence + explanation present on success |
| A5 | Registry path | Known seed plate → FOUND; unknown → NOT_FOUND |
| A6 | Risk engine | Level + recommendation shown |
| A7 | Report | PDF downloadable for completed investigation |
| A8 | History | New scan appears / searchable |
| A9 | Analytics | Overview loads without error |
| A10 | Provider truth | Startup logs `vision_provider=gemini`, `GeminiVisionService` |
| A11 | No OpenAI runtime dependency | Settings have no OpenAI fields; provider≠openai |

### 32.2 Engineering Acceptance

| # | Criterion |
|---|-----------|
| E1 | Domain purity preserved |
| E2 | Backend automated tests passing |
| E3 | Frontend builds |
| E4 | `.env.example` documents Gemini variables |
| E5 | Stub mode available for CI |

### 32.3 Explicit Failure Criteria

- Stub provider used during a “live AI” jury demo while claiming Gemini.  
- UI still references YOLO/OCR as active pipeline.  
- Server starts with provider=gemini and empty key (must fail fast).  
- Business logic embedded in FastAPI routers.

---

# 33. Appendix

### 33.1 Glossary

| Term | Definition |
|------|------------|
| **ANPR** | Automatic Number Plate Recognition |
| **Vision AI** | Multimodal model analyzing images + text instructions |
| **Gemini** | Google generative AI multimodal models |
| **Registry** | Authoritative vehicle records (demo DB or future VAHAN) |
| **Clone plate** | Same registration appearing on mismatched vehicle identity |
| **Port** | Interface in application layer for an external capability |
| **Adapter** | Infrastructure implementation of a port |
| **Risk engine** | Domain policy scoring mismatches and anomalies |

### 33.2 Environment Variable Reference

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `SENTINEL_VISION_PROVIDER` | Yes | `gemini` | `gemini` \| `stub` |
| `GEMINI_API_KEY` | If gemini | — | Secret |
| `SENTINEL_GEMINI_MODEL` | No | `gemini-2.5-flash` | Model id |
| `SENTINEL_DATABASE_URL` | No | SQLite path | Dev DB |
| `SENTINEL_API_PORT` | No | `8080` | API port |
| `SENTINEL_AUTH_JWT_SECRET` | Prod Yes | Dev default | Change in production |

### 33.3 Related Repository Documents

| Doc | Path |
|-----|------|
| Architecture overview | `docs/architecture/overview.md` |
| Configuration strategy | `docs/architecture/configuration-strategy.md` |
| API contracts | `docs/api/contracts-overview.md` |
| Database design | `docs/database/schema-design.md` |
| AI pipeline | `docs/ai-pipeline/README.md` |
| Getting started | `docs/development/getting-started.md` |
| Agent rules | `AGENTS.md` |

### 33.4 Demo Script (Suggested)

1. Login as demo officer.  
2. Show dashboard KPIs.  
3. Verify Vehicle with a clear plate image in registry → FOUND, LOW/ coherent risk.  
4. Verify with unknown plate image → Gemini reads real plate → NOT_FOUND (proves live Vision).  
5. Download PDF.  
6. Show history entry and analytics.  
7. Optionally show startup log snippet proving **GeminiVisionService**.

### 33.5 Legal & Ethics Notice

SentinelANPR AI is an **assistive** policing technology. Outputs may be incorrect. Enforcement actions must follow applicable law, departmental SOP, and human judgment. Facial identity and biometric expansions require separate legal authorization.

### 33.6 Document Size Note

This PRD is intentionally dense and section-complete for enterprise / hackathon evaluators. When exported to PDF with standard corporate styles (11pt body, 1" margins, diagrams), length falls in the **~45–60 page** band depending on pagination and figure placement.

### 33.7 Approval Block

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | ________________ | ________ | ________ |
| Software Architect | ________________ | ________ | ________ |
| Technical Lead | ________________ | ________ | ________ |
| AI Solution Architect | ________________ | ________ | ________ |
| Domain Sponsor | ________________ | ________ | ________ |

---

**End of Document — SentinelANPR AI PRD v2.0**

*AI-Powered Smart Vehicle Verification & Investigation Platform · Prakasam Police Hackathon*
