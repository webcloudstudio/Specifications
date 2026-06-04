# FUNCTIONALITY: Feature Index

| Field       | Value |
|-------------|-------|
| Version     | 20260603 V2 |
| Description | One-paragraph index of Marina features by phase; detail lives in the individual FEATURE-*.md files. |

**Description:** High-level index of Marina's features and their build phase. Implementation detail
(triggers, sequences, reads/writes, tests) lives in the per-feature files, which is what the dependency
graph and minimal builds target.

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
