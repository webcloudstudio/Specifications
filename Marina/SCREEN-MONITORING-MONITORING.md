# Screen: Monitoring — Health

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /monitoring` |
| Parent | — |
| Main Menu | MONITORING |
| Sub Menu | Health · default |
| Tab Order | 1: Health · 2: Scheduler · 3: Processes |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Project health, heartbeats, and recent events reported through Marina. |
| Description | Command-center view of project health, events, alerts, and current operational state. |
| Depends On | UI-GENERAL.md, FEATURE-HEALTHCHECK.md, FEATURE-REPORT-INGEST.md |
| Provides | GET /monitoring |

## Header KPIs

Left column uses three `mn-hdr-count` blocks: Healthy, Warning, Error.

## Navigation

Top tabs: SETUP · PROJECTS · MONITORING. MONITORING sub-tabs: Health, Scheduler, Processes.

## Layout

Four sections: health table, alert/event stream, operational attention, and recent activity.

## Health Table

| Column | Source | Content |
|--------|--------|---------|
| Project | `projects.display_name` | Link to detail |
| Health | latest heartbeat / endpoint check | UP / WARN / DOWN badge |
| Endpoint | project health endpoint or Marina catalog health | URL text |
| Last Heartbeat | latest heartbeat timestamp | Relative time |
| Last Event | latest event summary | Truncated text |
| Active Runs | running process count | Link to Processes |
| Schedule | missed/next scheduled operation | Link to Scheduler |

## Event and Alert Stream

| Column | Source |
|--------|--------|
| Time | event timestamp |
| Project | event project |
| Severity | INFO / WARN / ERROR |
| Message | event message |
| Source | health check, run, scheduler, project, or cloud report |

Filters: text search, severity, project, namespace, tag, source, and acknowledged/unacknowledged state.
Default sort: newest first.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Refresh | Button or 30s poll | Reload health and events |
| Poll health | Button click | POST /api/health/poll |
| Click project | Project link | GET /projects/{id} |
| Click event | Event row | Show event details drawer |
| Acknowledge alert | Alert action | Record operator and time; remove from attention count |
| Open command surface | Project/action link | Navigate to the project or operation needing attention |

## Open Questions
- None.
