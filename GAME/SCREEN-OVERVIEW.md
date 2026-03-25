# Screen: Dashboard

**Version:** 20260320 V1
**Extends:** SCREEN-DEFAULT
**Description:** Spec for the Dashboard screen

**The main view.** Shows every discovered project with status, operations, and quick links. This is the landing page.

## Menu Navigation

`Projects / Overview` 

## Route

```
GET /
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Links,Actions,Help`.

## Layout

Full-width project list. One row per project. Two-tier nav at top per UI-GENERAL; filter button in project sub-bar. Text/tag filter controls below sub-bar.

## Middle Columns

Renders Baseline with `columns=Links,Actions,Help`. Inherits all fixed columns and filter button from SCREEN-DEFAULT.

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
