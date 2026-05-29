# Marina — Backlog, Deferred Phases, and Spikes

This file holds deferred-phase plans and the spikes to run before/at build. It is not built in
Phase 1/2.

---

## Deferred Phase 3 — Dockerization / Fargate

A large, self-contained phase the owner will tackle before later phases. Intent:

- **Conform-time Dockerfile generation.** Conforming a project also generates a `Dockerfile` (and
  `.dockerignore`) from `METADATA.md` — the project still runs locally exactly as before; the Dockerfile
  simply captures much of what conformity already standardises. If a project already has a Dockerfile,
  use it.
- **Fargate, not EKS.** Launch dockerized projects on **ECS Fargate** (per-second billing, scales to
  zero between runs). EKS is explicitly rejected — its standing control-plane cost contradicts the
  near-zero-cost goal.
- **One service catalog, port-forwarded.** Each launched project gets a routed/port-forwarded call so
  the cloud catalog can reach it, making Marina a single catalog spanning local and cloud-run projects.
- **Guarded direct invocation.** Allow direct invocation of selected non-lifecycle `bin/` scripts
  (never `start`) as a future security service for third-party projects — a guardrailed perimeter around
  modular code.

Reference the GAME `ARCHITECTURE-DOCKER.md` for the local container model to reuse.

## Deferred — AgentCore (Secure Capability / MCP Sharing)

High-level only; re-analysed after Phase 1/2 findings. Bedrock **AgentCore Gateway** would expose the
capability catalog as MCP tools to the circle of trust with managed OAuth, and **AgentCore Identity**
would broker agent credentials — retiring any raw-port `.mcp.json` exposure. Depends on the Phase 1
catalog existing. Pricing is usage-based and must be confirmed before committing.

## Deferred — Browser UI / Screens

No screens are built in Phase 1/2 — features are verified via test scripts and CloudWatch. A later UI
phase reuses the GAME `SCREEN-*` designs: three colour-coded, left-to-right experiences (Welcome/Onboard,
Operations, Prototyper), feature-forward, with a "live (local) vs last-known (cloud)" badge so cloud
reads never masquerade as live.

---

## Spikes (resolved)

Each spike named the file its findings belong to and has been **run and reconciled** into that file
(per the spike standard in `SPECIFICATION_CONTRACT.md`). Full investigation write-ups are kept in
`SPIKE_RESULTS.md` as a decision log.

| # | Spike | Target file(s) | Outcome |
|---|-------|----------------|---------|
| 1 | API Gateway IAM/SigV4 across home networks | `stack/aws-api-gateway.md`, `stack/marina-library.md` | HTTP API v2 + per-member invoke role; no IP allow-list, no resource policy, REST v1 rejected |
| 2 | Repo-access → capability-access binding | `FEATURE-ACCESS-CONTROL.md`, `ARCHITECTURE.md` | GitHub token at onboard (never stored); 5-min in-process gate cache; nightly re-sync; admin-only onboard |
| 3 | Terraform remote backend bootstrap | `stack/terraform.md` | `backend/` stays local; `foundation/`/`services/` init directly to S3 — no migrate step |
| 4 | DynamoDB single-table schema validation | `DATABASE.md`, `stack/aws-dynamodb.md` | All 12 patterns valid, zero scans; condition uses `attribute_not_exists(SK)`; 30-day event TTL |
| 5 | GitHub Actions OIDC → Org member accounts | `stack/github-actions.md` | OIDC provider + repo-scoped trust; no static keys |
| 6 | `marina` library distribution via `uv` | `stack/marina-library.md`, `FEATURE-MARINA-LIB.md` | repo `marina-lib`; `uv add git+...@tag` pins to SHA in lock; no escape hatch |
