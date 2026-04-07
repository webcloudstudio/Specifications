# Screen: Service Catalog

**Version:** 2026-04-06 V2
**Row structure from:** SCREEN-DEFAULT (status badge, icon, project name — row header only; does not use Baseline table or filter button)
**Description:** Specification for the Service Catalog screen — browse services, fire scripts, stream logs, manage MCP servers, and monitor queues

Service-oriented view of the platform. Shows all registered services (platform and project-provided) across all transports: REST, CLI, MCP, async queue, and web UI. Each service shows its tools, available transports, and operational status. Scripts can be run directly. MCP servers can be started, stopped, and exposed. Queue depths are visible at a glance.

## Menu Navigation

`Dashboards / Service Catalog`

## Route

```
GET /servicecatalog
```

## Layout

Three-panel. Left: service list (grouped). Top-right: service detail. Bottom-right: activity feed (recent runs, queue drains, MCP events).

```
┌──────────────────────┬──────────────────────────────────────────┐
│  Services            │  Service: Batch Runner                    │
│  ──────────────────  │  Platform service  v1.0.0                 │
│                      │  Transports: REST CLI MCP                 │
│  PLATFORM SERVICES   │  ──────────────────────────────────────── │
│  ● Batch Runner      │  Tools                                    │
│  ● Workflow          │  run_script  POST /api/services/batch-r.. │
│  ● AsyncQueue        │  run_status  GET  /api/services/batch-r.. │
│                      │  run_log     GET  /api/services/batch-r.. │
│  PROJECT SERVICES    │  ──────────────────────────────────────── │
│  ▶ MyApp             │  Active Runs        Recent Runs           │
│    ● pricing (MCP)   │  deploy  RUNNING    test  done 2m ago     │
│  ▶ Other Project     │                                           │
│    ● sync (REST)     ├──────────────────────────────────────────┤
│                      │  Activity                                 │
│  ℹ Button Key        │  14:02 batch-runner/run_script myapp/dep  │
│                      │  14:01 async-queue/drain voice (3 msgs)   │
│                      │  13:58 workflow/transition ticket-42 →test │
└──────────────────────┴──────────────────────────────────────────┘
```

On narrow viewports: service list collapses to a selector dropdown; panels stack vertically.

## Help Icon and Button Key

A help icon (ℹ circle-info) is pinned at the bottom of the left panel. Clicking it opens a popover with a legend explaining the colored indicators used throughout the screen:

| Indicator | Meaning |
|-----------|---------|
| Green dot (●) | Service healthy / MCP server running |
| Yellow dot (●) | Service degraded / queue has pending items |
| Red dot (●) | Service error / MCP server failed |
| Gray dot (●) | Service stopped / not monitored |
| Blue badge | REST transport available |
| Green badge | CLI transport available |
| Purple badge | MCP transport available |
| Orange badge | Async transport available |
| Pulsing ring | Operation currently running |

The popover also shows a compact transport legend:
- **REST** — call via HTTP from any language
- **CLI** — call via `game-cli` from bash scripts
- **MCP** — call from Claude or other AI agents
- **Async** — submit to file queue, processed on drain

The help icon badge shows "?" and is always visible. Dismiss popover by clicking outside or pressing Escape.

## Service List (left panel)

Grouped by source: **Platform Services** (from GAME), then **Project Services** (from managed projects, grouped by project name as collapsible sections).

Each service row:

| Element | Content |
|---------|---------|
| Health dot | Colored indicator (see Button Key) |
| Service name | From manifest `display_name` or `name` |
| Transport badges | Small colored pills showing enabled transports |
| Type label | `(MCP)` / `(REST)` / `(Queue)` for project services — dim text |

Clicking a service loads the detail panel. Selected row highlighted.

## Detail Panel (top-right)

### Service Header

| Field | Source |
|-------|--------|
| Service name | `services.display_name` or `services.name` |
| Source | "Platform service" or "Project: {name}" |
| Version | From manifest |
| Description | From manifest |
| Transport badges | Colored badges for each enabled transport with labels |

### Tools Table

One row per tool defined in the service manifest.

| Column | Content |
|--------|---------|
| Name | Tool name |
| Description | One-line description from manifest |
| Endpoint | REST path (click to copy curl command) |
| CLI | `game-cli {service} {tool}` (click to copy) |
| Actions | **Try** button (opens inline form with input fields from schema) |

