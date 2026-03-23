# Reference Gaps

**Version:** 20260323 V1
**Build-ref:** oneshot/GAME/2026-03-22.1
**Purpose:** Features not yet specified, organized by target spec file. Drives iteration priority.

> Format: Sections are spec filenames. `(NEW)` = file does not exist yet. Each gap is a checkbox: `- [ ]` open, `- [x]` specified. Include GAME reference file, priority (P0=critical → P10=someday), and one-line description.

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Must have — blocks other work |
| P1 | Must have — core feature gap |
| P2 | Should have — important for quality |
| P3 | Should have — operational feature |
| P4 | Should have — testing/validation |
| P5 | Nice to have — analytics/intelligence |
| P6 | Nice to have — spec tooling |
| P7 | Nice to have — publishing polish |
| P8 | Someday — infrastructure improvements |
| P9–P10 | Backlog |

---

## FUNCTIONALITY.md

- [ ] **P0 — Service Catalog API (Flow 12):** `GET /api/catalog` returns every project, its endpoints, bin/ scripts, health path, port. GAME ref: `routes.py` catalog endpoints.
- [ ] **P0 — Script Endpoint API (Flow 11):** `POST /api/{name}/run/{script}` exposes bin/ scripts as REST. GAME ref: `routes.py` script endpoints.
- [ ] **P0 — Project Health API (Flow 13):** `GET /api/{name}/health` proxies to each project's health endpoint. GAME ref: `routes.py` health proxy.
- [ ] **P0 — CLI/Bash Gateway:** `bin/game-cli.sh` wrapper for catalog, run, health commands from bash without curl.
- [ ] **P2 — Heartbeat Polling (Flow 6):** Background poller not implemented. GAME ref: `monitoring.py` (82 LOC, concurrent threaded polling, incident cache).
- [ ] **P3 — Schedule Fire (Flow 7):** DB columns exist, cron loop missing. GAME ref: not fully implemented there either.
- [ ] **P3 — Missed-Run Recovery:** Catch up on startup if scheduled run was missed.
- [ ] **P3 — Dynamic Port Management:** Track ports in use, detect conflicts. Spec: "Dynamic Port Management and Forwarding".

## ARCHITECTURE.md

- [ ] **P2 — monitoring.py module:** Health polling module missing from architecture. GAME ref: `monitoring.py`.
- [ ] **P8 — Request timing middleware:** Log requests >50ms. GAME ref: `app.py` timing decorator.
- [ ] **P8 — TTL caches:** Cache workflow states and tag colors (30s). GAME ref: routes.py cache decorators.
- [ ] **P8 — Dead process cleanup:** Detect stale PIDs, mark op_runs as error. GAME ref: spawn.py cleanup.

## SCREEN-TAGS.md (NEW)

- [ ] **P1 — Tag management screen:** `/tags` + CRUD APIs (`/api/tag/add`, `/api/tag/update`, `/api/tag/delete`). Custom tag colors with color picker. GAME ref: `templates/tags.html`, `routes.py` tag endpoints, `data/tag_colors.json`.

## SCREEN-SETTINGS.md (NEW)

- [ ] **P1 — Settings screen:** `/settings` + `/settings/save`. App-level config (PROJECTS_DIR, APP_NAME, port, display prefs). GAME ref: `templates/settings.html`.

## SCREEN-HELP.md (NEW)

- [ ] **P1 — Help screen:** `/help` serving platform documentation. GAME ref: `templates/help.html`.

## SCREEN-ENVIRONMENT.md (NEW)

- [ ] **P1 — Environment screen:** `/environment` showing loaded env vars and config state. GAME ref: `templates/environment.html`.

## SCREEN-PUBLISHER.md

- [ ] **P1 — Publish edit page:** `/publish/edit/<project_id>` for per-project homepage metadata. GAME ref: `templates/publish_edit.html`.
- [ ] **P1 — Publish preview:** Local Astro preview server start/stop at port 4321. GAME ref: `bin/LocalPreview.sh`.
- [ ] **P7 — Card image generation:** Port `bin/generate_card_images.py`. GAME ref: `bin/generate_card_images.py`.

