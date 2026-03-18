# Database

**SQLite with WAL mode.** Single file at `data/cc.db`. All tables below.

---

## Source-of-Truth Model

| Layer | Role |
|-------|------|
| **Project files** (`METADATA.md`, `bin/`, etc.) | Authoritative source of truth — what is committed to git |
| **Database** | Runtime cache — the sole source of data for all UI page renders |
| **Refresh (scan)** | The only operation that reads project files; syncs DB from files |

**Page rendering reads the database only.** No template, route, or partial reads a file from disk during a normal page load. All data is pre-loaded into SQLite at startup and refreshed on demand.

**Writes go to both.** When the UI changes a value (e.g. status badge click, port edit), GAME writes to the DB immediately and then patches the same value into the project's `METADATA.md`. The file stays current so git history tracks it.

```
Startup / Refresh                         Normal page load
─────────────────                         ────────────────
scan_projects()                           Route handler
  └─ read METADATA.md (each project)        └─ db.get_all_projects()
  └─ read bin/ headers                      └─ db.get_all_operations_keyed()
  └─ upsert → SQLite                        └─ render_template()  (DB data only)

UI write (status click, port edit, etc.)
─────────────────────────────────────────
  └─ UPDATE projects SET ...    (DB)
  └─ patch METADATA.md          (file)
```

### Implications for performance

- Page loads should be fast: 2–3 SQLite queries, no file I/O.
- The Refresh button (`/api/sync`) is the only slow path — it walks the filesystem.
- Startup scan runs in a background thread so the server is ready immediately.
- WAL mode: `PRAGMA journal_mode=WAL` is set once (persistent on the file). Subsequent connections do not need to re-issue it.

---

## Schema

### projects

Discovered projects. One row per project directory. Upserted on every scan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| name | TEXT UNIQUE | Machine name from METADATA.md |
| display_name | TEXT | Human-readable name |
| title | TEXT | Display title (legacy — prefer display_name) |
| path | TEXT | Absolute path to project directory |
| status | TEXT | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED |
| port | INTEGER | Service port |
| stack | TEXT | Technology summary |
| health_endpoint | TEXT | Health check path |
| desired_state | TEXT | running/on-demand |
| namespace | TEXT | development/qa/production/custom |
| tags | TEXT | Comma-separated |
| project_type | TEXT | software/book/etc. |
| description | TEXT | Short description |
| is_active | BOOLEAN | False if removed from disk |
| last_scanned | TEXT | datetime string |
| has_git | BOOLEAN | .git directory present |
| has_venv | BOOLEAN | venv/ present |
| has_node | BOOLEAN | node_modules/ or package.json present |
| has_claude | BOOLEAN | AGENTS.md/CLAUDE.md present |
| card_title | TEXT | Portfolio card title (overrides display_name if set) |
| card_desc | TEXT | Portfolio card description (overrides description if set) |
| card_tags | TEXT | Portfolio card tags |
| card_type | TEXT | Portfolio card category |
| card_url | TEXT | Portfolio card URL |
| card_show | BOOLEAN | Include in generated portfolio page |
| card_image | TEXT | Portfolio card image filename |
| version | TEXT | From METADATA.md `version:` field |
| extra | TEXT | JSON blob for additional METADATA.md fields (links, bookmarks, etc.) |
| created_at | TEXT | datetime |
| updated_at | TEXT | datetime |

### operations

Registered operations from `bin/` script headers. Re-populated on every scan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| name | TEXT | Display name (from filename or `# Name:` header) |
| category | TEXT | From `# Category:` header; default `local` |
| cmd | TEXT | Full command string |
| cwd | TEXT | Working directory |
| needs_venv | BOOLEAN | Activate venv before running |
| is_url | BOOLEAN | Open a URL rather than run a command |
| default_port | INTEGER | From `# Port:` header |
| health_path | TEXT | From `# Health:` header |
| schedule | TEXT | From `# Schedule:` header |
| timeout | INTEGER | From `# Timeout:` header |
| sort_order | INTEGER | Display order |

### op_runs

History of operation executions (and currently-running processes).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| op_id | INTEGER FK | References operations.id |
| project_id | INTEGER FK | References projects.id |
| status | TEXT | running/done/error/stopped |
| pid | INTEGER | OS process ID |
| started_at | TEXT | datetime |
| finished_at | TEXT | datetime or NULL while running |
| exit_code | INTEGER | NULL while running |
| log_path | TEXT | Path to log file |
| cmd | TEXT | Actual command executed |
| name | TEXT | Operation name at time of run |

### tickets

Kanban-style tickets per project.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| title | TEXT | Ticket title |
| description | TEXT | Detail text |
| state | TEXT | idea/proposed/ready/in_development/testing/done |
| tags | TEXT | Comma-separated |
| sort_order | INTEGER | Column position |
| created_at | TEXT | datetime |
| updated_at | TEXT | datetime |

---

## Conventions

- WAL mode set once at DB init (persistent on file) — not repeated per connection
- Foreign keys enforced per connection: `PRAGMA foreign_keys=ON`
- All timestamps as SQLite `datetime('now')` strings
- JSON stored in `extra` TEXT column, parsed by application layer
- Schema changes via `_add_column_if_missing()` in `db.py` — no migration files needed for additive changes
- Database created automatically on first startup if missing

---

## Open Questions / Design Decisions

- **`title` column**: Legacy field, functionally duplicated by `display_name`. Candidate for removal once all templates use `display_name`.
- **WAL PRAGMA per connection**: Currently issued on every `get_db()` call. Since WAL is a file-level persistent setting, this is harmless but wasteful. Should be moved to `init_db()` only.
- **Tag colors**: Currently stored in `data/tag_colors.json` (file). Could be promoted to a `tag_colors` DB table to stay consistent with the DB-as-UI-source model.
- **`has_docs`, `has_tests`, `has_specs` flags**: Not yet in schema. Needed for contract-earns-capability auto-detection (see FEATURE_MAP.md). Add as BOOLEAN columns in next schema pass.
