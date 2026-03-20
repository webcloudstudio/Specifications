# Screen: Dashboard

**The main view.** Shows every discovered project with status, operations, and quick links. This is the landing page.

## Route

```
GET /
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Links,Actions,Help`.

## Layout

Full-width project list. One row per project. Nav bar at top per UI-GENERAL. Filter bar below nav.

## Per-Project Row

Uses the Baseline fixed columns (status badge, namespace, icon + name, cog) plus:

| Column | Source | Interaction |
|--------|--------|-------------|
| Links | `extra.links`, server link from `port` | Click → open URL in new tab |
| Actions | `operations` (category != maintenance) | Operation buttons per UI-GENERAL |
| Help | `has_docs`, `extra.doc_path` | Green Documentation button → `/project/{id}/doc/` in new tab |

Running projects show a green dot indicator in the project name cell.

## Project Detail (click project name or cog)

Navigates to SCREEN-PROJECT for the selected project.

## Actions

| Action | Trigger | Effect |
|--------|---------|--------|
| Run operation | Click button | Launches script, button shows running state |
| Stop operation | Click running button | Sends SIGTERM |
| Filter | Text/tag/status/namespace controls | Client-side row filtering |
| Rescan | Nav bar button | POST `/api/scan`, refreshes project list |
| Push | Per-project (shown when `git_unpushed > 0`) | POST `/api/push/{id}` |

## Startup Behavior

Scanner reads METADATA.md, AGENTS.md, and bin/ headers. Missing files produce compliance gaps, not errors. Projects removed from disk are marked inactive.

## Data Flow

| Reads | Writes |
|-------|--------|
| Project scanner results | Operation launch requests |
| Process engine run states | Git push commands |
| Tag color config | |

## Open Questions

- Should the dashboard auto-refresh running project status on a timer, or only on explicit action?
