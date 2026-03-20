# Database

**Version:** 20260320 V1  
**Description:** Database schema: tables, columns, and types

SQLite at `data/game.db`. Stack conventions (WAL, FK pragma, migrations) per `stack/sqlite.md`.

## Source of Truth

| Layer | Role |
|-------|------|
| Project files (METADATA.md, bin/, filesystem) | Authoritative — committed to git |
| SQLite database | Runtime cache — sole source for UI renders |
| Startup scan | Background thread on Flask start; populates DB from disk |
| Refresh button | Re-runs scan without restart |

Pages read DB only. UI writes go to both DB and METADATA.md (keeps file current for git history).

---

## projects

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | unique, machine slug = directory name |
| display_name | TEXT | from METADATA.md |
| path | TEXT | absolute path to project dir |
| status | TEXT | IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED |
| port | INTEGER | nullable |
| stack | TEXT | slash-separated |
| health_endpoint | TEXT | default /health |
| desired_state | TEXT | running / on-demand |
| namespace | TEXT | default: development |
| tags | TEXT | comma-separated |
| project_type | TEXT | software / book |
| has_git | INTEGER | auto-detected |
| has_venv | INTEGER | auto-detected |
| has_node | INTEGER | auto-detected |
| has_claude | INTEGER | auto-detected |
| has_docs | INTEGER | auto-detected |
| card_title | TEXT | portfolio override, defaults to display_name |
| card_desc | TEXT | portfolio override, defaults to short_description |
| card_tags | TEXT | portfolio override |
| card_type | TEXT | portfolio override |
| card_url | TEXT | portfolio override |
| card_image | TEXT | portfolio override |
| card_show | INTEGER | include in portfolio |
| version | TEXT | YYYY-MM-DD.N |
| extra | JSON | links, bookmarks, doc_path, tech_stack |
| is_active | INTEGER | 0 if removed from disk |
| last_scanned | TEXT | timestamp |
| created_at | TEXT | timestamp, set once |
| updated_at | TEXT | timestamp, updated on scan + UI writes |

## operations

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| project_id | FK | references projects |
| name | TEXT | from `# Name:` script header |
| category | TEXT | local / service / maintenance |
| cmd | TEXT | e.g. bin/start.sh |
| cwd | TEXT | project path |
| needs_venv | INTEGER | |
| is_url | INTEGER | open URL instead of run command |
| default_port | INTEGER | from `# Port:` header |
| health_path | TEXT | from `# Health:` header |
| schedule | TEXT | cron expression from `# Schedule:` header |
| timeout | INTEGER | from `# Timeout:` header |
| sort_order | INTEGER | |

Operations are deleted and re-seeded per project on every scan.

## op_runs

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| op_id | FK | references operations |
| project_id | FK | references projects |
| status | TEXT | running / done / error / stopped |
| pid | INTEGER | OS process ID |
| started_at | TEXT | |
| finished_at | TEXT | nullable while running |
| exit_code | INTEGER | nullable while running |
| log_path | TEXT | logs/{project}_{script}_{yyyymmdd_hhmmss}.log |
| cmd | TEXT | actual command executed |
| name | TEXT | operation name at time of run |

## tickets

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| project_id | FK | references projects |
| title | TEXT | |
| description | TEXT | |
| state | TEXT | idea / proposed / ready / in_development / testing / done |
| tags | TEXT | comma-separated |
| sort_order | INTEGER | column position |
| created_at | TEXT | |
| updated_at | TEXT | |

---

## Open Questions

- Remove legacy `title` column? `display_name` covers it.
- Promote `tag_colors` from JSON file to a DB table?
- Add `has_tests`, `has_specs` boolean flags to projects?
- Add `git_branch`, `git_dirty`, `git_unpushed`, `git_last_commit` columns or keep in `extra` JSON?
