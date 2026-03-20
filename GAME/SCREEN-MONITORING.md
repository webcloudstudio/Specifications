# Screen: Monitoring

**Service health dashboard and event timeline.** Polls running services, shows status, alerts on failure.

## Route

```
GET /monitoring
```

## Layout

Two sections: Health Table (top), Event Timeline (bottom).

## Health Table

| Column | Source | Content |
|--------|--------|---------|
| Project name | `projects.display_name` | Standard row header |
| Endpoint | `port` + `health_endpoint` | e.g., `localhost:5001/health` |
| Status | Heartbeat poller | UP (green) / DOWN (red) / UNKNOWN (gray) badge |
| Last checked | `heartbeats.last_checked` | Timestamp |
| Response time | `heartbeats.response_ms` | Milliseconds |
| Uptime | `heartbeats.uptime_pct` | Rolling 24h percentage |

Only projects with both `port` and `health_endpoint` appear.

## Event Timeline

Chronological list of platform events from the `events` table. Each row:

| Column | Content |
|--------|---------|
| Timestamp | When it happened |
| Project | Which project (or "Platform") |
| Event | Type + summary (e.g., "operation_completed: Start Server exited 0") |

Filter by project or event type. Most recent events first.

## Alerts

Banner notification when a service changes state (UP→DOWN or DOWN→UP). Links to the affected project.

**States:** `UNKNOWN → UP → DOWN → UP` (cycle). SNOOZED suppresses alerts but continues polling.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Refresh | Button or auto-timer | Re-polls all health endpoints |
| Snooze | Click on alert | Suppresses alerts for that service |
| Filter events | Dropdown/text | Filters timeline |
| Click project | Name link | Navigates to SCREEN-PROJECT |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` (port, health) | `heartbeats` table |
| HTTP health endpoints | `events` table (state transitions) |
| Process engine (running state) | Alert notifications |

## Open Questions

- What should the polling interval be? Configurable per-project or global?
- Should alerts use browser notifications or just in-page banners?
