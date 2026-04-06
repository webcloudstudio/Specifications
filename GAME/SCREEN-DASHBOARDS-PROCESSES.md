# Screen: Processes

**Version:** 20260320 V1
**Row structure from:** SCREEN-DEFAULT (status badge, icon, project name — fixed columns only; does not use Baseline table or filter button)
**Description:** Specification for the Processes screen

**Live log viewer and process control.** Shows what is running, what ran, and the output.

## Menu Navigation

`Dashboards / Processes`

## Route

```
GET /processes
```

## Layout

Project list with expandable rows. If a project has running processes, they show inline with a View Log button. Expand a row to see prior run history.

## Process List

Standard header per SCREEN-DEFAULT (status badge, icon, name). Each row expands to show:

| Column | Source | Content |
|--------|--------|---------|
| Operation | `op_runs.name` | Derived from script filename |
| Status | `op_runs.status` | RUNNING / DONE / ERROR / STOPPED badge |
| Started | `op_runs.started_at` | Timestamp |
| Duration | Calculated | Elapsed (if running) or total |
| View Log | Button | Opens log viewer |
| Stop | Button | Sends SIGTERM (shown only when RUNNING) |

The list is sortable and filterable. Short names only — no full pathnames since project and script are known.

## Log Viewer

Monospace output area. Auto-scrolls while process is running. Stops on exit.

Header: project name, operation name, status badge, start time.

Controls: Stop (if running), Back to list.

## State Machine

```
IDLE → STARTING → RUNNING → DONE
                           → ERROR (non-zero exit)
                           → STOPPED (user cancelled)
```

Platform parses `[$PROJECT_NAME]` status lines from output to track transitions.

## Log Files

Named per CLAUDE_RULES: `logs/{project}_{script}_{yyyymmdd_hhmmss}.log`. Project name prepended for sorting.

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Expand row | Click project | Shows run history |
| View log | Click button | Opens log viewer panel |
| Stop process | Click Stop | SIGTERM to process group |
| Filter | Text/status | Client-side filtering |

## Data Flow

| Reads | Writes |
|-------|--------|
| `op_runs` table | Stop signal → process |
| Log files | Running count → nav bar badges |

## Open Questions

- Should log viewer support text search within output?
