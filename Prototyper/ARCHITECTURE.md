# Architecture

**Version:** 20260320 V1
**Description:** Module layout, routes, and directory structure

**Flask app with blueprints.** App factory pattern. Scanner, process engine, and publisher are backend modules that feed data to the screen routes.

---

## App Factory

`create_app()` in `app.py`. Returns a configured Flask instance.

1. Load config from environment and `.env`
2. Initialize SQLite database (create tables if missing, run migrations)
3. Register blueprints
4. Start async project scan on first request

## Blueprints

Single blueprint `cc` registered on `/`. All routes live in `routes.py`.

## Backend Modules

### Scanner (`scanner.py`)

Scans `$PROJECTS_DIR` for project directories. For each:
1. Read METADATA.md → parse key:value fields
2. Read AGENTS.md / CLAUDE.md → extract endpoints, bookmarks
3. Read bin/ scripts → parse CommandCenter headers (any language: sh, py, js, pl)
4. Upsert into `projects` and `operations` tables

Runs asynchronously on startup (not blocking first page load). Triggered manually by rescan button.

**Script header detection:** The scanner reads the first 20 lines of every executable file in `bin/`. Any script containing `# CommandCenter Operation` is registered as an operation. Supported languages: Bash, Python, Perl, JavaScript, Ruby — any language using `#` comments. This enables self-documentation as a core platform feature.

### Process Engine (`ops.py` + `spawn.py`)

Launches bin/ scripts as background subprocesses.

1. Receive launch request (project_id, operation_id)
2. Create `runs` record with status STARTING
3. Fork subprocess: execute script from project root
4. Capture stdout/stderr to log file: `logs/{project}_{script}_{yyyymmdd_hhmmss}.log`
5. Parse `[$PROJECT_NAME]` lines from output for status transitions
6. Update `runs` record on exit (status, exit_code, finished_at)

Provides: `launch(project_id, operation_id)`, `stop(run_id)`, `get_running()`, `get_log(run_id)`.

### Publisher (`publisher.py`)

Builds static portfolio site from METADATA.md fields.

1. Query projects where `show_on_homepage = true`
2. Generate card HTML from title, short_description, tags, image
3. If project has `doc/index.html`, add documentation link
4. Write static site to output directory
5. Optionally push to GitHub Pages

## Routes (HTMX)

All screen interactions use HTMX for partial page updates. Server returns HTML fragments, not JSON.

| Method | Path | Returns | Trigger |
|--------|------|---------|---------|
| GET | `/` | Full dashboard page | Page load |
| POST | `/api/scan` | Status message | Rescan button |
| POST | `/api/run/{op_id}` | Updated button state | Operation click |
| POST | `/api/stop/{run_id}` | Updated button state | Stop click |
| POST | `/api/push/{project_id}` | Git status fragment | Push button |
| GET | `/project/{id}` | Project detail page | Name/cog click |
| GET | `/processes` | Process list page | Nav link |
| GET | `/processes/{run_id}/log` | Log content fragment | View Log click |
| GET | `/publisher` | Publisher page | Nav link |
| POST | `/publisher/build` | Build status | Rebuild button |
| POST | `/publisher/publish` | Publish status | Publish button |
| GET | `/project-config` | Configuration list | Nav link |
| GET | `/monitoring` | Monitoring page | Nav link |
| GET | `/workflow` | Workflow board | Nav link |
| GET | `/health` | `{"status":"ok"}` | Health check |

## Directory Layout

```
Prototyper/
  app.py                 App factory (create_app)
  routes.py              All routes (single blueprint: cc)
  scanner.py             Project discovery
  ops.py                 Operation launch/stop/status
  spawn.py               Subprocess management
  publisher.py           Portfolio builder
  models.py              PROJECT_TYPES registry
  db.py                  Database access helpers
  claude_convention.py   CLAUDE.md / AGENTS.md parsing
  templates/             Flask/Jinja2 templates
    base.html            Layout with nav bar
    partials/            HTMX response fragments
  static/
    style.css            Custom styles (Bootstrap 5 dark theme)
  bin/
    common.sh            Shared script functions
    common.py            Shared Python functions
    start.sh             Start Flask dev server
    stop.sh              Stop server
    build_documentation.sh  Generate docs/
  data/
    prototyper.db        SQLite database
  docs/                  Generated documentation
  logs/                  Operation log files
```

## Open Questions

- Should routes.py be split into per-screen blueprint modules as the app grows?
