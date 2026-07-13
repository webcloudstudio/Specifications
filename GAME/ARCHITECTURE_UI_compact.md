# SPEC: Architecture_Ui_Compact
<!-- Compacted from Specifications/GAME/ARCHITECTURE.md on 2026-05-11 by prompts/compact_architecture.md — regenerate via bin/compact_architecture.sh -->

# ARCHITECTURE: Architecture (UI Compact)

| Field       | Value |
|-------------|-------|
| Version     | 20260419 V1 |
| Description | Base Architecture Layout - Step 1 |

Flask app using the factory pattern (`create_app()` in `app.py`). Templates are rendered server-side via Jinja2. All screen interactions use HTMX for partial page updates — server returns HTML fragments, not JSON.

## Blueprints

Single blueprint `cc` registered on `/`. All routes live in `routes.py`.

## Routes (HTMX)

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
| GET | `/api/services` | JSON | List all registered services |
| GET | `/api/services/{name}` | JSON | Get one service manifest with tools |
| POST | `/api/services/{name}/{tool}` | JSON | Generic service tool dispatch |
| GET | `/api/mcp` | JSON | List registered MCP servers |
| POST | `/api/mcp/{id}/start` | JSON | Start MCP server |
| POST | `/api/mcp/{id}/stop` | JSON | Stop MCP server |
| POST | `/api/mcp/{id}/expose` | JSON | Expose MCP server on network port |
| POST | `/api/mcp/{id}/unexpose` | JSON | Unexpose MCP server |
| GET | `/api/mcp/{id}/config` | JSON | Get .mcp.json snippet |
| POST | `/api/services/workflow/create` | JSON | Create workflow instance |
| POST | `/api/services/workflow/transition` | JSON | Transition workflow state |
| GET | `/api/services/workflow/status` | JSON | Get workflow status + history |
| GET | `/api/services/workflow/list` | JSON | List workflows with filters |
| GET | `/api/services/workflow/list_types` | JSON | List workflow templates |
| POST | `/api/services/async-queue/submit` | JSON | Submit message to queue |
| GET | `/api/services/async-queue/status` | JSON | Check message status |
| GET | `/api/services/async-queue/list` | JSON | List queue messages |
| POST | `/api/services/async-queue/drain` | JSON | Drain pending messages |
| GET | `/api/services/async-queue/list_queues` | JSON | List queues with counts |

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
  service_registry.py    Service discovery and tool dispatch
  mcp_host.py            MCP server lifecycle management
  workflow_engine.py     Generic state machine service
  async_queue.py         File-based store-and-forward queue
  models.py              PROJECT_TYPES registry
  db.py                  Database access helpers
  claude_convention.py   CLAUDE.md / AGENTS.md parsing
  templates/             Flask/Jinja2 templates
    base.html            Layout shell (includes nav partials; no inline nav HTML)
    _nav_top.html        Top navigation bar partial
    _nav_sub.html        Sub-navigation bar partial (section-conditional)
    partials/            HTMX response fragments
  static/
    style.css            Custom styles (light-body dark-nav; see UI-GENERAL.md)
  bin/
    common.sh            Shared script functions
    common.py            Shared Python functions
    start.sh             Start Flask dev server
    stop.sh              Stop server
    build_documentation.sh  Generate docs/ and docs/index.html
  services/
    batch-runner.service.yaml   Platform service manifest
    workflow.service.yaml       Platform service manifest
    async-queue.service.yaml    Platform service manifest
  data/
    game.db              SQLite database
    tag_colors.json      Tag color assignments
    queues/              AsyncQueue JSONL files
      queue_config.yaml  Per-queue configuration
      archive/           Rotated completed messages
  docs/                  Generated documentation
  logs/                  Operation log files
  .env                   Local environment config (gitignored)
  .env.sample            Environment variable reference template
