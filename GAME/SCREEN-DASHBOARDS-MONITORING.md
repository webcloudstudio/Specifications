# Screen: Monitoring

**Version:** 20260407 V2
**Description:** Service health dashboard and interleaved event log for all running projects.

## Menu Navigation

Main Menu: Monitoring
Sub Menu: Monitoring (Default)

## Route

```
GET /monitoring
```

## Layout

Two sections stacked vertically: Health Table (top), Event Log (bottom).

```
┌──────────────────────────────────────────────────────────┐
│  Health Table                                            │
│  ──────────────────────────────────────────────────────  │
│  [project rows with up/down status]                      │
├──────────────────────────────────────────────────────────┤
│  Event Log                                               │
│  [🔍 Filter events...]  [⚠ Warnings] [✖ Errors]         │
│  ──────────────────────────────────────────────────────  │
│  Timestamp ▼  | Project     | Severity | Message        │
│  ────────────────────────────────────────────────────── │
│  12:34:01     | MyApp       | ERROR    | exit code 1    │
│  12:33:58     | CoreService | WARN     | slow response  │
│  12:33:55     | Platform    | INFO     | scan completed │
│  ...                                                     │
└──────────────────────────────────────────────────────────┘
```

---

## Health Table

Only projects with both `port` and `health_endpoint` appear.

| Column | Source | Content |
|--------|--------|---------|
| Project | `projects.display_name` | Standard row header |
| Endpoint | `port` + `health_endpoint` | e.g., `localhost:5001/health` |
| Status | Heartbeat poller | `UP` (green) / `DOWN` (red) / `UNKNOWN` (gray) badge |
| Last checked | `heartbeats.last_checked` | Timestamp |
| Response time | `heartbeats.response_ms` | Milliseconds |
| Uptime | `heartbeats.uptime_pct` | Rolling 24h percentage |

Column headers are clickable to sort. Current sort direction shown with ▲/▼ arrow.

### Alerts

Banner notification when a service changes state (UP→DOWN or DOWN→UP). Links to the affected project. Snooze suppresses alerts for that service but continues polling.

---

## Event Log

Interleaved chronological log of events from all projects that have been started (i.e., have appeared in the process engine since last restart). Reads from the `events` table. Most recent first.

### Filter Bar

Rendered above the log table. All filters are client-side.

| Control | Type | Behavior |
|---------|------|----------|
| Text search | Input (`🔍 Filter events…`) | Substring match on Project + Message fields. Case-insensitive. |
| Warnings toggle | Checkbox `⚠ Warnings` | Show/hide rows where `severity = WARN`. Default: checked (shown). |
| Errors toggle | Checkbox `✖ Errors` | Show/hide rows where `severity = ERROR`. Default: checked (shown). |

INFO rows are always shown when no filters exclude them. The combination of checkboxes works as inclusive show/hide (unchecking hides that severity level).

### Log Table

| Column | Source | Content | Sortable |
|--------|--------|---------|---------|
| Timestamp | `events.created_at` | `HH:MM:SS` (date shown on date change rows) | Yes — default sort, descending |
| Project | `events.project_id` → `projects.display_name` | Project name or "Platform" for system events | Yes |
| Severity | `events.severity` | Colored pill: `INFO` (muted) / `WARN` (amber) / `ERROR` (red) | Yes |
| Message | `events.summary` | Full event message; truncate at 120 chars with tooltip for rest | No |

Clicking any column header sorts the table by that column. Click again to reverse direction. ▲/▼ arrow shown on active sort column.

### Severity Color Standards

| Severity | Color | Condition |
|----------|-------|-----------|
| INFO | Muted gray | Normal operation events |
| WARN | Amber `#fdab3d` | Slow response, exit code warnings, non-fatal errors |
| ERROR | Red `#e44258` | Process exits with error, service DOWN, unhandled exceptions |

### Default State

On page load: all severities shown, no text filter, sorted by Timestamp descending. Shows events from all projects that have been started. Limit: 500 rows; older rows require manual scroll or pagination (future).

---

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Sort column | Click header | Sorts table by that column; toggles direction |
| Filter text | Type in search | Filters rows client-side in real time |
| Toggle severity | Click checkbox | Shows/hides that severity level |
| Refresh | Button or auto-timer | Reloads health endpoints and appends new events |
| Snooze alert | Click on alert banner | Suppresses alerts for that service |
| Click project name | Name link | Navigates to SCREEN-DRILLDOWN-PROJECT |

---

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` (port, health_endpoint, display_name) | `heartbeats` table (poll results) |
| HTTP health endpoints | `events` table (state-change entries) |
| `events` table (all severity levels, all started projects) | Alert snooze state |

---

## Open Questions

- Should the event log auto-append new rows via polling (SSE or HTMX polling), or require a manual refresh?
- Should the log limit of 500 rows be configurable in Settings?