## SCREEN-DASHBOARD.md

- [ ] **P1 — Type-specific templates:** `templates/types/_software_detail.html`, `_book_detail.html`, `_software_row.html`, `_book_row.html`. GAME ref: `templates/types/`.
- [ ] **P1 — Inline row editor:** `/api/project/<id>/edit-row` returns editable form; `/api/project/<id>/row` returns read-only. HTMX swap. GAME ref: `routes.py` edit-row endpoints.
- [ ] **P1 — Links management:** `/api/project/<id>/links/add`, `/links/remove`. GAME ref: `routes.py` link endpoints.
- [ ] **P2 — Project registration:** `/api/register-project` for manual registration. GAME ref: `routes.py` register endpoint.

## SCREEN-PROJECT.md

- [ ] **P2 — Quick edit API:** `/api/project/<id>/quick-edit` saves workflow state + type in one call. GAME ref: `routes.py`.

## UI-GENERAL.md

- [ ] **P2 — Configurable alerting:** Thresholds with snooze/escalation. Spec: "Configurable Alerting".

## DATABASE.md

- [ ] **P8 — Database migrations:** `_run_migrations()` is a no-op. Implement add-column-if-missing. GAME ref: `db.py` migration pattern.
- [ ] **P8 — workflow.json:** Externalize workflow state definitions. GAME ref: `data/workflow.json`.

## tests/ (NEW — no spec file needed)

- [ ] **P4 — Test framework:** Create `tests/` with conftest.py, fixtures (app, client, db).
- [ ] **P4 — Unit tests — db layer:** init_db, query, execute, upsert, migrations.
- [ ] **P4 — Unit tests — scanner:** detect_project, parse_metadata_md, scan_bin_operations.
- [ ] **P4 — Unit tests — operations:** launch, stop, monitor, log capture.
- [ ] **P4 — Unit tests — routes:** All API endpoints.
- [ ] **P4 — Unit tests — publisher:** build_portfolio, card metadata.
- [ ] **P4 — Unit tests — claude_convention:** parse_agents_md, @AGENTS.md redirect.
- [ ] **P4 — Integration tests:** scan → discover → run → check → view log.

## bin/ scripts (NEW — no spec file needed)

- [ ] **P3 — bin/test.sh:** Run test suite.
- [ ] **P3 — bin/PushAndPublish.sh:** Full GitHub Pages publish pipeline.
- [ ] **P3 — bin/LocalPreview.sh:** Astro preview server.
- [ ] **P3 — bin/validate_project.py:** Validate project compliance.
- [ ] **P6 — bin/create_project.py:** Scaffold new projects from templates.

## Unspecified Features (from Features.html)

- [ ] **P5 — Usage analytics:** Port `usage_analyzer.py` (454 LOC). Token tracking, cost estimation, HTML reports.
- [ ] **P5 — AI Transaction Log:** Wire up `ai_decisions` table. Decisions/rationale per build.
- [ ] **P5 — Project Maturity Scorecard:** Measure against standards (tests, docs, health, CLAUDE.md, git).
- [ ] **P5 — Health KPIs:** Compliance, uptime, self-test, spec-drift in one view.
- [ ] **P6 — Specification management:** `has_specs` detection, spec editor UI.
- [ ] **P6 — Spec-to-code traceability:** Specs → commits → tickets linked.
- [ ] **P6 — Common technology rules:** Shared rules across projects.
- [ ] **P6 — Compliance validation:** Guardrails and KPI checks.
- [ ] **P7 — Consistent doc branding:** Standard structure across all projects.
- [ ] **P7 — Diagram export:** Port `bin/export_diagrams.py`. Excalidraw → PNG.
- [ ] **P9 — Smart git commits:** Descriptive labels, auto-commit integration.
- [ ] **P9 — Secrets management:** Detect/protect .env files, warn on commit.
- [ ] **P9 — Project templates/scaffolding:** Jinja2 templates for new projects.
- [ ] **P0 — Published API docs:** Auto-generate API reference at `/api/docs`. Spec: "Published Service API".

---

## Closed
<!-- Gaps that have been fully specified. Check the box above and note the date here. -->

