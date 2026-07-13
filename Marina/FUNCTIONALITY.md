# FUNCTIONALITY: Feature Index

| Field       | Value |
|-------------|-------|
| Version     | 20260603 V2 |
| Description | One-paragraph index of Marina features by phase; detail lives in the individual FEATURE-*.md files. |

**Description:** High-level index of Marina's product capabilities. The initial build is deliberately
small: welcome and registration, capability discovery and storage, and the project explorer. The local
control plane is primary; the private AWS plane is a later integration surface.

## Product Capability Ownership

| Capability | Home | Primary screens/features |
|------------|------|--------------------------|
| Welcome and repository registration | SETUP | `SCREEN-SETUP-SUMMARY.md`, `SCREEN-SETUP-REPOSITORIES.md`, `FEATURE-PROJECT-REGISTRATION.md` |
| Project identity and organization | PROJECTS | `SCREEN-PROJECTS-DASHBOARD.md`, `SCREEN-PROJECTS-DETAIL.md`, `FEATURE-PROJECT-ORGANIZATION.md` |
| Capability discovery and storage | Scanner/catalog | `FEATURE-CAPABILITY-DISCOVERY.md`, `FEATURE-SCANNER.md`, `DATABASE.md` |
| Capability exploration | PROJECTS | `SCREEN-PROJECTS-CAPABILITIES.md`, `FEATURE-SERVICE-CATALOG.md` |
| Standards and conformance | PROJECTS / Validation | Deferred after initial explorer slice |
| Project workflow | PROJECTS / Workflow | `SCREEN-PROJECTS-WORKFLOW.md` |
| Runs, logs, health, schedules, and events | MONITORING | `SCREEN-MONITORING-*`, batch runner, health check |
| AWS integration and private publication | Integration features | `FEATURE-CATALOG-*.md`, `FEATURE-REPORT-INGEST.md`, `FEATURE-S3-SHARE.md` |

Project organization is the source of truth for namespace, tags, lifecycle, and workflow assignment.
Monitoring consumes that registry; it does not create a second project list.

---

## Phase 1 — Private Read / Ingest / Report Surface

- **Infrastructure (Terraform)** (`FEATURE-INFRA.md`) — the layered `infra/` Terraform tree
  (`backend/`, `foundation/`, `services/`, `modules/`) that provisions the entire AWS broadcast plane:
  the DynamoDB catalog table, SQS queues, S3 buckets, IAM/OIDC roles, Lambdas, and the API Gateway whose
  `api_url` output is `MARINA_API_URL`. Real HCL — every other cloud feature is deployed by it.
- **Marina Library** (`FEATURE-MARINA-LIB.md`) — the `marina` Python package: the single cloud boundary
  (`catalog`, `report`, `queue`, `share`). Every other feature depends on it. Published in its own git
  repo; consumers add it via `uv`.
- **Catalog Publish** (`FEATURE-CATALOG-PUBLISH.md`) — the local agent upserts a project's metadata and
  capabilities into DynamoDB through `POST /catalog`.
- **Catalog Read** (`FEATURE-CATALOG-READ.md`) — private 24×7 read of the org tree, one project, or the
  capability list via IAM-authorised `GET` endpoints.
- **Report Ingest** (`FEATURE-REPORT-INGEST.md`) — heartbeat and event ingestion (`POST /heartbeat`,
  `POST /events`) plus per-project health aggregation (`GET /health/{project}`).
- **Access Control** (`FEATURE-ACCESS-CONTROL.md`) — Org-identity authorisation that mirrors git-repo
  access; the shared gate every read/invoke path calls.

## Local Control Plane — Product Scope

## Initial Build

The initial build includes only these end-to-end slices:

1. **Welcome and Registration:** configure the projects directory, discover local repositories, clone
   repositories from configured sources, preview identity/provenance, and explicitly register projects.
2. **Capability Discovery and Storage:** parse `METADATA.md`, `AGENTS.md`/`CLAUDE.md`, `bin/` CommandCenter
   headers, and MCP declarations; persist normalized records, evidence, hashes, warnings, and scan history.
3. **Project Explorer:** browse registered projects and their discovered metadata, git state, capabilities,
   warnings, and provenance.

The initial build does not invoke, expose, publish, schedule, or remotely share capabilities.

- **Project Organization** (`FEATURE-PROJECT-ORGANIZATION.md`) — the registry and user-managed grouping,
  tagging, workflow, and lifecycle model.
- **Scanner** (`FEATURE-SCANNER.md`) — discovery and reconciliation of repositories obtained during setup
  or found in the projects directory.
- **Service Catalog** (`FEATURE-SERVICE-CATALOG.md`) — project capabilities, operations, links, and
  schedules discovered from conformed project documentation.
- **Batch Runner** (`FEATURE-BATCH-RUNNER.md`) — controlled local execution with run state and logs.
- **Health Check** (`FEATURE-HEALTHCHECK.md`) — health polling and state-change events.
- **Workflow Service** (`FEATURE-WORKFLOW-SERVICE.md`) — project-scoped tickets and transitions; its UI
  is owned by `SCREEN-PROJECTS-WORKFLOW.md`.

## Phase 2 — Durable Ingest and Company Share

- **Async Queue** (`FEATURE-ASYNCQUEUE.md`) — SQS-backed store-and-forward: producers submit 24×7, the
  local agent drains when alive. Replaces GAME's JSONL queue.
- **Voice Capture** (`FEATURE-VOICE-CAPTURE.md`) — capture audio inside the firewall to S3 and enqueue a
  transcription job; Whisper transcription runs locally.
- **S3 Company Share** (`FEATURE-S3-SHARE.md`) — a deliberately simple per-user-prefix file share for
  the circle of trust.

## Deferred (documented in IDEAS.md, not built here)

- Phase 3 — Dockerization / Fargate launch of conformed projects.
- Later — AgentCore (secure capability/MCP sharing) and a browser UI.

## Open Questions

- Should Phase 1 expose a single combined `GET /catalog` that includes last-known health inline, or keep
  health on its own `GET /health/{project}` endpoint? Current design keeps them separate for cacheability.
