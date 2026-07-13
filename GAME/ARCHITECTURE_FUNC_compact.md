# SPEC: Architecture_Func_Compact
<!-- Compacted from Specifications/GAME/ARCHITECTURE.md on 2026-05-11 by prompts/compact_architecture.md — regenerate via bin/compact_architecture.sh -->

# ARCHITECTURE: Architecture (Functionality Compact)

| Field       | Value |
|-------------|-------|
| Version     | 20260419 V1 |
| Description | Base Architecture Layout - Step 1 |

Flask app with blueprints. App factory pattern. Scanner, process engine, and publisher are backend modules that feed data to the screen routes.

## App Factory

`create_app()` in `app.py`. Returns a configured Flask instance.

1. Load config from environment and `.env`
2. Initialize SQLite database (create tables if missing, run migrations)
3. Register blueprints
4. Start async project scan on first request

## Blueprints

Single blueprint `cc` registered on `/`. All routes live in `routes.py`.

## Backend Modules

- **`scanner.py`** — Scans `$PROJECTS_DIR` for project directories; reads METADATA.md, AGENTS.md, and bin/ headers; upserts into `projects` and `operations` tables; calls GitHub API for repo counts; writes `platform_stats`.
- **`ops.py` + `spawn.py`** — Launches bin/ scripts as background subprocesses; captures stdout/stderr to log files; tracks run status in `runs` table.
- **`publisher.py` → `bin/homepage_build.py`** — Builds static portfolio site from METADATA.md fields using Jinja2 templates; syncs templates from Specifications; renders to `$PUBLISHER_TARGET/publish/`.
- **`monitoring.py`** — Periodic health poller (HTTP GET or TCP connect per project) and log ingestor (incremental reads from `data/logs/*.log`); runs as two background threads; writes `heartbeats`, `health_check_log`, and `events`.
- **`scheduler.py`** — Background cron loop; evaluates cron expressions against operations where `schedule IS NOT NULL AND schedule_enabled = 1`; delegates to ops.py; tracks `last_scheduled_run` / `next_scheduled_run`; fires catch-up on startup.
- **`service_registry.py`** — Discovers platform, project, and MCP service manifests (`*.service.yaml`); upserts into `services` and `service_tools` tables; dispatches tool calls via `dispatch_tool()`.
- **`mcp_host.py`** — Manages MCP server lifecycle; discovers manifests in `mcp/*.service.yaml`; starts/stops processes via process engine; assigns ports from configurable range (default 9100–9199).
- **`workflow_engine.py`** — Generic state machine; loads templates from `workflow_templates`; creates instances, validates and executes transitions, records history, emits `workflow_transition` events.
- **`async_queue.py`** — File-based store-and-forward queue; reads/writes JSONL in `data/queues/`; drains via `service_registry.dispatch_tool()`; manages rotation and archival.
- **`models.py`** — `PROJECT_TYPES` registry.
- **`db.py`** — Database access helpers.
- **`claude_convention.py`** — CLAUDE.md / AGENTS.md parsing.

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
| `MCP_PORT_RANGE_START` | No | `9100` | First port in the MCP server port range |
| `MCP_PORT_RANGE_END` | No | `9199` | Last port in the MCP server port range |

`.env.sample` ships in the repo as a reference template; `.env` is gitignored.

`bin/start.sh` must read `GAME_PORT` from `.env` before starting Flask, defaulting to `5000` if unset.
