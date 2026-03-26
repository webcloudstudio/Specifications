# Screen: Service Catalog

**Version:** 20260323 V1
**Row structure from:** SCREEN-DEFAULT (status badge, icon, project name — row header only; does not use Baseline table or filter button)
**Description:** Spec for the Service Catalog screen — browse exposed API endpoints, fire scripts, and stream logs

API-oriented view of all projects and their registered scripts. Each project shows its endpoint surface; scripts can be run directly from the screen. Active and past runs are visible inline with live log output.

## Menu Navigation

`Dashboards / Service Catalog`

## Route

```
GET /servicecatalog
```

## Layout

Two-panel. Left: project list (accordion). Right: detail panel for the selected project.

```
┌─────────────────────┬──────────────────────────────────────────┐
│  Project List       │  Project: My App                         │
│  ─────────────────  │  Port: 5001  Health: /health  ACTIVE     │
│  ▶ My App           │  ─────────────────────────────────────── │
│  ▶ Other Project    │  Scripts                                  │
│  ...                │  start   service   POST /api/myapp/run/.. │
│                     │  test    local     POST /api/myapp/run/.. │
│                     │  ─────────────────────────────────────── │
│                     │  Active Runs        Recent Runs           │
│                     │  start  RUNNING     deploy  done 2m ago   │
└─────────────────────┴──────────────────────────────────────────┘
```

On narrow viewports: project list collapses to a selector dropdown; detail panel takes full width.

## Project List (left panel)

Sorted by name. Each row:

| Element | Content |
|---------|---------|
| Status badge | `projects.status` |
| Icon + name | `projects.display_name` |
| Script count | Number of registered scripts (dim badge) |
| Health indicator | Green dot if UP, red if DOWN, gray if unmonitored |

Clicking a row loads the detail panel for that project. Selected row highlighted. No filter bar — project count is manageable.

## Detail Panel (right panel)

### Project Header

| Field | Source |
|-------|--------|
| Display name | `projects.display_name` |
| Status badge | `projects.status` |
| Port | `projects.port` |
| Health path | `projects.health_endpoint` |
| Base URL | `http://localhost:{port}` (link, opens new tab) |
| Last scanned | `projects.last_scanned` |

Rescan button (small, top-right): triggers `POST /api/scan` for this project only, then refreshes the panel.

### Scripts Table

One row per registered operation for this project.

| Column | Content |
|--------|---------|
| Name | `operations.name` |
| Category | Badge: service / local / maintenance |
| Endpoint | `POST /api/{name}/run/{script}` — click to copy |
| Timeout | `operations.timeout` (seconds; dim if not set) |
| Last Run | Relative time + status badge of most recent `op_runs` row |
| Actions | **Run** button; **Log** button (shown when last run exists) |

**Curl copy:** Clicking the endpoint cell copies `curl -X POST http://localhost:{GAME_PORT}/api/{name}/run/{script}` to clipboard. Toast confirmation.

### Run Controls

**Run button behavior:**
1. Fires `POST /api/{name}/run/{script}`
2. Button changes to `Running…` with spinner
3. Inline status row appears below the script row (see Active Run Row below)
4. Button remains disabled until run completes or is stopped

**Active Run Row** (inline, below the triggering script row):

| Element | Content |
|---------|---------|
| Run ID | `#42` |
| Status badge | Polls `GET /api/runs/{run_id}` every 2 seconds; badge cycles RUNNING → DONE / ERROR / STOPPED |
| Duration | Elapsed seconds (live) |
| Stop button | `POST /api/runs/{run_id}/stop` — shown only while RUNNING |
| View Log button | Opens log drawer (see below) |

Polling stops when status leaves `running`. Badge color: blue = running, green = done, red = error, gray = stopped.

### Log Drawer

Slide-in panel from the right (or bottom on narrow screens). Opens when "View Log" is clicked.

| Element | Content |
|---------|---------|
| Header | Project name + script name + run ID + status badge |
| Log area | Monospace, scrollable, auto-scrolls while RUNNING |
| Source | `GET /api/runs/{run_id}/log` — fetched on open; re-fetched every 3 seconds while RUNNING |
| Stop button | Shown while RUNNING |
| Close | X button or Escape |
| Download | Downloads log as `.log` file (full content) |

Live update stops when status leaves `running`.

### Recent Runs

Below the scripts table. Last 10 runs across all scripts for this project.

| Column | Content |
|--------|---------|
| Script | Script name |
| Status | Badge |
| Started | Relative time |
| Duration | Seconds |
| Exit | Exit code |
| Log | Link to open log drawer for that run |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Select project | Click row | Loads detail panel (HTMX swap) |
| Run script | Click Run | POST fire → inline status row |
| Stop run | Click Stop | POST stop → status updates to stopped |
| View log | Click View Log | Opens log drawer |
| Copy endpoint | Click endpoint cell | Copies curl command to clipboard |
| Rescan project | Rescan button | POST /api/scan → refreshes panel |
| Download log | Download button | Browser download of log file |

## Data Flow

| Reads | Writes |
|-------|--------|
| `GET /api/catalog` (initial load) | `POST /api/{name}/run/{script}` (fire) |
| `GET /api/runs/{run_id}` (polling) | `POST /api/runs/{run_id}/stop` (stop) |
| `GET /api/runs/{run_id}/log` (log) | `POST /api/scan` (rescan) |

Screen uses HTMX for project selection / panel swaps. Run controls and polling use plain JS fetch (JSON API, not HTMX fragments).

## Open Questions

- Should the log drawer support text search within output?
- Should the screen auto-select the first project on load, or start with the panel empty?
- Should active runs from other sessions (e.g., started via curl) appear in the Active Runs section?
