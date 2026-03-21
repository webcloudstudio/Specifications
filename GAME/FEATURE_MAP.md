# GAME Feature Map

**Version:** 20260320 V2
**Description:** Feature map: complete list of system features

**Complete catalog of project attributes, platform features, and operational capabilities.**

This is the primary feature reference for GAME. It defines what the platform knows about projects, what it can do with them, and what capabilities it provides automatically. All SCREEN-*.md files reference features defined here. For field types, column definitions, and constraints, see DATABASE.md.

---

## I. Project Identity

### Naming (Consolidation)

The platform has too many name/description fields. The canonical model:

| Field | Source | Purpose |
|-------|--------|---------|
| `name` | METADATA.md | Machine slug, matches directory name |
| `display_name` | METADATA.md | Human-readable name for all UI display |
| `short_description` | METADATA.md | One sentence, shown in lists and cards |
| `git_repo` | METADATA.md | Full HTTPS URL to repository |

**Derived / Override fields** (should default from the above, only stored separately when user explicitly overrides):

| Field | Defaults From | Override Purpose |
|-------|---------------|------------------|
| `card_title` | `display_name` | Portfolio card shows a different name |
| `card_desc` | `short_description` | Portfolio card shows a different summary |
| `title` | `display_name` | Legacy — **candidate for removal** |
| `description` | `short_description` | Longer narrative — rarely used, store in `extra` if needed |

**Rule:** If `card_title` is empty, use `display_name`. If `card_desc` is empty, use `short_description`. Never require the user to enter the same text twice.

### Visual Identity (NEW)

| Field | Source | Purpose |
|-------|--------|---------|
| `color` | METADATA.md | Project accent color for dashboard cards, charts, badges |
| `icon` | METADATA.md | Emoji or icon identifier for quick visual scanning |
| `logo` | METADATA.md | Path to project logo image (relative to project dir) |

**Usage:** The dashboard row shows the icon next to the project name. The color tints the project's card border, tag pills, and chart segments. The logo appears in the project detail view and on portfolio cards (falls back to a colored initial if missing).

**Default behavior:** If `color` not set, derive from a hash of the project name (deterministic palette). If `icon` not set, use the first letter of `display_name` in a colored circle.

### Classification

| Field | Values | Purpose |
|-------|--------|---------|
| `project_type` | `software`, `book`, custom | Determines UI template and default operations |
| `category` | `infrastructure`, `client`, `tool`, `library`, `experiment` | High-level grouping for filtering/reporting |
| `owner` | Name or handle | Who maintains this project |
| `tags` | Freeform csv | Cross-cutting labels for filtering |

### Lifecycle

| Field | Values | Purpose |
|-------|--------|---------|
| `status` | IDEA, PROTOTYPE, ACTIVE, PRODUCTION, ARCHIVED | Development phase |
| `is_active` | Auto | false = removed from disk |
| `desired_state` | running, on-demand | Service always-on vs. manual start |
| `namespace` | development, qa, production, custom | Environment segregation |

### Technology & Infrastructure

| Field | Source | Purpose |
|-------|--------|---------|
| `stack` | METADATA.md | Slash-separated tech summary |
| `port` | METADATA.md | Service port (if applicable) |
| `health_endpoint` | METADATA.md | Health check path (default `/health`) |
| `deploy_url` | METADATA.md | Production/live URL |
| `version` | METADATA.md | YYYY-MM-DD.N format |

### Auto-Detected Flags (Scanner)

| Flag | Detection Method | Purpose |
|------|------------------|---------|
| `has_git` | `.git/` directory exists | Show git status, push button |
| `has_venv` | `venv/` or `.venv/` exists | Activate before running scripts |
| `has_node` | `node_modules/` or `package.json` exists | npm-based operations |
| `has_claude` | `CLAUDE.md` or `AGENTS.md` exists | Claude-integrated project |
| `has_tests` | `tests/` or `bin/test.sh` exists | Show test runner button |
| `has_docs` | `doc/index.html` exists | Show documentation link |
| `has_specs` | Corresponding dir in Specifications/ | Specification management link |

### Portfolio & Publishing

