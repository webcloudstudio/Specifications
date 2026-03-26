# Database

**Version:** 20260320 V1  
**Description:** Database schema: tables, columns, and types

**SQLite with WAL mode.** Single file at `data/game.db`.

---

## Source-of-Truth Model

| Layer | Role |
|-------|------|
| **Project files** (`METADATA.md`, `bin/`, filesystem) | Authoritative source of truth — committed to git, editable by developer |
| **SQLite database** | Runtime cache — the sole source of data for all UI page renders |
| **Startup scan** | Runs automatically in a background thread every time Flask starts; populates the DB from disk |
| **Refresh button** | Re-runs the same scan without restarting; useful when files changed mid-session |

**Page rendering reads the database only.** No template, route, or partial reads a file from disk during a normal page load.

**Writes go to both.** When the UI changes a value (status badge click, port inline edit, etc.), Prototyper writes to the DB immediately and then patches the same value into the project's `METADATA.md`. This keeps the file current so git history tracks changes.

```
Startup / Refresh (slow path — filesystem I/O)
───────────────────────────────────────────────
scan_projects()
  └─ for each project directory:
       detect_project()          → reads METADATA.md, bin/ headers, filesystem flags
       parse_metadata_md()       → reads METADATA.md key-values and ## Links table
       scan_bin_operations()     → reads first 20 lines of each bin/*.sh / bin/*.py
       upsert_project()          → INSERT or UPDATE into SQLite

Normal page load (fast path — DB only)
───────────────────────────────────────
Route handler
  └─ db.get_all_projects()           → SELECT * FROM projects
  └─ db.get_all_operations_keyed()   → SELECT * FROM operations (one query, all projects)
  └─ render_template()               → Jinja renders from dicts; no file I/O

UI write (status click, port edit, etc.)
─────────────────────────────────────────
  └─ UPDATE projects SET ...     (SQLite)
  └─ patch METADATA.md           (file — keeps disk in sync)
```

---

## Field Source Mapping

Every field stored in the `projects` table, its source, and when it is read.

| DB Column | Source File / Method | Read On | Notes |
|-----------|---------------------|---------|-------|
| `name` | Directory name | Scan | Machine slug; must match directory name |
| `display_name` | `METADATA.md` → `display_name:` | Scan | Human-readable name for UI |
| `title` | CamelCase split of directory name | Scan | Legacy; prefer `display_name` |
| `path` | Filesystem (`os.path.abspath`) | Scan | Absolute path to project directory |
| `status` | `METADATA.md` → `status:` | Scan | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED; also writable from UI |
| `port` | `METADATA.md` → `port:` or auto-detected from `app.py` | Scan | Integer; also writable inline from UI |
| `stack` | `METADATA.md` → `stack:` | Scan | Slash-separated tech summary |
| `namespace` | `METADATA.md` → `namespace:` | Scan | Default: `development`; hidden in UI when default |
| `tags` | `METADATA.md` → `tags:` | Scan | Comma-separated string |
| `health_endpoint` | `METADATA.md` → `health:` | Scan | Default: `/health` |
| `desired_state` | `METADATA.md` → `desired_state:` | Scan | `running` or `on-demand` |
| `version` | `METADATA.md` → `version:` | Scan | Format: `YYYY-MM-DD.N` |
| `project_type` | `METADATA.md` → `project_type:` or heuristic | Scan | `software` / `book` |
| `has_git` | `.git/` directory present | Scan | Boolean flag |
| `has_venv` | `venv/` or `.venv/` directory present | Scan | Boolean flag |
| `has_node` | `node_modules/` directory present | Scan | Boolean flag |
| `has_claude` | `CLAUDE.md` file present | Scan | Boolean flag; enables CLAUDE.md modal |
| `has_docs` | Any subdir starting with `doc` containing `index.html` or `index.htm` (glob: `*/doc*/index.htm*`) | Scan | Boolean flag; enables 📖 Help button |
| `card_title` | `METADATA.md` → `title:` (card section) | Scan | Portfolio card; overrides `display_name` if set |
| `card_desc` | `METADATA.md` → `short_description:` or `description:` | Scan | Portfolio card description |
| `card_tags` | `METADATA.md` → `tags:` | Scan | Portfolio card tags |
| `card_type` | `METADATA.md` → `card_type:` | Scan | Portfolio category label |
| `card_url` | `METADATA.md` → `card_url:` | Scan | Portfolio card link |
| `card_image` | `METADATA.md` → `image:` | Scan | Portfolio card image filename |
| `card_show` | `METADATA.md` → `show_on_homepage:` | Scan | Boolean; include in generated portfolio |
| `extra` (JSON) | Various | Scan | Stores: `links`, `bookmarks`, `doc_path`, `tech_stack`, `has_start_sh`, etc. |
| `last_scanned` | System clock | Scan | Timestamp of last successful scan |
| `created_at` | System clock | Insert only | Set once on first discovery |
| `updated_at` | System clock | Scan + UI writes | Updated on every upsert |

