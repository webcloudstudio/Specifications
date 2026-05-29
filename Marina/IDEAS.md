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

## Spikes (runnable investigations to resolve before/at build)

Each spike is a concrete question the owner can ask to have run, with a decision to follow. They are
also seeded into the relevant `## Open Questions` sections so the build tooling can surface them.

1. **API Gateway IAM/SigV4 across heterogeneous home networks.** Confirm that cross-account AWS
   Organization principals can invoke an IAM-authorised HTTP API from arbitrary home networks with no
   public anonymous path. Deliverable: the resource policy + invoke-role trust pattern to encode.
2. **Repo-access → capability-access binding.** Decide how the "you hold the repo key" signal is
   captured. Default: an Org-side ACL table in DynamoDB written at onboarding (no per-call GitHub
   dependency). Spike validates how onboarding verifies repo access (GitHub token check at onboard time)
   and whether the gate caches the ACL per warm Lambda.
3. **Terraform remote backend bootstrap.** Validate the local-state `backend/` bootstrap then
   backend-migrate flow for `foundation/`/`services/`, resolving the chicken-and-egg cleanly.
4. **DynamoDB single-table schema validation.** Replay every access pattern in `DATABASE.md` against a
   local DynamoDB (or `moto`) to confirm zero scans and correct `begins_with` subtree reads.
5. **GitHub Actions OIDC → Org member accounts.** Stand up the OIDC provider + least-privilege deploy
   role with a repo-scoped trust policy; confirm no static keys are needed.
6. **`marina` library distribution via `uv`.** Confirm `uv add git+...@tag` pins cleanly and that a
   version bump flows into consumers via `uv.lock`; settle the library repo name and tagging flow.