| Field | Defaults From | Purpose |
|-------|---------------|---------|
| `show_on_homepage` | false | Include in published portfolio |
| `card_title` | `display_name` | Override title for portfolio card |
| `card_desc` | `short_description` | Override description for card |
| `card_tags` | `tags` | Override tags for card filtering |
| `card_type` | `project_type` | Override type badge |
| `card_url` | `deploy_url` or `git_repo` | Override link URL |
| `card_image` | `logo` | Override card thumbnail |

### Git State, Timestamps, and Extensions

Git state (`git_branch`, `git_dirty`, `git_unpushed`, `git_last_commit`), timestamps (`created_at`, `updated_at`, `last_scanned`), and the `extra` JSON blob are scanner-populated fields. See DATABASE.md → `projects` for column definitions.

The type registry (`models.py`) defines which fields each type uses. New types add entries to `PROJECT_TYPES` and two HTML partials.

---

## II. Operations & Script Registry

### Discovery

Scripts in `bin/` with the `# CommandCenter Operation` marker in the first 20 lines are automatically registered on scan.

### Operation Attributes

| Attribute | Header | Purpose |
|-----------|--------|---------|
| `script_name` | (filename) | Operation identifier |
| `script_path` | (relative path) | Execution path |
| `display_name` | (derived) | Button label |
| `category` | `# Category:` | Group: `service`, `maintenance`, `build`, `deploy` |
| `port` | `# Port:` | Service port override |
| `health_path` | `# Health:` | Health endpoint for monitoring |
| `schedule` | `# Schedule:` | Cron expression for automated runs |
| `timeout` | `# Timeout:` | Max execution seconds |

See DATABASE.md → `operations` for the full schema.

### Default Operations (by stack)

| Stack | Operation | Command |
|-------|-----------|---------|
| Flask | Start Server | `flask run --port {port}` |
| Django | Start Server | `python manage.py runserver {port}` |
| Node | Start Dev | `npm run dev` |
| Astro | Start Dev | `npm run dev` |
| Bash | Run Script | `./start.sh` |

### Run Records

Operation runs are tracked per-execution. See DATABASE.md → `op_runs` for the schema.

### Process State Machine

```
IDLE --> STARTING --> RUNNING --> DONE
                              --> ERROR (non-zero exit)
                              --> STOPPED (user SIGTERM)
```

---

## III. Scheduling Engine

### Schedule Declaration

Operations declare schedules via the `# Schedule:` header in bin/ scripts:

```bash
#!/bin/bash
# CommandCenter Operation
# Category: maintenance
# Schedule: 0 2 * * *
```

Schedule tracking fields (`last_scheduled_run`, `next_scheduled_run`, `schedule_enabled`) are stored alongside the cron expression. See DATABASE.md → `operations`.

### Standard Scheduled Scripts

| Script | Convention | Typical Schedule |
|--------|------------|-----------------|
| `bin/daily.sh` | Daily maintenance | `0 2 * * *` |
| `bin/weekly.sh` | Weekly maintenance | `0 3 * * 0` |
| `bin/build.sh` | Rebuild on schedule | Project-specific |

### Missed Run Recovery

On startup, the scheduler checks `last_scheduled_run` against the cron expression. If a run was missed (platform was down), it fires immediately (catch-up). Only the most recent missed run fires — no backfill cascade.

---

## IV. Heartbeats & Events

Two fundamentally different observation types. Heartbeats answer "what is the state right now?" Events answer "what happened?"

### Heartbeats (Continuous State)

Heartbeats are periodic polls that produce a current state. They have no history beyond the current value and a rolling window.

| Heartbeat | Source | States | Poll Method |
|-----------|--------|--------|-------------|
| **Service Health** | `port` + `health` from METADATA.md | UP / DOWN / UNKNOWN | HTTP GET to health endpoint |
| **Process State** | Operations engine | RUNNING / STOPPED | Check PID existence |
| **Git State** | Scanner | CLEAN / DIRTY / UNPUSHED | `git status` + `git log` |
| **Compliance** | Scanner | COMPLIANT / GAPS / UNCHECKED | Check required files exist |

**Aggregate indicators:**
- **UP** = all heartbeats healthy
- **DOWN** = any heartbeat in failure state
- **MIXED** = some up, some down (multi-service projects)

See DATABASE.md → `heartbeats` for the record schema.

### Events (Discrete Occurrences)