### `extra` JSON sub-fields

| Key | Source | Notes |
|-----|--------|-------|
| `links` | `METADATA.md` → `## Links` table | List of `{label, url}` shown in Links column |
| `bookmarks` | `AGENTS.md` / `CLAUDE.md` → `## Bookmarks` | Quick-access links for AI context |
| `doc_path` | Filesystem detection | Relative path to doc index (e.g., `docs/index.html`); used to build Flask proxy URL `/project/{id}/doc/index.html` |
| `tech_stack` | Auto-detected from `app.py`, `package.json`, etc. | Fallback for `stack` column |
| `has_start_sh` | `bin/start.sh` present | Legacy flag; bin operations supersede this |

### Operations table field sources

| DB Column | Source | Read On |
|-----------|--------|---------|
| `project_id` | FK to projects | Scan |
| `name` | `# Name:` header in bin script | Scan |
| `category` | `# Category:` header; default `local` | Scan |
| `cmd` | Derived from filename (`bin/start.sh`) | Scan |
| `cwd` | Project path | Scan |
| `default_port` | `# Port:` header | Scan |
| `health_path` | `# Health:` header | Scan |
| `schedule` | `# Schedule:` header | Scan |
| `timeout` | `# Timeout:` header | Scan |

Operations are deleted and re-seeded on every scan (only `bin/` operations — custom operations survive).

---

## Startup / Refresh Sequence

Both server startup and the Refresh button execute the same `scan_projects()` function in `scanner.py`. `scanner.py` is a library module — it has no entry point; it is called by `app.py` (startup) and by the `/api/sync` route (Refresh button).

On startup, the scan runs in a **background thread** so the server is immediately ready to serve requests; the DB will be fully populated within a few seconds. After a restart, the Refresh button is redundant — the startup scan has already run. Use Refresh only when project files change *while the server is running* and you want to pick up those changes without restarting.

```
1. cleanup_orphaned()        Remove DB rows for projects no longer on disk
2. for each directory in PROJECTS_DIR:
   a. detect_project()
      - Read filesystem flags (has_git, has_venv, has_node, has_claude, has_docs)
      - Detect doc_path by checking doc/ and docs/ for index.html / index.htm
      - Auto-detect tech stack from known files (app.py, package.json, manage.py, etc.)
      - Auto-detect port from app.py or METADATA.md
   b. parse_metadata_md()
      - Parse key:value lines → display_name, status, port, stack, namespace,
        health_endpoint, desired_state, version, project_type, tags
      - Parse ## Links table → extra.links
      - Parse card metadata → card_* columns
   c. scan_bin_operations()
      - Read first 20 lines of each bin/*.sh and bin/*.py
      - Look for `# CommandCenter Operation` marker
      - Extract Name, Category, Port, Schedule, Timeout, Health headers
   d. parse claude/agents if has_claude → extra.bookmarks
   e. upsert_project()
      - UPDATE if exists (preserves user-edited fields via COALESCE)
      - INSERT if new
      - DELETE + re-seed operations table for this project
