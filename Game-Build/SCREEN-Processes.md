# Screen: Processes

**Version:** 20260320 V1  
**Description:** Spec for the Processes screen

View running and completed operations across all projects.

## Route

```
GET /processes
```

## Layout

List of op_runs records, most recent first.

## Columns

| Column | Content |
|--------|---------|
| Project | Project display_name |
| Operation | Operation name |
| Status | running / done / error / stopped (colored badge) |
| Started | started_at timestamp |
| Duration | elapsed or total time |
| Actions | View Log button, Stop button (if running) |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| View log | Click View Log | GET /processes/{run_id}/log → log content fragment |
| Stop | Click Stop on running process | POST /api/stop/{run_id} → status updates |

## Open Questions

- Auto-refresh running processes via HTMX polling?
- Filter by project or status?
- Max log display length before truncation?