Events are timestamped records of things that happened. They accumulate in a log and are never overwritten.

| Event Type | Source | Trigger |
|------------|--------|---------|
| `operation_started` | Operations engine | Script launched |
| `operation_completed` | Operations engine | Script exited (includes exit code) |
| `operation_failed` | Operations engine | Non-zero exit |
| `state_transition` | Heartbeat poller | UP-->DOWN, DOWN-->UP, etc. |
| `git_push` | Dashboard action | User pushed commits |
| `git_commit` | Scanner | New commit detected on scan |
| `schedule_fired` | Scheduler | Cron triggered an operation |
| `schedule_missed` | Scheduler | Startup catch-up detected missed run |
| `build_completed` | Publisher | Portfolio site rebuilt |
| `deploy_completed` | Publisher/config | Site published or config deployed |
| `scan_completed` | Scanner | Project directory re-scanned |
| `ticket_transition` | Workflow | Ticket moved between states |
| `metadata_changed` | Configuration | METADATA.md field edited |
| `alert_fired` | Monitoring | Health alert triggered |
| `spec_updated` | Specification mgmt | Spec file committed via transaction log |

**Platform-level event log** visible on the Monitoring screen as a timeline. Per-project event log visible on the project detail screen.

See DATABASE.md → `events` for the record schema.

---

## V. Specification Management

### Transaction Log Integration

Projects with a corresponding directory in `Specifications/` (e.g., `Specifications/GAME/`) have specification management capabilities. The transaction log tracks AI decisions and changes:

| Feature | Details |
|---------|---------|
| **Spec Directory** | `Specifications/{project_name}/` — linked by convention |
| **Transaction Log** | Ordered record of spec decisions, changes, rationale |
| **Spec Files** | Markdown documents: README, ARCHITECTURE, DATABASE, SCREEN-*, FEATURE_MAP, etc. |
| **Versioning** | Spec changes committed to the Specifications repo with descriptive messages |

See DATABASE.md → `transaction_log` for the record schema.

### Spec-to-Code Traceability

| Direction | Mechanism |
|-----------|-----------|
| Spec --> Code | Transaction log entry links to ticket; ticket links to commits |
| Code --> Spec | Scanner detects `has_specs` flag; UI links to spec directory |
| Spec --> Spec | Cross-references between FEATURE_MAP, SCREEN-*, ARCHITECTURE |

---

## VI. Auto-Detection Magic

Features that GAME provides automatically for Claude-developed projects by reading filesystem conventions:

### On Scan (Automatic)

| Detection | Method | Result |
|-----------|--------|--------|
| **Project exists** | Directory with METADATA.md in $PROJECTS_DIR | Project record created |
| **Identity** | Parse METADATA.md key:value fields | All identity fields populated |
| **Operations** | Parse `# CommandCenter Operation` headers in bin/ | Operation buttons appear |
| **Bookmarks** | Parse `## Bookmarks` in AGENTS.md | Quick-link buttons on dashboard |
| **Endpoints** | Parse `## Service Endpoints` in AGENTS.md | Clickable service links |
| **Dev Commands** | Parse `## Dev Commands` in AGENTS.md | Context for the platform |
| **Stack detection** | `requirements.txt` --> Python, `package.json` --> Node, `Cargo.toml` --> Rust | Auto-populate stack if empty |
| **Git status** | `git status`, `git log`, `git rev-list` | Branch, dirty, unpushed, last commit |
| **Environment flags** | Check for venv/, node_modules/, .git/, CLAUDE.md, tests/, doc/ | Boolean flags |
| **Schedule registration** | `# Schedule:` headers in bin/ scripts | Cron jobs registered |
| **Compliance check** | Required files present per CLAUDE_RULES | Compliance gaps flagged |
| **Spec linkage** | Matching directory in Specifications/ | Spec management enabled |

### Contract-Earns-Capability Principle

"Add the file; the platform discovers the capability."

| File Added | Capability Earned |
|------------|-------------------|
| `METADATA.md` | Project appears in dashboard |
| `AGENTS.md` | Bookmarks, endpoints, dev commands extracted |
| `bin/start.sh` with header | Start button appears |
| `bin/daily.sh` with `# Schedule:` | Daily automation registered |
| `doc/index.html` | Documentation link appears |
| `Specifications/{name}/` | Specification management enabled |
| `health: /health` in METADATA | Health monitoring enabled |
| `port: NNNN` in METADATA | Service monitoring + heartbeat enabled |
| `show_on_homepage: true` | Portfolio card generated |