3. Log scan duration per project and total
```

**User-edited fields are preserved on re-scan** via SQL `COALESCE(?, column)` — if the scan value is NULL, the existing DB value is kept. Fields where METADATA.md is authoritative (status, port, stack) overwrite the DB.

---

## Schema

### projects

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| name | TEXT UNIQUE | — | Machine slug; matches directory name |
| display_name | TEXT | NULL | Human-readable name from METADATA.md |
| title | TEXT | — | CamelCase-split fallback (legacy) |
| path | TEXT | NULL | Absolute path to project directory |
| status | TEXT | 'template' | Lifecycle status |
| port | INTEGER | NULL | Service port |
| stack | TEXT | NULL | Technology summary |
| health_endpoint | TEXT | '/health' | Health check path |
| desired_state | TEXT | 'on-demand' | running / on-demand |
| namespace | TEXT | 'development' | Deployment namespace |
| tags | TEXT | NULL | Comma-separated tags |
| project_type | TEXT | 'software' | software / book / etc. |
| description | TEXT | NULL | Short description |
| has_git | INTEGER | 0 | .git/ present |
| has_venv | INTEGER | 0 | venv/ present |
| has_node | INTEGER | 0 | node_modules/ present |
| has_claude | INTEGER | 0 | CLAUDE.md present |
| has_docs | INTEGER | 0 | doc[s]/index.htm[l] present |
| card_title | TEXT | NULL | Portfolio card title |
| card_desc | TEXT | NULL | Portfolio card description |
| card_tags | TEXT | NULL | Portfolio card tags |
| card_type | TEXT | NULL | Portfolio card category |
| card_url | TEXT | NULL | Portfolio card URL |
| card_image | TEXT | NULL | Portfolio card image filename |
| card_show | INTEGER | 0 | Include in portfolio page |
| version | TEXT | NULL | YYYY-MM-DD.N from METADATA.md |
| extra | TEXT | '{}' | JSON blob (links, bookmarks, doc_path, etc.) |
| is_active | INTEGER | 1 | 0 if removed from disk |
| last_scanned | TEXT | NULL | Timestamp of last scan |
| created_at | TEXT | datetime('now') | First discovery |
| updated_at | TEXT | datetime('now') | Last scan or UI write |

### operations

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| name | TEXT | Display name from `# Name:` header |
| category | TEXT | `local` / `service` / `maintenance` / custom |
| cmd | TEXT | Command string (e.g., `bin/start.sh`) |
| cwd | TEXT | Working directory (project path) |
| needs_venv | INTEGER | Activate venv before running |
| is_url | INTEGER | Open URL rather than run command |
| default_port | INTEGER | From `# Port:` header |
| health_path | TEXT | From `# Health:` header |
| schedule | TEXT | From `# Schedule:` header (cron expression) |
| last_scheduled_run | TEXT | Last time the scheduler fired this operation |
| next_scheduled_run | TEXT | Calculated next fire time |
| schedule_enabled | INTEGER | 1 = active; allows pausing without removing the header |
| timeout | INTEGER | From `# Timeout:` header |
| sort_order | INTEGER | Display order |

### op_runs

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| op_id | INTEGER FK | References operations.id |
| project_id | INTEGER FK | References projects.id |
| status | TEXT | running / done / error / stopped |
| pid | INTEGER | OS process ID |
| started_at | TEXT | datetime |
| finished_at | TEXT | datetime or NULL while running |
| exit_code | INTEGER | NULL while running |
| log_path | TEXT | Path to log file |
| cmd | TEXT | Actual command executed |
| name | TEXT | Operation name at time of run |

### tickets

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| title | TEXT | Ticket title |
| description | TEXT | Detail text |
| state | TEXT | idea / proposed / ready / in_development / testing / done |
| tags | TEXT | Comma-separated |
| sort_order | INTEGER | Column position |
| created_at | TEXT | datetime |
| updated_at | TEXT | datetime |

