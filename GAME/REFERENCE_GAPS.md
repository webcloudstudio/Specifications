# Reference Gaps

**Version:** 20260326 V3
**Build-ref:** oneshot/GAME/2026-03-26.1
**Purpose:** Features not yet specified, organized by target specification file. Drives iteration priority.

> Format: Sections are specification filenames. `(NEW)` = file does not exist yet. Each gap is a checkbox: `- [ ]` open, `- [x]` specified. Include GAME reference file, priority (P0=critical → P10=someday), and one-line description.

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Must have — blocks other work |
| P1 | Must have — core feature gap |
| P2 | Should have — important for quality |
| P3 | Should have — operational feature |
| P4 | Should have — testing/validation |
| P5 | Nice to have — analytics/intelligence |
| P6 | Nice to have — specification tooling |
| P7 | Nice to have — publishing polish |
| P8 | Someday — infrastructure improvements |
| P9–P10 | Backlog |

---

## FUNCTIONALITY.md

- [x] **P0 — Service Catalog API (Flow 12):** `GET /api/catalog` returns every project, its endpoints, bin/ scripts, health path, port. Specified in FEATURE-SERVICE-CATALOG.md.
- [x] **P0 — Script Endpoint API (Flow 11):** `POST /api/{name}/run/{script}` exposes bin/ scripts as REST. Specified in FEATURE-SERVICE-CATALOG.md.
- [x] **P0 — Project Health API (Flow 13):** `GET /api/{name}/health` proxies to each project's health endpoint. Specified in FEATURE-HEALTHCHECK.md.
- [ ] **P0 — CLI/Bash Gateway:** `bin/game-cli.sh` wrapper for catalog, run, health commands from bash without curl. No specification yet.
- [x] **P2 — Heartbeat Polling (Flow 6):** Background poller fully specified in FEATURE-HEALTHCHECK.md (concurrent threading, state transitions, uptime_pct).
- [x] **P3 — Schedule Fire (Flow 7):** Cron loop specified in SCREEN-MONITORING-SCHEDULER.md; startup catch-up in FUNCTIONALITY.md Flow 7.
- [x] **P3 — Missed-Run Recovery:** FUNCTIONALITY.md Flow 7 startup catch-up fires ONE immediate run for each missed schedule.
- [ ] **P3 — Dynamic Port Management:** Track ports in use, detect conflicts at scan time. Not yet specified.

## ARCHITECTURE.md

- [x] **P1 — monitoring.py / healthcheck.py module:** Full `Health Monitor (monitoring.py)` section now in ARCHITECTURE.md with poller thread, log ingestor thread, and provided functions.
- [x] **P1 — scheduler.py module:** Full `Scheduler (scheduler.py)` section now in ARCHITECTURE.md with cron loop, catch-up logic, and provided functions.
- [x] **P1 — Routes table update:** Routes table in ARCHITECTURE.md now includes all FEATURE-SERVICE-CATALOG and FEATURE-HEALTHCHECK routes (lines 115–125).
- [ ] **P8 — Request timing middleware:** Log requests >50ms.
- [ ] **P8 — TTL caches:** Cache workflow states and tag colors (30s).
- [ ] **P8 — Dead process cleanup:** Detect stale PIDs, mark op_runs as error.

## DATABASE.md

- [x] **P1 — Add FEATURE-HEALTHCHECK tables:** `health_check_log`, `log_positions`, `log_filter` now documented in DATABASE.md schema section with summary table and retention notes.
- [x] **P1 — Promote tag_colors to DB table:** Full `tag_colors` schema now in DATABASE.md; migration path from `data/tag_colors.json` documented.
- [ ] **P1 — has_tests and has_specs flags:** Remain in DATABASE.md Open Questions only — not yet added to the `projects` table schema or Field Source Mapping table.
- [ ] **P3 — git_last_commit_date column:** Still in Open Questions — not added to projects table schema. Requires `git log` during scan.
- [x] **P8 — Database migrations:** `_add_column_if_missing()` pattern documented in DATABASE.md Conventions section.

## SCREEN-SETTINGS-LOGFILTER.md (NEW)

- [ ] **P2 — Log filter rule editor:** `log_filter` table is defined in FEATURE-HEALTHCHECK.md with seed rules, but no UI screen exists to view, edit, add, or reorder classification rules. Needed for production tuning.

## SCREEN-PROTOTYPES-DETAIL.md (NEW)

- [ ] **P2 — Prototype detail view:** `GET /prototypes/{name}` is referenced in SCREEN-PROTOTYPES-LIST.md but has no specification. Should show parsed specification files as a rendered HTML index with file list, Open Questions, and links to the oneshot flow.

## SCREEN-SETTINGS-WORKFLOWS.md (NEW)

- [ ] **P3 — Workflow type management screen:** `workflow_types` table is seeded on startup; SCREEN-PROJECTS-WORKFLOW.md notes "until that screen exists, types are edited directly in the DB." Needs a proper settings screen for CRUD on workflow type definitions.

## SCREEN-PUBLISHER.md

