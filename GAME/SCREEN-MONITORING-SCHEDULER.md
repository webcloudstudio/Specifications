# Screen: Scheduler

| Field | Value |
|-------|-------|
| Version | 20260325 V1 |
| Route | `GET /scheduler` |
| Parent | — |
| Main Menu | Monitoring |
| Sub Menu | Scheduler |
| Tab Order | 1: Monitoring · 2: Scheduler · 3: Processes |
| Description | View and manage all scheduled operations. Enables/disables schedules and edits cron expressions. Scheduler runs as a background loop (see FUNCTIONALITY.md Flow 7). |

## Layout

Two sections stacked vertically: Schedule Table (top), Recent Schedule Events (bottom).

## Schedule Table

One row per operation that has a non-null `schedule` value. Sorted by project name, then operation name.

### Row Structure

| Column | Source | Content |
|--------|--------|---------|
| Status badge | `projects.status` | Standard status pill |
| Icon + project | `projects.display_name` | Standard project row header |
| Operation | `operations.name` | Operation display name |
| Category | `operations.category` | `service` / `local` / `maintenance` badge |
| Schedule | `operations.schedule` | Cron expression — inline editable |
| Enabled | `operations.schedule_enabled` | Toggle switch — on/off |
| Last Run | `operations.last_scheduled_run` | Timestamp or `—` if never run |
| Next Run | `operations.next_scheduled_run` | Calculated next fire time; `—` if disabled |
| Last Status | `op_runs.status` (most recent scheduled run) | DONE / ERROR / STOPPED badge |

### Schedule Inline Edit

Clicking the cron expression opens an inline editor for that row:

| Element | Behavior |
|---------|----------|
| Text input | Pre-filled with current cron expression |
| Validate | Real-time validation — shows human-readable description (e.g. "every day at 02:00") |
| Save | Writes new expression to `operations.schedule` in DB and patches `# Schedule:` header in the script file |
| Cancel | Reverts to read-only display |

Saving recalculates `next_scheduled_run` immediately.

### Enable/Disable Toggle

Clicking the toggle flips `operations.schedule_enabled`. No page reload — HTMX swap of the row. Does not alter the script file — allows pausing a schedule without removing the header.

## Bulk Controls

Action bar above the table:

| Control | Behavior |
|---------|----------|
| `Disable All` | Sets `schedule_enabled = false` for all shown rows |
| `Enable All` | Sets `schedule_enabled = true` for all rows that have a schedule |
| Project filter | Dropdown — filter rows by project |

## Recent Schedule Events

Last 30 rows from the `events` table where `event_type IN ('schedule_fired', 'schedule_missed')`. Columns:

| Column | Content |
|--------|---------|
| Timestamp | When it fired or was missed |
| Project | Which project |
| Operation | Script name |
| Event | `schedule_fired` (green) or `schedule_missed` (amber) badge |
| Status | Exit code / run outcome (linked to op_run if available) |

## Empty State

If no operations have a `# Schedule:` header:

> *No scheduled operations.*
> Add `# Schedule: <cron>` to a `bin/` script header to register it.

Shown centered, muted text, inside the table area.

## Startup Behavior

On platform startup, the scheduler loop starts automatically. Startup catch-up fires one immediate run for each missed schedule (per FUNCTIONALITY.md Flow 7). The Scheduler screen reflects what the loop last recorded — no additional polling is needed for the table; the Recent Events section auto-refreshes every 30 seconds via HTMX.

## Data Flow

| Reads | Writes |
|-------|--------|
| `operations` table (schedule, schedule_enabled, last/next run) | `operations.schedule_enabled` (toggle) |
| `op_runs` table (last scheduled run status) | `operations.schedule` + script `# Schedule:` header (cron edit) |
| `events` table (schedule_fired, schedule_missed) | `operations.next_scheduled_run` (recalculated on edit) |

## Open Questions

- Should the cron expression editor show a visual picker (minute/hour/day selectors) in addition to the raw expression?
	* Eventually yes, for now editing job data is done manually
- Should `schedule_missed` events trigger a visible alert banner on this screen?
	* yes  - it should have an clear icon