### Suggested Enhancements (Magic for Claude Users)

| Feature | How It Works | Value |
|---------|--------------|-------|
| **Auto-scaffold** | `create_project.py` generates all required files from a template | Zero-to-dashboard in one command |
| **Spec generation** | Generate ARCHITECTURE.md from scanning code structure, imports, routes | Keep specs in sync with code |
| **Dependency detection** | Scan imports and config for references to other managed projects | Dependency graph on dashboard |
| **Stale project detection** | No git commits in N days + status ACTIVE = flag for review | Surface forgotten projects |
| **Environment drift** | Compare `.env.example` vs `.env` across projects | Catch missing config |
| **Documentation freshness** | Compare `doc/` mtime vs last code commit | Flag stale docs |
| **Test coverage hint** | `has_tests` false + status ACTIVE = suggest adding tests | Quality nudge |
| **Common.sh drift** | Compare project's `bin/common.sh` against Specifications/templates/ | Flag outdated infrastructure |

---

## VII. Tag System

| Feature | Details |
|---------|---------|
| **Storage** | Comma-separated string in `projects.tags` |
| **Colors** | Per-tag hex color, stored in `tag_colors` table and `data/tag_colors.json` |
| **Filtering** | Dashboard filter by tag (pill buttons) |
| **Inline Editing** | Click tag on dashboard to edit |
| **Cross-project** | Same tag across projects creates a natural grouping |
| **Color Picker** | Settings screen with visual color selection |

---

## VIII. API Layer

### HTMX Endpoints (HTML fragments)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Full dashboard page |
| GET | `/api/project/{id}` | Project detail fragment |
| POST | `/api/scan` | Trigger re-scan |
| POST | `/api/run/{op_id}` | Launch operation |
| POST | `/api/stop/{run_id}` | Stop running operation |
| POST | `/api/push/{project_id}` | Git push |
| POST | `/api/project/{id}/toggle-publish` | Toggle portfolio inclusion |
| GET | `/processes` | Process list page |
| GET | `/processes/{run_id}/log` | Log content fragment |
| GET | `/publisher` | Publisher page |
| POST | `/publisher/build` | Rebuild portfolio |
| POST | `/publisher/publish` | Publish to GitHub Pages |
| GET | `/config` | Configuration page |
| GET | `/monitoring` | Monitoring page |
| GET | `/workflow` | Workflow board |
| GET | `/health` | `{"status":"ok"}` JSON |

### JSON API (programmatic access)

Potential extension: mirror key HTMX routes as JSON endpoints under `/api/v1/` for external tool integration (CLI tools, other projects, webhooks).

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/projects` | List all projects with status |
| `GET /api/v1/projects/{id}` | Single project detail |
| `GET /api/v1/projects/{id}/heartbeats` | Current heartbeat states |
| `GET /api/v1/projects/{id}/events` | Recent events |
| `POST /api/v1/projects/{id}/run/{op_id}` | Trigger operation |
| `GET /api/v1/events` | Platform-wide event feed |
| `GET /api/v1/health` | Platform health summary |

---

## IX. Workflow & Ticketing

### Workflow States

Default states from `workflow.json` (user-configurable):

```
IDEA --> PROPOSED --> READY --> IN DEVELOPMENT --> TESTING --> DONE
                                    ^                |
                                  READY <------------+  (rework)
