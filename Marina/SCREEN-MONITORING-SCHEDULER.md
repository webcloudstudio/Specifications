# Screen: Monitoring — Scheduler

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /monitoring/scheduler` |
| Parent | — |
| Main Menu | MONITORING |
| Sub Menu | Scheduler |
| Tab Order | 1: Health · 2: Scheduler · 3: Processes |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Scheduled project operations and recent schedule events. |
| Description | Schedule table for operations with cron metadata and enable/disable controls. |
| Depends On | UI-GENERAL.md, FEATURE-BATCH-RUNNER.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /monitoring/scheduler |

## Header KPIs

Left column uses two `mn-hdr-count` blocks: Enabled and Missed.

## Layout

Two stacked sections: Schedule Table, Recent Schedule Events.

## Schedule Table

| Column | Source | Interaction |
|--------|--------|-------------|
| Project | service catalog | Link to detail |
| Operation | service catalog | Display |
| Schedule | operation schedule | Inline edit |
| Enabled | schedule enabled flag | Toggle |
| Last Run | latest scheduled run | Link to process log |
| Next Run | calculated next run | Display |
| Last Status | latest run status | Badge |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Edit cron | Blur / Save | POST /api/schedules/{operation_id} |
| Toggle schedule | Switch click | POST /api/schedules/{operation_id}/toggle |
| Enable all | Button click | POST /api/schedules/enable-visible |
| Disable all | Button click | POST /api/schedules/disable-visible |

## Empty State

If no operations have schedule metadata, show `No scheduled operations discovered.`

## Open Questions
- None.
