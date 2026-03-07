# Database Schema

SQLite database at `data/cc.db`. WAL mode enabled, foreign keys enforced.

> **Technology Reference**: See `stack/sqlite.md` for SQLite-specific best practices (connection setup, PRAGMAs, migration patterns, backup, and when to choose PostgreSQL instead).

## Tables

### projects

Primary table. One row per discovered project directory.

```sql
CREATE TABLE IF NOT EXISTS projects (
    id           INTEGER PRIMARY KEY,
    name         TEXT UNIQUE NOT NULL,     -- directory name (case-sensitive, immutable identifier)
    title        TEXT NOT NULL,            -- display name, derived from dir name via camelCase splitting
    description  TEXT,
    project_type TEXT NOT NULL DEFAULT 'software',  -- 'software' or 'book'
    status       TEXT DEFAULT 'template',  -- legacy field (workflow stored in extra JSON)
    extra        TEXT DEFAULT '{}',        -- JSON: tech_stack, port, remote_url, workflow, links, bookmarks, unpushed, has_*_sh flags
    has_git      INTEGER DEFAULT 0,
    has_venv     INTEGER DEFAULT 0,
    has_node     INTEGER DEFAULT 0,
    has_claude   INTEGER DEFAULT 0,
    card_title   TEXT,                     -- GitHub homepage card fields
    card_desc    TEXT,
    card_tags    TEXT,                     -- comma-separated or JSON array
    card_type    TEXT,
    card_url     TEXT,
    card_show    INTEGER DEFAULT 0,        -- 1 = include on homepage
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);
```

### operations

Operations available for each project (seeded from `bin/` scripts and git status).

```sql
CREATE TABLE IF NOT EXISTS operations (
    id          INTEGER PRIMARY KEY,
    project_id  INTEGER REFERENCES projects(id),
    name        TEXT NOT NULL,            -- e.g. "Service Start", "Git Push"
    category    TEXT NOT NULL,            -- 'local' or 'remote'
    cmd         TEXT NOT NULL,            -- shell command, e.g. "bin/start.sh", "git push"
    cwd         TEXT,                     -- working directory (project path)
    needs_venv  INTEGER DEFAULT 0,
    is_url      INTEGER DEFAULT 0,        -- deprecated, unused
    default_port INTEGER,                 -- from bin/ CommandCenter Operation header
    sort_order  INTEGER DEFAULT 0
);
```

### op_runs

Tracks running and completed process executions.

```sql
CREATE TABLE IF NOT EXISTS op_runs (
    id         INTEGER PRIMARY KEY,
    op_id      INTEGER REFERENCES operations(id),  -- NULL for spawn-service processes
    started_at TEXT DEFAULT (datetime('now')),
    pid        INTEGER,
    status     TEXT DEFAULT 'running',    -- 'starting', 'running', 'done', 'error'
    cmd        TEXT,                      -- command that was executed
    name       TEXT                       -- human-readable operation name
);
```

## Extra JSON Column Schema

The `projects.extra` column stores a JSON object with these keys:

| Key             | Type    | Source      | Description                          |
|-----------------|---------|-------------|--------------------------------------|
| `tech_stack`    | string  | scanner     | "flask", "django", "node", "astro", "python" |
| `port`          | int     | scanner/user | Configured port number              |
| `remote_url`    | string  | scanner     | Git remote origin URL               |
| `workflow`      | string  | user        | Current workflow state key ("todo", "developing", "good") |
| `links`         | array   | scanner     | From Links.md: `[{label, url}]`     |
| `bookmarks`     | object  | scanner     | From CLAUDE.md: `{group: [{title, url}]}` |
| `unpushed`      | int     | scanner     | Count of unpushed git commits       |
| `has_start_sh`  | bool    | scanner     | Project has start.sh                |
| `has_build_sh`  | bool    | scanner     | Project has build.sh                |
| `has_deploy_sh` | bool    | scanner     | Project has deploy.sh               |
| `has_test_sh`   | bool    | scanner     | Project has test.sh                 |

## Migrations

Schema migrations run via `_run_migrations(conn)` during `init_db()`. Uses `PRAGMA table_info()` to detect missing columns and `ALTER TABLE` to add them. Current migrations:

1. Add `cmd` column to `op_runs`
2. Add `name` column to `op_runs`
3. Add `default_port` column to `operations`

## Data Access Patterns

- `get_db()` — Returns connection with `Row` factory, WAL mode, FK enforcement
- `row_to_dict(row)` — Converts Row to dict, auto-parses `extra` JSON field
- `get_project(id)` / `get_project_by_name(name)` — Single project lookup
- `get_all_projects()` — All projects ordered by type then title
- `get_operations(project_id)` — Operations ordered by category then sort_order
- `get_running_ops()` — JOIN op_runs + operations where status='running'
- `get_running_projects()` — Distinct projects with running ops (for nav bar badges)
- `query(sql, params, one=False)` — Generic query helper
- `execute(sql, params)` — Generic write helper, returns lastrowid
