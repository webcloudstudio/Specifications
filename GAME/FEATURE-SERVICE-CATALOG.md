# Feature: Service Catalog API

**Version:** 20260323 V1
**Description:** REST API for service discovery and headless script execution with fire-and-poll lifecycle

Exposes two API families:

1. **Catalog** — `GET /api/catalog` returns every project's identity, port, health path, and registered scripts.
2. **Script Runner** — `POST /api/{name}/run/{script}` fires any bin/ script headlessly and returns a `run_id` for polling.

These are pure JSON endpoints (no HTMX). External tools, curl, and the companion SCREEN-CATALOG use them directly.

---

## Trigger

Catalog data is populated by the existing startup scan (`scanner.py`). No additional detection step — `GET /api/catalog` reads `projects` + `operations` tables only (no disk I/O).

Script execution reuses the existing process engine (`ops.py` / `spawn.py`) and `op_runs` table. No new subprocess management code.

---

## API Endpoints

### Service Catalog

```
GET /api/catalog
```

Returns all active projects with their exposed scripts.

**Response:**

```json
{
  "projects": [
    {
      "name": "conquer_2026",
      "display_name": "Conquer 2026",
      "short_description": "2026 strategy game",
      "port": 5010,
      "health_path": "/health",
      "base_url": "http://localhost:5010",
      "scripts": [
        {
          "script": "start",
          "name": "Start Server",
          "category": "Operations",
          "run_endpoint": "POST /api/conquer_2026/run/start",
          "script_endpoint": "GET /api/conquer_2026/script/start",
          "timeout": 300,
          "schedule": null,
          "last_run_id": 42,
          "last_run_status": "done",
          "last_run_at": "20260323_110000"
        },
        {
          "script": "scorecard",
          "name": "Scorecard",
          "category": "Workflow",
          "run_endpoint": "POST /api/conquer_2026/run/scorecard",
          "script_endpoint": "GET /api/conquer_2026/script/scorecard",
          "timeout": 60,
          "schedule": null,
          "last_run_id": null,
          "last_run_status": null,
          "last_run_at": null
        }
      ],
      "links": [
        { "label": "GitHub", "url": "https://github.com/user/conquer_2026" },
        { "label": "Live Site", "url": "https://user.github.io/conquer_2026" }
      ],
      "endpoints": [
        { "method": "GET",  "path": "/health",          "description": "Health check" },
        { "method": "POST", "path": "/api/game/move",   "description": "Make a move" },
        { "method": "GET",  "path": "/api/game/state",  "description": "Get game state" }
      ],
      "mcp_tools": [
        { "name": "get_state",    "description": "Get current game state" },
        { "name": "make_move",    "description": "Submit a move" }
      ]
    }
  ],
  "total_projects": 12,
  "total_scripts": 34,
  "generated_at": "20260323_120000"
}
```

| Field | Source |
|-------|--------|
| `name` | `projects.name` |
| `display_name` | `projects.display_name` |
| `short_description` | `projects.card_desc` or `projects.display_name` |
| `port` | `projects.port` |
| `health_path` | `projects.health_endpoint` |
| `base_url` | Constructed: `http://localhost:{port}` (null if no port) |
| `scripts[].script` | Basename of `operations.cmd` without `bin/` and extension |
| `scripts[].name` | `operations.name` |
| `scripts[].category` | `operations.category` — one of `Operations`, `Workflow`, `Global` |
| `scripts[].run_endpoint` | Constructed: `POST /api/{name}/run/{script}` |
| `scripts[].script_endpoint` | Constructed: `GET /api/{name}/script/{script}` — returns script content |
| `scripts[].timeout` | `operations.timeout` |
| `scripts[].schedule` | `operations.schedule` |
| `scripts[].last_run_*` | Most recent `op_runs` row for this operation |
| `links[]` | `projects.extra.links` — from `METADATA.md → ## Links` table |
| `endpoints[]` | `projects.extra.endpoints` — from `AGENTS.md → ## Endpoints` table |
| `mcp_tools[]` | `service_tools` table where `service_id` matches this project's MCP service |

Only projects with `is_active = 1` appear. Scripts with `is_url = 1` are excluded (not executable).

**Script slug derivation:** `bin/start.sh` → `start`, `bin/deploy.py` → `deploy`. If two scripts share the same base name, `.sh` takes priority.

---

### Script Content

```
GET /api/{name}/script/{script}
```

Returns the full content of a registered script. Used by the Service Catalog Script Viewer modal.

**Response 200:**

