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
| `doc_path` | Filesystem detection | Relative path to doc index (e.g., `doc/index.html`); used to build Flask proxy URL `/project/{id}/doc/index.html` |
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
| schedule | TEXT | From `# Schedule:` header |
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

---

## Conventions

- WAL mode: set once in `init_db()` (persistent on the file); not repeated per connection
- Foreign keys: `PRAGMA foreign_keys=ON` per connection (required for FK enforcement)
- Schema changes: `_add_column_if_missing()` in `db.py` — additive only, no migration files
- JSON blobs: stored as TEXT, parsed by application; changes do not require schema migration
- DB created automatically on first startup if missing

---

## Open Questions / Design Decisions

- **`title` column**: Duplicated by `display_name`. Candidate for removal once all templates consistently use `display_name`.
- **WAL PRAGMA per connection**: Harmless (WAL is persistent) but wasteful — should move to `init_db()` only.
- **Tag colors**: Currently in `data/tag_colors.json` (file, not DB). Should be promoted to a `tag_colors` table to stay consistent with the DB-as-UI-source model.
- **`has_docs`, `has_tests`, `has_specs` flags**: `has_docs` is now implemented. `has_tests` and `has_specs` are roadmap items for contract-earns-capability (see FEATURE_MAP.md).
- **`git_last_commit_date`**: Not yet implemented. Would replace `version` date as the `LastUpdate` source — requires running `git log` during scan and storing the result.
