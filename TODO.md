# TODO

Ideas and tasks collected during specification review (2026-03-13).

---

## High Priority

- [ ] **Project Scaffolding** — Highest-leverage gap. New projects start non-compliant without it. Template library (web service, CLI tool, data pipeline) that generates METADATA.md, CLAUDE.md, bin/ scripts with headers, .env.example. Feature 3 in FEATURES.md.

- [ ] **Scheduling & Cron** — `# Schedule:` header in bin/ scripts. Platform runs operations at declared times. Daily/weekly/cron expressions. Missed-run catch-up. Feature 6.

- [ ] **Update GAME code to read METADATA.md** — GAME still reads `git_homepage.md` and `Links.md` in places. Publisher needs to read from METADATA.md. scanner.py needs update.

- [ ] **Environment Management tooling** — .env.example convention is defined in CLAUDE_RULES but no tooling exists to detect drift, missing vars, or committed secrets. Feature 13.

## Medium Priority

- [ ] **Job Pipelines** — Multi-step workflows (YAML-defined). Fan-out/fan-in, retry policy, pipeline status in dashboard. Inspired by Airflow DAGs but much simpler. Feature 7.

- [ ] **Event Log** — Centralized timeline of all platform events (state transitions, operations, health changes, deployments). Filterable, exportable. Feature 10.

- [ ] **Resource Limits** — `# MaxMemory:` and `# Timeout:` in bin/ headers. Enforce via ulimit/cgroups. Kill runaway processes. Feature 20.

- [ ] **Secrets Management** — Encrypted secrets store, runtime injection via env vars, rotation tracking, access audit. Feature 19.

- [ ] **Monitoring & Health Checks** — Service health polling with liveness/readiness checks. Alert on failure. Uptime tracking. Feature 8.

- [ ] **Compliance Verification gaps** — verify.py exists but doesn't cover all CLAUDE_RULES yet. Add checks for: .env.example presence, health endpoint declaration, CLAUDE.md required sections. Feature 11 at 70%.

## Low Priority

- [ ] **Desired State Reconciliation** — Kubernetes-inspired. `desired_state:` in METADATA.md. Reconciliation loop restarts crashed services, stops idle ones. Feature 21.

- [ ] **Rolling Restarts** — Stop/start one instance at a time. Health check before proceeding. Rollback on failure. Feature 22.

- [ ] **Namespace Isolation** — Logical environments (dev, staging, prod). Config overrides per namespace. Port range partitioning. Feature 23.

- [ ] **Service Discovery & Routing** — Projects find each other by name (`@project-name/api`). Platform resolves to host:port. Feature 24.

- [ ] **Workflow States UI** — Data model is designed but UI is not built. Kanban board, ticket detail, AI transaction log viewer. Feature 12.

## Decisions Needed

- [ ] **Stack directory** — Contains technology reference files (flask.md, sqlite.md, etc.) used by `generate-prompt.sh`. Useful for building new projects from scratch, but not part of the specification hierarchy. Keep as reference material or move to archive? Currently kept.

- [ ] **Template HTML files** — `_root_index_template.html` and `_project_index_template.html` drive the documentation viewer. The markdown-to-HTML converter is very basic (no code block rendering, no proper list nesting). Consider upgrading to a proper markdown library or accepting the limitations.

- [ ] **generate-prompt.sh and validate.sh** — These tools reference the old STACK.yaml pattern. Should they be updated to work with METADATA.md `stack:` field, or kept as-is since they serve a different purpose (full AI build prompts)?

## Ideas From Archive

- [ ] **Three-layer methodology** (from archive/METHODOLOGY.md) — Layer 1: what the product does (features), Layer 2: contracts (binding layer), Layer 3: how it's built (tech spec). This is a good mental model. Currently implicit in FEATURES→CLAUDE_RULES→GAME. Could be made explicit in README.

- [ ] **Contract-earns-capability pattern** (from archive/THE-CONTRACT.md) — "A project adds the file; the platform discovers the capability." This design principle should be preserved. Currently embedded in CLAUDE_RULES and PROJECT-DISCOVERY but worth calling out as a first principle.

- [ ] **Audio/image attachments on tickets** (from WORKFLOW-STATES) — Useful for capturing voice notes or screenshots during ideation. Low priority but good UX for solo practitioners.

- [ ] **Per-ticket cost attribution** (from USAGE-ANALYTICS) — Link AI session costs to specific workflow tickets. Requires integration between USAGE-ANALYTICS and WORKFLOW-STATES.
