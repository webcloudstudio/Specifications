# Screen: Monitoring — Processes

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /monitoring/processes` |
| Parent | — |
| Main Menu | MONITORING |
| Sub Menu | Processes |
| Tab Order | 1: Health · 2: Scheduler · 3: Processes |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Running and completed local operations launched through Marina. |
| Description | Process list and log viewer for local project operations. |
| Depends On | UI-GENERAL.md, FEATURE-BATCH-RUNNER.md |
| Provides | GET /monitoring/processes |

## Header KPIs

Left column uses three `mn-hdr-count` blocks: Running, Done, Error.

## Layout

Project-grouped process list. Log viewer appears inline when a run is selected.

## Process List

| Column | Source | Interaction |
|--------|--------|-------------|
| Project | run project | Expand row |
| Operation | run operation | Display |
| Status | run state | Badge |
| Started | run start time | Display |
| Duration | calculated | Display |
| Log | run log path | Open log viewer |
| Stop | running run | Stop button |

## Log Viewer

Monospace output panel. Auto-scroll while running. Header shows project, operation, status, start time, and Stop button when applicable.

## State Machine

`IDLE -> STARTING -> RUNNING -> DONE | ERROR | STOPPED`

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| View log | Button click | Load run log panel |
| Stop process | Button click | POST /api/runs/{run_id}/stop |
| Filter | Text/status filter | Client-side row filtering |
| Refresh | Button or 5s poll | Reload running rows and selected log |

## Open Questions
- None.