```json
{
  "project": "conquer_2026",
  "script": "start",
  "filename": "start.sh",
  "name": "Start Server",
  "category": "Operations",
  "content": "#!/bin/bash\n# CommandCenter Operation\n...",
  "run_endpoint": "POST /api/conquer_2026/run/start"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 404 | Project `{name}` not found |
| 404 | Script `{script}` not registered for that project |

Content is read directly from the script file at request time (not from the DB). This is intentional — the modal shows the actual current file, not a cached version.

---

### Fire Script

```
POST /api/{name}/run/{script}
```

| Param | Source |
|-------|--------|
| `{name}` | `projects.name` slug |
| `{script}` | Script basename (no `bin/`, no extension) |

**Request body:** optional JSON `{ "env": { "KEY": "VAL" } }` for injected environment vars.

**Response 202:**

```json
{
  "run_id": 42,
  "status": "running",
  "started_at": "20260323_120000",
  "poll_url": "/api/runs/42",
  "log_url": "/api/runs/42/log",
  "stop_url": "/api/runs/42/stop"
}
```

**Errors:**

| Code | Reason |
|------|--------|
| 404 | Project `{name}` not found |
| 404 | Script `{script}` not registered for that project |
| 409 | Script already running (same operation has `status = running`) |

---

### Poll Run Status

```
GET /api/runs/{run_id}
```

**Response 200:**

```json
{
  "run_id": 42,
  "status": "running",
  "exit_code": null,
  "started_at": "20260323_120000",
  "finished_at": null,
  "log_url": "/api/runs/42/log",
  "stop_url": "/api/runs/42/stop"
}
```

`status` values: `running` | `done` | `error` | `stopped`

Client polls until status is not `running`. Recommended interval: 2 seconds.

---

### Fetch Log

```
GET /api/runs/{run_id}/log
```

Returns full log content. Safe to call while the process is still running — returns whatever has been written so far.

**Response 200:**

```json
{
  "run_id": 42,
  "status": "running",
  "log": "...full log text...",
  "line_count": 37
}
```

Optional query param `?tail=N` returns the last N lines only.

---

### Stop Run

```
POST /api/runs/{run_id}/stop
```

Sends SIGTERM to the process group. Updates `op_runs.status` to `stopped`.

**Response 200:**

```json
{
  "run_id": 42,
  "status": "stopped"
}
```

Returns 404 if `run_id` not found; returns 200 (no-op) if already finished.

---

## Fire-and-Poll Pattern

Long-running scripts (servers, builds, deploys) follow this lifecycle:

```
1. POST /api/{name}/run/{script}
      ↓ 202 { run_id, poll_url }

2. GET /api/runs/{run_id}   ← poll every 2 seconds
      status: "running"     ← continue polling
      status: "done"        ← stop polling, fetch log
      status: "error"       ← stop polling, fetch log for diagnostics
      status: "stopped"     ← stop polling (user cancelled)

3. GET /api/runs/{run_id}/log
      ← full output

4. (optional) POST /api/runs/{run_id}/stop
      ← cancel mid-run
```

This is the same state machine the process engine already uses — no new DB fields.

---

## State Machine

Reuses the existing `op_runs` state machine:

```
STARTING → RUNNING → DONE
                   → ERROR     (non-zero exit)
                   → STOPPED   (SIGTERM)
```

`STARTING` transitions to `RUNNING` as soon as the subprocess PID is confirmed alive. The catalog API only reports `running` (not `starting`) — the distinction is internal.

---

## Implementation Notes

| Concern | Approach |
|---------|----------|
| JSON vs HTMX | These endpoints return JSON only. No HTML fragments. |
| Auth | None — localhost use only. |
| Concurrent runs | Allowed per operation unless the script itself prevents it. The 409 guard is opt-in per script via `# Singleton:` header (not yet implemented). |
| Schema changes | None — reads `projects`, `operations`; writes to `op_runs` via existing `ops.py`. |
| Catalog freshness | Reflects last scan. Stale if projects changed without a rescan. Includes `generated_at` so callers can detect staleness. |

---

## Reads / Writes

| Reads | Writes |
|-------|--------|
| `projects` (all active) | `op_runs` (new row on fire) |
| `operations` (all scripts) | `op_runs` (status update on finish) |
| `op_runs` (last run per operation) | `events` (operation_started, operation_completed) |
| Log files (log endpoint) | Log file (appended by process engine) |

---

## New Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/catalog` | Full catalog JSON (scripts, links, endpoints, MCP tools) |
| GET | `/api/{name}/script/{script}` | Script file content JSON |
| POST | `/api/{name}/run/{script}` | Run record JSON (202) |
| GET | `/api/runs/{run_id}` | Run status JSON |
| GET | `/api/runs/{run_id}/log` | Log content JSON |
| POST | `/api/runs/{run_id}/stop` | Stop confirmation JSON |

Screen route: `GET /servicecatalog`.

---

## Open Questions

- Should `GET /api/catalog` support `?project={name}` filtering? Yes — add optional `?name={name}` param returning a single-project response. Low cost, high convenience for callers who only need one project.
- Should the 409 guard be the default? Yes — 409 is always enforced. Add `?force=true` query param to bypass for scripts that support concurrent runs. The `# Singleton: true` header (not yet implemented) is the proper per-script opt-out.
- Should log fetching support chunked streaming? Not in V1. Full log via JSON is sufficient. Add SSE streaming as a P3 enhancement when logs exceed ~100KB regularly.
