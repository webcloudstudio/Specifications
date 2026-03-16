# Architecture

**Flask app with blueprints.** App factory pattern. Scanner, process engine, and publisher are backend modules that feed data to the screen routes.

---

## App Factory

`create_app()` in `app.py`. Returns a configured Flask instance.

1. Load config from environment and `.env`
2. Initialize SQLite database (create tables if missing, run migrations)
3. Register blueprints
4. Start async project scan on first request

## Blueprints

| Blueprint | Mount | Purpose |
|-----------|-------|---------|
| `dashboard` | `/` | Main project list, project detail, inline actions |
| `processes` | `/processes` | Process list, log viewer, stop endpoint |
| `publisher` | `/publisher` | Portfolio build, preview, publish |
| `config` | `/config` | Profile management, deploy, rollback |
| `usage` | `/usage` | Token analytics dashboard |
| `api` | `/api` | JSON endpoints for HTMX partial updates |

## Backend Modules

### Scanner (`scanner.py`)

Scans `$PROJECTS_DIR` for project directories. For each:
1. Read METADATA.md → parse key:value fields
2. Read AGENTS.md / CLAUDE.md → extract endpoints, bookmarks
3. Read bin/ scripts → parse CommandCenter headers
4. Upsert into `projects` and `operations` tables

Runs asynchronously on startup (not blocking first page load). Triggered manually by rescan button.

### Process Engine (`engine.py`)

Launches bin/ scripts as background subprocesses.

1. Receive launch request (project_id, operation_id)
2. Create `runs` record with status STARTING
3. Fork subprocess: `bash bin/{script}.sh` from project root
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

### Usage Analyzer (`usage.py`)

Reads AI session JSONL logs (produced by ai engine, not produced by GAME).

A mechanism to scan the ai agent logs or to poll the ai agent to see
information similar to the anthropic /usage command so we can display
data to the user.  At present I have not found a solution.

## Routes (HTMX)

All screen interactions use HTMX for partial page updates. Server returns HTML fragments, not JSON.

| Method | Path | Returns | Trigger |
|--------|------|---------|---------|
| GET | `/` | Full dashboard page | Page load |
| POST | `/api/scan` | Status message | Rescan button |
| POST | `/api/run/{op_id}` | Updated button state | Operation click |
| POST | `/api/stop/{run_id}` | Updated button state | Stop click |
| POST | `/api/push/{project_id}` | Git status fragment | Push button |
| GET | `/api/project/{id}` | Project detail fragment | Row click |
| GET | `/processes` | Process list page | Nav link |
| GET | `/processes/{run_id}/log` | Log content fragment | View Log click |
| GET | `/publisher` | Publisher page | Nav link |
| POST | `/publisher/build` | Build status | Rebuild button |
| POST | `/publisher/publish` | Publish status | Publish button |
| GET | `/config` | Config page | Nav link |
| POST | `/config/deploy/{profile}` | Deploy status | Deploy button |
| POST | `/config/rollback/{id}` | Rollback status | Rollback button |
| GET | `/usage` | Usage page | Nav link |
| GET | `/health` | `{"status":"ok"}` | Health check |

## Directory Layout

```
GAME/
  app.py                 App factory (create_app)
  scanner.py             Project discovery
  engine.py              Process execution
  publisher.py           Portfolio builder
  config_engine.py       Config profile manager
  usage.py               Token analytics
  models.py              Database helpers, schema creation
  templates/
    base.html            Layout with nav bar
    dashboard.html       Main project list
    project_detail.html  Single project view
    processes.html       Process list and log viewer
    publisher.html       Publisher controls
    config.html          Config management
    usage.html           Usage analytics
    partials/            HTMX response fragments
  static/
    css/style.css        Custom styles (Bootstrap 5 dark theme)
    js/app.js            Client-side helpers
  bin/
    common.sh            Shared script functions
    start.sh             Start Flask dev server
    stop.sh              Stop server
    build_documentation.sh  Generate doc/
  data/
    game.db              SQLite database
    migrations/          Numbered SQL migration files
  config_engine/
    profiles/            YAML config profiles
    staged/              Git-committed staged configs
  doc/                   Generated documentation
  logs/                  Operation log files
```
