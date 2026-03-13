# Database

**SQLite with WAL mode.** Single file at `data/game.db`. All tables below.

---

## Schema

### projects

Discovered projects. One row per project directory. Upserted on every scan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| name | TEXT UNIQUE | Machine name from METADATA.md |
| display_name | TEXT | Human-readable name |
| path | TEXT | Absolute path to project directory |
| status | TEXT | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED |
| port | INTEGER | Service port |
| stack | TEXT | Technology summary |
| health_endpoint | TEXT | Health check path |
| desired_state | TEXT | running/on-demand |
| namespace | TEXT | development/qa/production/custom |
| tags | TEXT | Comma-separated |
| show_on_homepage | BOOLEAN | Portfolio inclusion |
| title | TEXT | Display title with tagline |
| short_description | TEXT | One sentence |
| git_branch | TEXT | Current branch |
| git_dirty | BOOLEAN | Uncommitted changes |
| git_unpushed | INTEGER | Unpushed commit count |
| git_last_commit | TEXT | Last commit message |
| is_active | BOOLEAN | False if removed from disk |
| last_scanned | TEXT | yyyymmdd_hhmmss |
| extra | TEXT | JSON blob for additional METADATA.md fields |

### operations

Registered operations from bin/ script headers. Re-populated on scan.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| script_name | TEXT | Filename (e.g., start.sh) |
| script_path | TEXT | Relative path (e.g., bin/start.sh) |
| display_name | TEXT | Derived from filename |
| category | TEXT | From header or default |
| port | INTEGER | From `# Port:` header |
| health_path | TEXT | From `# Health:` header |
| schedule | TEXT | From `# Schedule:` header |
| timeout | INTEGER | From `# Timeout:` header |

### runs

History of operation executions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_id | INTEGER FK | References projects.id |
| operation_id | INTEGER FK | References operations.id |
| status | TEXT | STARTING/RUNNING/DONE/ERROR/STOPPED |
| pid | INTEGER | OS process ID |
| started_at | TEXT | yyyymmdd_hhmmss |
| finished_at | TEXT | yyyymmdd_hhmmss or NULL |
| exit_code | INTEGER | NULL while running |
| log_path | TEXT | Path to log file |

### tag_colors

User-defined tag colors.

| Column | Type | Description |
|--------|------|-------------|
| tag | TEXT PK | Tag name |
| color | TEXT | Hex color (#4caf50) |

### config_deployments

AI configuration deployment history.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| profile_name | TEXT | Profile that was deployed |
| deployed_at | TEXT | yyyymmdd_hhmmss |
| git_sha | TEXT | Commit SHA of staged config |

### usage_sessions

Parsed AI session records (read from external JSONL logs).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| project_name | TEXT | Project context |
| model | TEXT | AI model name |
| tokens_in | INTEGER | Input tokens |
| tokens_out | INTEGER | Output tokens |
| estimated_cost | REAL | From rates table |
| session_time | TEXT | yyyymmdd_hhmmss |

### usage_rates

User-editable cost rates.

| Column | Type | Description |
|--------|------|-------------|
| model | TEXT PK | Model name |
| cost_per_million_in | REAL | Cost per 1M input tokens |
| cost_per_million_out | REAL | Cost per 1M output tokens |

---

## Conventions

- WAL mode enabled on connection: `PRAGMA journal_mode=WAL`
- Foreign keys enforced: `PRAGMA foreign_keys=ON`
- All timestamps in `yyyymmdd_hhmmss` format
- JSON stored in TEXT columns, parsed by application
- Migrations in `data/migrations/` as numbered SQL files
- Database created on first startup if missing
