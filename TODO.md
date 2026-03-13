# TODO

Ideas and tasks collected during specification review (2026-03-13).

---

## High Priority

- [ ] **Project Scaffolding** — Highest-leverage gap. Template library that generates METADATA.md, AGENTS.md, CLAUDE.md (pointer), bin/common.sh, bin/start.sh, .env.example, .gitignore. One-shot project creation. Feature 3.

- [ ] **Update GAME code to read METADATA.md** — GAME still reads `git_homepage.md` and `Links.md`. Scanner, publisher, and dashboard need updating. Also update to read AGENTS.md instead of CLAUDE.md for bookmarks/endpoints.

- [ ] **Implement bin/common.sh standard** — Create a reference common.sh with get_metadata(), PORT, PROJECT_NAME. Test it across existing projects. This is the foundation for all script integration.

- [ ] **Secrets file convention** — Create `$PROJECTS_DIR/.secrets` file. Update common.sh to source it. Document in CLAUDE_RULES (done). Implement in GAME and other projects.

- [ ] **Update verify.py** — Add checks for: AGENTS.md presence, .env.example when .env exists, bin/common.sh, display_name derivation, version format (YYYY-MM-DD.N), git initialized for ACTIVE+.

## Medium Priority

- [ ] **Scheduling & Cron** — Platform reads `# Schedule:` from bin/ headers. Runs operations at declared times. Missed-run catch-up on startup. Feature 6.

- [ ] **Monitoring & Health Checks** — SCREEN-MONITORING. Poll services for `port:` + `health:` from METADATA.md. UP/DOWN/UNKNOWN states. Alert on transition. Feature 8.

- [ ] **Environment Management tooling** — Detect .env/.env.example drift, warn on committed .env, compare vars across projects. Feature 13.

- [ ] **Event Log** — Centralized timeline. Parse `[$PROJECT_NAME] Event:` lines from logs. Filterable, exportable. Feature 10.

- [ ] **Compliance Verification expansion** — verify.py at 70%. Add: health endpoint responding, AGENTS.md required sections, date format validation, namespace/desired_state field validation.

- [ ] **Documentation generation** — Standard bin/build_documentation.sh that generates doc/index.html from METADATA.md + AGENTS.md + markdown files. Template-based. Feature 15.

## Low Priority

- [ ] **Job Pipelines** — Multi-step workflows (YAML-defined). Fan-out/fan-in, retry. Feature 7.

- [ ] **Resource Limits** — `# Timeout:` and `# MaxMemory:` enforcement. Feature 20.

- [ ] **Desired State Reconciliation** — `desired_state: running` triggers auto-restart. Feature 21.

- [ ] **Namespace Isolation** — Filter and config overrides by namespace. Feature 23.

- [ ] **Workflow States UI** — Kanban board, ticket detail, AI transaction log viewer. Feature 12.

- [ ] **Rolling Restarts** — Health-gated restart cycle. Feature 22.

## Decisions Made

- [x] **METADATA.md format** — Line-based key: value in a markdown file. Not YAML. Parsed with grep/cut.
- [x] **AGENTS.md replaces CLAUDE.md** — CLAUDE.md becomes a pointer (`@AGENTS.md`). Vendor-neutral.
- [x] **Service discovery** — Just read METADATA.md. No `@project-name` syntax. The metadata file IS the registry.
- [x] **Version format** — `YYYY-MM-DD.N` (e.g., 2026-03-13.3). Minor increments per commit.
- [x] **Date format** — Always `yyyymmdd` or `yyyymmdd_hhmmss` for file sorting.
- [x] **Desired state values** — `running` (stays up) or `on-demand` (manual start/stop).
- [x] **Namespace values** — `development`, `qa`, `production`, or custom name.
- [x] **GAME specs by screen** — Removed duplicate standards, organized by UI screen.
- [x] **Git integration simplified** — Just a Push button when unpushed commits exist. Async scan.
- [x] **Stack directory** — Keep as reference for generate-prompt.sh. Not part of spec hierarchy.

## Ideas From Archive

- [ ] **Three-layer methodology** (archive/METHODOLOGY.md) — Layer 1: features, Layer 2: contracts, Layer 3: tech spec. Good mental model. Currently implicit in FEATURES→CLAUDE_RULES→GAME.

- [ ] **Contract-earns-capability** (archive/THE-CONTRACT.md) — "Add the file; platform discovers the capability." First principle worth calling out.

- [ ] **Audio/image attachments on tickets** — Voice notes and screenshots during ideation. Good UX for solo practitioners.

- [ ] **Per-ticket cost attribution** — Link AI session costs to workflow tickets.