**Try button behavior:**
1. Opens an inline form below the tool row with input fields generated from the tool's input schema
2. User fills in required fields
3. Submit fires `POST /api/services/{service}/{tool}` with the form data as JSON
4. Response shown inline below the form
5. For batch-runner tools: response includes run_id and auto-opens the active run tracker

### MCP Controls (shown only for MCP-enabled services)

| Element | Content |
|---------|---------|
| MCP Status | Running / Stopped / Error badge |
| Expose toggle | Switch: exposed (network port) vs. unexposed (stdio only) |
| Port | Assigned port when exposed |
| Config snippet | "Copy Config" button — copies `.mcp.json` snippet to clipboard |
| Start / Stop | Buttons to manage the MCP server process |

### Queue Status (shown only for async-enabled services or AsyncQueue itself)

| Element | Content |
|---------|---------|
| Queue name(s) | List of queues this service reads from |
| Pending | Count of pending messages |
| Processing | Count of currently processing messages |
| Last drained | Timestamp of last drain |
| Drain button | Triggers `POST /api/services/async-queue/drain?queue={name}` |

### Run Controls

Same as V1: Run button fires scripts, inline status row shows active runs with polling, View Log opens the log drawer. No changes to existing behavior.

### Active Run Row (inline, below the triggering tool row)

| Element | Content |
|---------|---------|
| Run ID | `#42` |
| Status badge | Polls `GET /api/runs/{run_id}` every 2 seconds; badge cycles RUNNING → DONE / ERROR / STOPPED |
| Duration | Elapsed seconds (live) |
| Stop button | `POST /api/runs/{run_id}/stop` — shown only while RUNNING |
| View Log button | Opens log drawer |

### Log Drawer

Slide-in panel from the right (or bottom on narrow screens). Same as V1:

| Element | Content |
|---------|---------|
| Header | Service name + tool name + run ID + status badge |
| Log area | Monospace, scrollable, auto-scrolls while RUNNING |
| Source | `GET /api/runs/{run_id}/log` — re-fetched every 3 seconds while RUNNING |
| Stop button | Shown while RUNNING |
| Close | X button or Escape |
| Download | Downloads log as `.log` file |

### Recent Runs

Below the tools table. Last 10 runs for this service (across all tools).

| Column | Content |
|--------|---------|
| Tool | Tool name |
| Status | Badge |
| Started | Relative time |
| Duration | Seconds |
| Exit | Exit code |
| Log | Link to open log drawer |

## Activity Feed (bottom-right panel)

Chronological feed of recent service activity across all services. Sources:
- Batch Runner: operation started/completed/failed
- Workflow: state transitions
- AsyncQueue: drain events, message submissions
- MCP: server started/stopped/exposed

Each entry: timestamp, service name, tool name, one-line summary. Clicking an entry navigates to the relevant service detail.

Auto-refreshes every 10 seconds. Shows last 50 entries. Filter dropdown: All / Batch Runner / Workflow / Queue / MCP.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Select service | Click row | Loads detail panel (HTMX swap) |
| Try tool | Click Try | Opens inline form with schema-driven inputs |
| Run script | Click Run on batch-runner tool | POST fire → inline status row |
| Stop run | Click Stop | POST stop → status updates |
| View log | Click View Log | Opens log drawer |
| Copy endpoint | Click endpoint cell | Copies curl command to clipboard |
| Copy CLI | Click CLI cell | Copies game-cli command to clipboard |
| Copy MCP config | Copy Config button | Copies .mcp.json snippet |
| Expose MCP | Toggle expose switch | POST expose → starts MCP server on port |
| Drain queue | Drain button | POST drain → processes pending messages |
| View help | Click ℹ icon | Opens button key popover |

## Data Flow

| Reads | Writes |
|-------|--------|
| `services` table (all active) | `op_runs` (via batch-runner) |
| `service_tools` table | `mcp_servers` (expose/unexpose/start/stop) |
| `mcp_servers` table (status, port) | `events` (service activity) |
| `op_runs` (recent runs) | Queue files (drain) |
| Queue files (pending counts) | |
| `events` (activity feed) | |

## Open Questions

- Should the Try button support saving and replaying tool invocations (like Postman collections)? Useful for repeated testing. Could store saved invocations in a `service_invocations` table.
- Should the Activity Feed support WebSocket or SSE for real-time updates instead of polling? Polling is simpler but misses events between refreshes.
- Should project services be auto-collapsed in the left panel, or expanded by default? Auto-collapsed if there are more than 5 projects to avoid overwhelming the list.
