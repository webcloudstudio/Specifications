# Architecture

**Version:** 20260320 V1
**Description:** Module layout, routes, and directory structure

Flask app factory with blueprints. Scanner, process engine, and publisher are backend modules feeding data to screen routes.

## App Factory

`create_app()` in `app.py`:
1. Load config from environment and `.env`
2. Initialize SQLite (create tables if missing, run migrations)
3. Register blueprints
4. Start async project scan on first request

## Blueprint

Single blueprint `cc` registered on `/`. All routes in `routes.py`.

## Backend Modules

| Module | Responsibility |
|--------|---------------|
| `scanner.py` | Scans $PROJECTS_DIR: reads METADATA.md, AGENTS.md, bin/ headers, filesystem flags. Upserts into DB. |
| `ops.py` + `spawn.py` | Launches bin/ scripts as subprocesses. Run/stop/log lifecycle. |
| `publisher.py` | Builds static portfolio from projects where card_show=true. |
| `db.py` | Database access helpers, migrations. |
| `models.py` | PROJECT_TYPES registry. |
| `claude_convention.py` | CLAUDE.md / AGENTS.md parsing. |

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | `/` | Full dashboard page |
| POST | `/api/scan` | Status message |
| POST | `/api/run/{op_id}` | Updated button state |
| POST | `/api/stop/{run_id}` | Updated button state |
| POST | `/api/push/{project_id}` | Git status fragment |
| GET | `/api/project/{id}` | Project detail fragment |
| GET | `/processes` | Process list page |
| GET | `/processes/{run_id}/log` | Log content fragment |
| GET | `/publisher` | Publisher page |
| POST | `/publisher/build` | Build status |
| POST | `/publisher/publish` | Publish status |
| GET | `/project-config` | Configuration page |
| GET | `/monitoring` | Monitoring page |
| GET | `/workflow` | Workflow board |
| GET | `/health` | `{"status":"ok"}` JSON |

## Directory Layout

```
GAME/
  app.py                 create_app()
  routes.py              All routes (blueprint: cc)
  scanner.py             Project discovery
  ops.py                 Operation launch/stop/status
  spawn.py               Subprocess management
  publisher.py           Portfolio builder
  models.py              PROJECT_TYPES registry
  db.py                  Database helpers + migrations
  claude_convention.py   AGENTS.md parsing
  templates/
    base.html            Layout with nav bar
    partials/            HTMX response fragments
  static/
    style.css            Dark theme styles
  bin/
    common.sh            Shared script functions
    start.sh             Start Flask dev server
    stop.sh              Stop server
    build_documentation.sh  Generate docs/
  data/
    game.db              SQLite database
  doc/                   Generated documentation
  logs/                  Operation log files
```

## Open Questions

- Should `usage_analyzer.py` remain? No working solution for reading AI session costs.
- Split `routes.py` into per-screen route files as screens grow?
