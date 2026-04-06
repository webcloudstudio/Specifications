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

### Publisher (`publisher.py` → `bin/homepage_build.py`)

Builds static portfolio site from METADATA.md fields using Jinja2 templates. No Astro, no npm.

1. Optionally sync templates from `$SPECIFICATIONS_PATH/GAME/templates/` → `$PUBLISHER_TARGET/templates/`
2. Load `config/site_config.md` (YAML frontmatter + Markdown body → `home_html`)
3. Scan `$PROJECTS_DIR` for projects where `show_on_homepage = true`; resolve card fields and tag colors
4. Render `$PUBLISHER_TARGET/templates/*.j2` with Jinja2 → write to `$PUBLISHER_TARGET/publish/`
5. Copy static assets (images, diagrams, project docs) to `$PUBLISHER_TARGET/publish/`

**Scripts:**

| Script | Purpose |
|--------|---------|
| `bin/homepage_build.sh` | Bash wrapper; delegates to `homepage_build.py` |
| `bin/homepage_review.sh` | Serve `$PUBLISHER_TARGET/publish/` via `python3 -m http.server` |
| `bin/homepage_publish.sh` | `git add -A && git commit && git push origin main` in `$PUBLISHER_TARGET` |

Deprecated: `bin/RebuildYourHomepage.sh`, `bin/LocalPreview.sh`, `bin/PushAndPublish.sh`.

**New env vars:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `PUBLISHER_TARGET` | sibling `My_Github/` | TARGET directory (configurable on install) |
| `HOMEPAGE_PREVIEW_PORT` | `4321` | Port for `homepage_review.sh` |

See `HOMEPAGE-PUBLISHER.md` for full specification including template variable contract and build algorithm.

### Health Monitor (`monitoring.py`)

Periodic service health poller and log event ingestor. Runs as two background threads started at app startup.

**Poller thread:** Checks each project with a port or `health_check_type`. Performs HTTP GET or TCP connect; writes `heartbeats` and `health_check_log`; appends `events` on state change. Per-project interval from `health_check_interval` column (default 60s).

**Log ingestor thread:** Runs every 60 seconds. Incrementally reads new bytes from `{project.path}/data/logs/*.log` using cursor positions in `log_positions`. Classifies lines against `log_filter` rules; writes matched lines to `events`. `junk` lines are discarded.

Provides: `start_poller()`, `stop_poller()`, `poll_now()`, `ingest_now()`.

### Scheduler (`scheduler.py`)

Background cron loop. Started at app startup. Runs every 60 seconds.

Queries `operations` where `schedule IS NOT NULL AND schedule_enabled = 1`. Evaluates each cron expression against current time using a standard cron parser. On match, delegates to the process engine (`ops.py`) to launch the operation. Tracks `last_scheduled_run` and calculates `next_scheduled_run`. On startup, checks for missed runs and fires one catch-up per operation.

Provides: `start_scheduler()`, `stop_scheduler()`, `tick()`.

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
| POST | `/publisher/{project_id}/card` | Updated card row fragment | Card field edit or checkbox |
| GET | `/project-config` | Configuration list | Nav link |
| GET | `/monitoring` | Monitoring page | Nav link |
| GET | `/workflow` | Workflow board | Nav link |
| GET | `/health` | `{"status":"ok"}` | Health check |
| GET | `/scheduler` | Scheduler page | Nav link |
| GET | `/servicecatalog` | Service Catalog page | Nav link |
| GET | `/prototypes` | Prototype list | Nav link |
| POST | `/api/prototypes/create` | JSON | New prototype scaffold |
| GET | `/api/prototypes` | JSON | List prototype dirs |
| GET | `/welcome` | Welcome page | Nav link (default `/`) |
| GET | `/project-setup` | Project Setup page | Nav link |
| GET | `/project-validation` | Validation page | Nav link |
| GET | `/project-maintenance` | Maintenance page | Nav link |
| GET | `/project-workflow` | Workflow screen | Nav link |
| POST | `/api/specification-tickets` | JSON | Create specification ticket + write file |
| POST | `/api/validate/{project_id}` | HTMX row fragment | Run validation checks |
| GET | `/settings/general` | Settings page | Settings gear icon → General tab |
| POST | `/settings/general` | HTMX form fragment | Save settings |
| GET | `/settings/tags` | Tag settings page | Settings gear icon → Tags tab |
| POST | `/settings/tags` | JSON | Save tag colors |
| GET | `/settings/help` | Help page | Settings gear icon → Help tab |
| GET | `/api/catalog` | JSON | Service catalog (all projects + scripts) |
| POST | `/api/{name}/run/{script}` | JSON 202 | Fire script headlessly |
| GET | `/api/runs/{run_id}` | JSON | Poll run status |
| GET | `/api/runs/{run_id}/log` | JSON | Fetch run log |
| POST | `/api/runs/{run_id}/stop` | JSON | Stop run |
| POST | `/api/heartbeat` | JSON 200 | Record script heartbeat |
| POST | `/api/events` | JSON 200 | Record script event |
| POST | `/api/health/poll` | JSON | Trigger immediate health poll |
| GET | `/api/health/{name}` | JSON | Current health for one project |
| POST | `/api/logs/ingest` | JSON | Trigger immediate log ingest |
| GET | `/api/github/repos` | JSON | Fetch GitHub repo list |

## Directory Layout

```
GAME/
  app.py                 App factory (create_app)
  routes.py              All routes (single blueprint: cc)
  scanner.py             Project discovery
  ops.py                 Operation launch/stop/status
  spawn.py               Subprocess management
  publisher.py           Portfolio builder
  monitoring.py          Health poller + log ingestor (background threads)
  scheduler.py           Cron loop for scheduled operations
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
    build_documentation.sh  Generate docs/ and docs/index.html
  data/
    game.db        SQLite database
    tag_colors.json  Tag color assignments
  docs/                  Generated documentation
  logs/                  Operation log files
  .env                   Local environment config (gitignored)
  .env.sample            Environment variable reference template
```

## Configuration

Environment variables loaded from `.env` at startup (via `python-dotenv`). A `.env.sample` at the project root documents all supported variables.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `FLASK_ENV` | No | `development` | Flask environment; `production` disables debug mode |
| `FLASK_DEBUG` | No | `1` | Enable Flask auto-reloader and debugger |
| `SECRET_KEY` | Yes | — | Flask session signing key |
| `PROJECTS_DIR` | Yes | — | Absolute path to the directory containing managed projects |
| `SPECIFICATIONS_PATH` | No | — | Absolute path to the Specifications repo (enables `has_specs` detection and Conform) |
| `GITHUB_USERNAME` | No | — | GitHub username for Project Setup screen repo discovery |
| `GITHUB_TOKEN` | No | — | GitHub personal access token (required for private repos) |
| `GAME_PORT` | No | `5000` | Port the GAME server listens on |
| `DATABASE_PATH` | No | `data/game.db` | Path to SQLite database file |

`.env.sample` ships in the repo as a reference template; `.env` is gitignored.

## Open Questions

- Should routes.py be split into per-screen blueprint modules as the app grows? Not at PROTOTYPE — single routes.py until the file exceeds ~800 lines or team size demands it. Per-screen blueprints add indirection without benefit at current scale.
