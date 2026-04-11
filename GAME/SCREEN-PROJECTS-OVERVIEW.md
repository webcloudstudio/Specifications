# Screen: Dashboard

**Version:** 20260407 V2
**Extends:** SCREEN-DEFAULT
**Description:** Default Projects view. Discovered projects with status, operations, links, and documentation.

**The main view.** Shows every discovered project with status, operations, and quick links. Default screen for the Projects tab and the app root.

## Menu Navigation

Main Menu: Projects
Sub Menu: Dashboard (Default)
Inherits From: SCREEN-DEFAULT

## Route

```
GET /
GET /projects/dashboard   (alias)
```

## Layout

Full-width project list. Action bar at top of page content (filter controls + Rescan). Project rows below.

```
┌────────────────────────────────────────────────────┐
│  [🔍 Filter projects...]  [status pills]  [Rescan] │
│  ──────────────────────────────────────────────── │
│  ● ACTIVE   MyApp      [Start] [Stop]  [↗] [📄] ⚙ │
│  ● PROTO    NewThing   [Build]         [↗] [📄] ⚙ │
│  ● IDEA     Draft      [Run]           [↗]      ⚙ │
│  ...                                               │
└────────────────────────────────────────────────────┘
```

## Action Bar

Rendered at the top of the page content, below the sub-bar. Not in the sub-bar.

| Control | Type | Behavior |
|---------|------|----------|
| Filter input | Text input | Client-side filter by project name. Placeholder: "Filter projects…" |
| Status pills | Toggle buttons | Show/hide rows by status: `normal` (default, hides IDEA + ARCHIVED) / `all` / `idea` / `archive`. State encoded as `?filter=` URL param. |
| Namespace filter | Dropdown | Filter by namespace. Hidden when only one namespace exists. |
| **Rescan Your Projects** | Button (outline, right-aligned) | POST `/api/scan`; refreshes project list in place. |

Filters are client-side (no server round-trip). Rescan triggers a server scan then reloads the list via HTMX.

## Columns

Explicit column set — does not vary by URL params. Fixed order:

| # | Column | Source | Interaction |
|---|--------|--------|-------------|
| 1 | Status badge | `projects.status` | Display-only. Read-only colored pill. No click action. To change status use project detail (⚙) or Configuration screen. |
| 2 | Namespace badge | `projects.namespace` | Hidden when value is `development`. |
| 3 | Icon + Name | `projects.project_type`, `projects.display_name` | Running projects show a green dot (●) before the name. Name links to `/project/{id}`. |
| 4 | Actions | `operations` (category ≠ maintenance) | Operation buttons per UI-GENERAL. Run/stop per process engine state. |
| 5 | Links | `projects.extra.links`, `projects.port` | Link buttons. Falls back to server link when `port` is set. Opens in new tab. |
| 6 | Help | `projects.has_docs`, `projects.extra.doc_path` | Green Documentation button → proxy route → new tab. Shown only when `has_docs` is true (any of `doc*/index.htm*` exists). |
| 7 | Settings (cog) | — | Links to `/project/{id}` (project detail / inline editor). |

No Tags column. No Stack column. No Configuration column. No Maintenance column on this view.

## Project Detail (click name or cog)

Navigates to SCREEN-DRILLDOWN-PROJECT for the selected project.

## Startup Behavior

Scanner reads METADATA.md, AGENTS.md, and bin/ headers. Missing files produce compliance gaps, not errors. Projects removed from disk are marked inactive.

## Data Flow

| Reads | Writes |
|-------|--------|
| Project scanner results | Operation launch requests (POST `/api/run/{id}/{op}`) |
| Process engine run states | Stop requests (POST `/api/stop/{id}/{op}`) |
| `PROJECTS_DIR` (env) | Git push requests (POST `/api/push/{id}`, shown when `git_unpushed > 0`) |
|  | Rescan trigger (POST `/api/scan`) |

## Open Questions

- Should the Dashboard auto-refresh running project status on a timer, or only on explicit action?
- Should the Push button (shown when `git_unpushed > 0`) remain per-row, or move to project detail only?
