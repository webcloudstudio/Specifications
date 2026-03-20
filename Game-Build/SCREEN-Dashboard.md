# Screen: Dashboard

Main screen. Shows all projects with status, operations, and quick actions.

## Route

```
GET /
```

## Layout

Full project list as rows. Each row uses the Standard Row Header (see UI.md).

## Columns

| Column | Content |
|--------|---------|
| Status + Name | Standard Row Header |
| Stack | `stack` field |
| Port | Port number, linked to localhost:{port} |
| Operations | Operation buttons per project (see UI.md Operation Buttons) |
| Git | Push button (visible when unpushed > 0), branch, dirty indicator |
| Links | From extra.links |
| Help | Documentation button (visible when has_docs=true) |
| CLAUDE | Button to open AGENTS.md modal (visible when has_claude=true) |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Run operation | Click operation button | POST /api/run/{op_id} → button shows running state |
| Stop operation | Click stop on running op | POST /api/stop/{run_id} → button reverts to idle |
| Git push | Click push button | POST /api/push/{project_id} → push button disappears |
| Rescan | Click refresh button | POST /api/scan → project list refreshes |
| View detail | Click project name | GET /api/project/{id} → detail panel expands |
| View CLAUDE.md | Click CLAUDE button | Opens modal with AGENTS.md content |

## Filter Bar

Standard filter bar (see UI.md): text search, status pills, tag pills, namespace dropdown.

## Open Questions

- Inline editing of status/port on dashboard, or only on Configuration screen?
- Show git_last_commit date as "last updated" indicator?