- [x] **P1 — Publish edit page:** Cover is provided by the SCREEN-PUBLISHER.md Build/Publish/Preview/Homepage sections. Per-project card editing is handled via Configuration screen (`card_show`, `card_title`, etc.).
- [ ] **P1 — Publish preview:** Local Astro preview server start/stop at port 4321. SCREEN-PUBLISHER.md references this but `bin/LocalPreview.sh` is not specified.
- [ ] **P7 — Card image generation:** `bin/generate_card_images.py` not yet specified.

## SCREEN-PROJECTS-VALIDATION.md

- [ ] **P2 — Schedule nightly validation:** `Validate All` triggered automatically on schedule. Not yet wired to scheduler. When specified, add a `validation_schedule` key to settings table and reference FUNCTIONALITY.md Flow 7.

## SCREEN-WORKFLOW.md

- [ ] **P2 — AI agent submission mechanism:** READY tickets can be "submitted to an AI agent" but the trigger mechanism (queue, webhook, API call to Claude) is unspecified. Needs a concrete flow or FEATURE-AI-SUBMISSION.md.

## tests/ (no specification file needed)

- [ ] **P4 — Test framework:** Create `tests/` with conftest.py, fixtures (app, client, db).
- [ ] **P4 — Unit tests — db layer:** init_db, query, execute, upsert, migrations.
- [ ] **P4 — Unit tests — scanner:** detect_project, parse_metadata_md, scan_bin_operations.
- [ ] **P4 — Unit tests — operations:** launch, stop, monitor, log capture.
- [ ] **P4 — Unit tests — routes:** All API endpoints.
- [ ] **P4 — Unit tests — publisher:** build_portfolio, card metadata.
- [ ] **P4 — Unit tests — claude_convention:** parse_agents_md, @AGENTS.md redirect.
- [ ] **P4 — Integration tests:** scan → discover → run → check → view log.

## bin/ scripts (no specification file needed)

- [ ] **P0 — Published API docs:** Auto-generate API reference at `/api/docs`. No specification yet.
- [ ] **P3 — bin/test.sh:** Run test suite.
- [ ] **P3 — bin/PushAndPublish.sh:** Full GitHub Pages publish pipeline (referenced in FUNCTIONALITY.md Flow 5, not yet a formal script specification).
- [ ] **P3 — bin/LocalPreview.sh:** Astro preview server (referenced in SCREEN-PUBLISHER.md).
- [ ] **P6 — bin/create_project.py:** Scaffold new projects from templates (lives in GAME project, referenced from Specifications AGENTS.md).

## Unspecified Features (backlog)

- [ ] **P5 — Usage analytics:** `usage_analyzer.py` (454 LOC). Token tracking, cost estimation, HTML reports.
- [ ] **P5 — AI Transaction Log UI:** `ai_decisions` table exists in DATABASE.md; no screen renders it outside of ticket detail.
- [ ] **P5 — Health KPIs dashboard:** Compliance, uptime, self-test, specification-drift aggregated in one view. Partially covered by SCREEN-PROJECTS-VALIDATION.md.
- [ ] **P6 — Specification-to-code traceability:** Specifications → commits → tickets linked.
- [ ] **P7 — Consistent doc branding:** Standard structure across all projects.
- [ ] **P9 — Smart git commits:** Descriptive labels, auto-commit integration.
- [ ] **P9 — Secrets management:** Detect/protect .env files, warn on commit.

---

## Closed

| Gap | Resolved in | Date |
|-----|-------------|------|
| P0 Service Catalog API | FEATURE-SERVICE-CATALOG.md | 2026-03-23 |
| P0 Script Endpoint API | FEATURE-SERVICE-CATALOG.md | 2026-03-23 |
| P0 Project Health API | FEATURE-HEALTHCHECK.md | 2026-03-23 |
| P2 Heartbeat Polling | FEATURE-HEALTHCHECK.md | 2026-03-23 |
| P3 Schedule Fire | SCREEN-MONITORING-SCHEDULER.md | 2026-03-25 |
| P3 Missed-Run Recovery | FUNCTIONALITY.md Flow 7 | 2026-03-20 |
| P1 Tag management screen | SCREEN-SETTINGS-TAGS.md | 2026-03-25 |
| P1 Settings screen | SCREEN-SETTINGS-GENERAL.md | 2026-03-26 |
| P5 Project Maturity Scorecard | SCREEN-PROJECTS-VALIDATION.md (conformity levels) | 2026-03-25 |
| P6 Specification management | SCREEN-PROTOTYPES-LIST.md + SCREEN-PROJECTS-WORKFLOW.md | 2026-03-24 |
| P1 monitoring.py module | ARCHITECTURE.md (Health Monitor section) | 2026-03-26 |
| P1 scheduler.py module | ARCHITECTURE.md (Scheduler section) | 2026-03-26 |
| P1 Routes table update | ARCHITECTURE.md (routes table lines 115–125) | 2026-03-26 |
| P1 FEATURE-HEALTHCHECK tables in DATABASE.md | DATABASE.md (health_check_log / log_positions / log_filter section) | 2026-03-26 |
| P1 tag_colors DB table | DATABASE.md (tag_colors schema + migration note) | 2026-03-26 |
| P8 Database migrations | DATABASE.md Conventions (_add_column_if_missing note) | 2026-03-26 |