```

### Ticket and AI Decision Log

Ticket attributes and per-ticket AI decision log schema: see DATABASE.md → `tickets` and `ai_decisions`.

When a ticket enters IN DEVELOPMENT, the AI agent's decisions are logged to `ai_decisions`. This creates an audit trail from idea through implementation.

---

## X. Publisher & Portfolio

### How It Works

1. Scan projects where `show_on_homepage = true`
2. For each: use `card_title` (or `display_name`), `card_desc` (or `short_description`), `card_image` (or `logo`), `card_tags` (or `tags`)
3. If `doc/index.html` exists, add documentation link
4. Generate static site from `config/site_config.md` branding
5. Serve locally or push to GitHub Pages

### Source Files

| File | Purpose |
|------|---------|
| `config/site_config.md` | Site title, branding, home page markdown (YAML frontmatter + body) |
| `git_homepage.md` | Per-project card metadata override |
| `static/images/*.webp` | Card thumbnail images |

---

## XI. Compliance & Project Health

### Compliance Checks (Scanner)

Based on CLAUDE_RULES requirements:

| Check | Required For | Detection |
|-------|-------------|-----------|
| METADATA.md exists | All projects | File presence |
| AGENTS.md exists | All projects | File presence |
| CLAUDE.md points to AGENTS.md | All projects | Content check |
| bin/common.sh exists | Projects with bin/ | File presence |
| .env.example when .env exists | Projects with .env | File comparison |
| `name` field in METADATA.md | All projects | Parse check |
| `display_name` in METADATA.md | All projects | Parse check |
| Version format valid | All projects | Regex: `YYYY-MM-DD.N` |
| Git initialized | ACTIVE+ status | `.git/` exists |
| Health endpoint responding | PRODUCTION services | HTTP check |

### Project Health Score (Derived)

Composite score from multiple signals:

| Signal | Weight | Healthy | Unhealthy |
|--------|--------|---------|-----------|
| Compliance | High | All checks pass | Missing required files |
| Git activity | Medium | Commits within 30 days | Stale (no activity) |
| Service health | High | UP heartbeat | DOWN heartbeat |
| Tests exist | Low | `has_tests = true` | No tests for ACTIVE+ |
| Docs current | Low | `has_docs = true` | Docs older than code |
| Env drift | Medium | .env matches .env.example | Missing vars |

---

## XII. Summary: What Makes a Project Fully Managed

A project earns platform capabilities by adding files (contract-earns-capability):

| Level | Files Required | Capabilities Earned |
|-------|---------------|---------------------|
| **Discovered** | METADATA.md | Appears in dashboard, identity, status |
| **Contextual** | + AGENTS.md | Bookmarks, endpoints, dev commands extracted |
| **Operational** | + bin/ scripts with headers | Operation buttons, run/stop, logging |
| **Monitored** | + `port:` + `health:` in METADATA | Heartbeat polling, UP/DOWN/MIXED status |
| **Scheduled** | + `# Schedule:` in script headers | Automated cron runs, missed-run catch-up |
| **Published** | + `show_on_homepage: true` | Portfolio card on GitHub Pages |
| **Documented** | + doc/index.html | Documentation link in dashboard + portfolio |
| **Specified** | + Specifications/{name}/ | Spec management, transaction log |
| **Compliant** | + All CLAUDE_RULES files | Full compliance score, health badge |

---

## References

| Document | Location | Purpose |
|----------|----------|---------|
| ARCHITECTURE.md | This directory | Backend code structure |
| DATABASE.md | This directory | Schema definition — all field types, column definitions, constraints |
| UI-GENERAL.md | This directory | Shared UI patterns |
| SCREEN-*.md | This directory | Per-screen specifications |
| CLAUDE_RULES.md | `../RulesEngine/CLAUDE_RULES.md` | Agent behavior contract |
| DOCUMENTATION_BRANDING.md | `../RulesEngine/DOCUMENTATION_BRANDING.md` | Documentation theming standards |

### Document Responsibilities

| Document | Answers | Does NOT Cover |
|----------|---------|----------------|
| **FEATURE_MAP** (this file) | What features does the platform offer? What can it detect? What are the behavioral rules? | Field types, column constraints, schema details. |
| **ARCHITECTURE** | How is the code organized? What are the modules? How does data flow? | What the user sees. What features exist. |
| **DATABASE** | What tables exist? What columns, types, defaults, constraints? | Why those columns exist (→ FEATURE_MAP). |
| **UI-GENERAL** | What shared UI patterns exist? Nav bar, standard row header, dark theme, modals, HTMX. | Screen-specific layouts. |
| **SCREEN-*** | What does this specific screen show? What can the user do? | Backend implementation. Full attribute definitions. |

**Flow:** FEATURE_MAP defines features → ARCHITECTURE describes modules → DATABASE defines storage → UI-GENERAL defines shared patterns → SCREEN-* defines per-screen layout.