### heartbeats

One row per project per heartbeat type. Overwritten on each poll (no history; rolling window only).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| heartbeat_type | TEXT | service_health / process_state / git_state / compliance |
| current_state | TEXT | Current state value (e.g. UP, DOWN, RUNNING, CLEAN, COMPLIANT) |
| last_checked | TEXT | Timestamp of last poll (yyyymmdd_hhmmss) |
| response_ms | INTEGER | Response time in ms (service_health only; NULL otherwise) |
| uptime_pct | REAL | Rolling 24h uptime percentage (service_health only; NULL otherwise) |

### events

Append-only log. Rows are never updated or deleted.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id; NULL for platform-level events |
| event_type | TEXT | Valid values: `operation_started`, `operation_completed`, `operation_failed`, `state_transition`, `git_push`, `git_commit`, `schedule_fired`, `schedule_missed`, `build_completed`, `deploy_completed`, `scan_completed`, `ticket_transition`, `metadata_changed`, `alert_fired`, `spec_updated`, `spec_ticket_created` |
| timestamp | TEXT | When it happened (yyyymmdd_hhmmss) |
| summary | TEXT | Human-readable one-liner |
| detail | TEXT | JSON event-specific payload |
| source | TEXT | Subsystem that generated the event |

### transaction_log

Spec decision log. One row per decision, change, question, or rationale entry.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Sequential entry number |
| project_id | INTEGER FK | References projects.id |
| timestamp | TEXT | When the decision was made (yyyymmdd_hhmmss) |
| category | TEXT | decision / change / question / rationale |
| title | TEXT | One-line summary |
| body | TEXT | Full description, context, alternatives considered |
| files_affected | TEXT | JSON array of spec file paths modified |
| ticket_id | INTEGER FK | Optional link to tickets.id |

### ai_decisions

Per-ticket AI decision log. Written when a ticket enters IN DEVELOPMENT.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| ticket_id | INTEGER FK | References tickets.id |
| timestamp | TEXT | When the work happened (yyyymmdd_hhmmss) |
| decision | TEXT | What was decided and why |
| alternatives | TEXT | What was considered but rejected |
| files_changed | TEXT | JSON array of files modified |

### workflow_types

Configurable spec ticket type definitions. Seeded once on first startup; rows are never deleted by the scanner — only by user action via Settings. Each row defines one button in the Projects / Workflow screen.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| name | TEXT | — | Display name shown on button (e.g. `Patch`) |
| file_prefix | TEXT | — | Prefix used for generated filename (e.g. `PATCH`) |
| description | TEXT | NULL | Tooltip text shown on hover |
| template | TEXT | — | Markdown template for the created file; supports `{title}` and `{body}` placeholders |
| sort_order | INTEGER | 0 | Left-to-right display order within the Workflows column |
| is_active | INTEGER | 1 | 1 = shown in UI; 0 = hidden without deleting |
| created_at | TEXT | datetime('now') | |
| updated_at | TEXT | datetime('now') | |

**Seed data (inserted if table is empty on startup):**

| name | file_prefix | description |
|------|-------------|-------------|
| Patch | PATCH | Bug fix, behavioral correction, or refactor |
| Screen | SCREEN | New or revised screen specification |
| Feature | FEATURE | New or revised feature specification |
| Acceptance Criteria | AC | Testable MUST / MUST NOT batch |

### spec_tickets

Unified ticket store shared by the Projects / Workflow screen (file creation) and the Dashboards / Workflow Kanban (lifecycle tracking). One row per ticket regardless of whether a spec file has been generated yet.

