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
| Description | Health dashboard and interleaved event log for local and published projects. |
| Depends On | UI-GENERAL.md, FEATURE-HEALTHCHECK.md, FEATURE-REPORT-INGEST.md |
| Provides | GET /monitoring |

## Header KPIs

Left column uses three `mn-hdr-count` blocks: Healthy, Warning, Error.

## Navigation

Top tabs: SETUP · PROJECTS · WORKFLOW · MONITORING. MONITORING sub-tabs: Health, Scheduler, Processes.

## Layout

Two stacked sections: Health Table, Event Log.

## Health Table

| Column | Source | Content |
|--------|--------|---------|
| Project | `projects.display_name` | Link to detail |
| Health | latest heartbeat / endpoint check | UP / WARN / DOWN badge |
| Endpoint | project health endpoint or Marina catalog health | URL text |
| Last Heartbeat | latest heartbeat timestamp | Relative time |
| Last Event | latest event summary | Truncated text |

## Event Log

| Column | Source |
|--------|--------|
| Time | event timestamp |
| Project | event project |
| Severity | INFO / WARN / ERROR |
| Message | event message |

Filters: text search, severity toggles, project selector. Default sort: newest first.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Refresh | Button or 30s poll | Reload health and events |
| Poll health | Button click | POST /api/health/poll |
| Click project | Project link | GET /projects/{id} |
| Click event | Event row | Show event details drawer |

## Open Questions
- None.