Supersedes the `tickets` table — see note below.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| project_id | INTEGER FK | — | References projects.id |
| workflow_type_id | INTEGER FK | NULL | References workflow_types.id; NULL for tickets not tied to a type |
| filename | TEXT | NULL | Created file basename (e.g. `PATCH-003-fix-nav.md`); NULL until file is written |
| title | TEXT | — | User-entered title (also used in filename slug) |
| body | TEXT | NULL | User-entered body / description |
| file_status | TEXT | `pending` | File-processing state: `pending` / `applied` / `rejected`; only meaningful when `filename` is set |
| kanban_state | TEXT | `idea` | Kanban lifecycle: `idea` / `proposed` / `ready` / `in_development` / `testing` / `done` |
| priority | TEXT | `medium` | `low` / `medium` / `high` / `critical` |
| tags | TEXT | NULL | Comma-separated tag string |
| sort_order | INTEGER | 0 | Column position within `kanban_state` |
| created_at | TEXT | datetime('now') | |
| updated_at | TEXT | datetime('now') | |

> **`tickets` table is superseded.** New code reads and writes `spec_tickets`. The `tickets` table is retained for backwards compatibility until migrated.

### settings

Key-value store for application-level configuration. Seeded on first startup. Rows are never deleted — only updated.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| key | TEXT PK | — | Setting identifier |
| value | TEXT | NULL | Current value |
| description | TEXT | NULL | Human-readable label shown in Settings UI |
| updated_at | TEXT | datetime('now') | |

**Seed data:**

| key | value | description |
|-----|-------|-------------|
| `app_name` | `Command Center` | Name displayed in the upper-left corner of the application |
| `homepage_url` | `` | Live homepage URL (shown on the Homepage screen) |

### tag_colors

Color assignments per tag. Written by `POST /settings/tags`. Canonical source for tag pill colors — supersedes `data/tag_colors.json` once this table is added.

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| tag | TEXT PK | — | Raw tag string |
| bg | TEXT | `#64748b` | Background hex color |
| fg | TEXT | `#ffffff` | Foreground hex color |
| updated_at | TEXT | datetime('now') | |

> Until this table is added, `data/tag_colors.json` remains the color source. Migration: on first Settings / Tag page load, import any entries from the JSON file into this table and delete the file.

### health_check_log, log_positions, log_filter

These three tables support `monitoring.py` (health poller + log ingestor). Full schema is in FEATURE-HEALTHCHECK.md. Summary:

| Table | Purpose | Retention |
|-------|---------|-----------|
| `health_check_log` | Raw HTTP/TCP poll results (one row per check) | 24h rolling window |
| `log_positions` | Byte-offset cursor per project log file (incremental ingestion) | Permanent |
| `log_filter` | Regex classification rules; seeded with defaults on startup | Permanent |

Schema is authoritative in FEATURE-HEALTHCHECK.md. When these tables are implemented, add their full column definitions here and remove this reference.

---

## Conventions

- WAL mode: set once in `init_db()` (persistent on the file); not repeated per connection
- Foreign keys: `PRAGMA foreign_keys=ON` per connection (required for FK enforcement)
- Schema changes: `_add_column_if_missing()` in `db.py` — additive only, no migration files
- JSON blobs: stored as TEXT, parsed by application; changes do not require schema migration
- DB created automatically on first startup if missing

---

## Open Questions / Design Decisions

- **`title` column**: Duplicated by `display_name`. Remove once all templates reference `display_name` exclusively. Until then, keep it to avoid breaking existing renders.
- **WAL PRAGMA per connection**: Harmless (WAL is persistent). Move to `init_db()` only as a cleanup task — not a blocking issue.
- **Tag colors**: Promoted to `tag_colors` table above. `data/tag_colors.json` is legacy; migrate on first Settings / Tag load.
- **`has_tests` flag**: Scanned from `tests/` directory or `bin/test.sh` presence. Add to scanner and `projects` table schema in same pass as `has_specs`.
- **`has_specs` flag**: Scanned from `{SPECIFICATIONS_PATH}/{project.name}/` existence. Requires `SPECIFICATIONS_PATH` to be set; defaults to `false` when not configured.
- **`git_last_commit_date`**: Not yet implemented. Would replace `version` date as the `LastUpdate` column source. Requires `git log --format=%ci -1` during scan and storing the ISO date. Add to `projects` table when scanner is updated.
