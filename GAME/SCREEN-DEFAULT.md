# Screen: Baseline Layout

| Field | Value |
|-------|-------|
| Version | 20260320 V1 |
| Route | `GET /default?title=...&columns=...&filter=...&sort=...` |
| Parent | — |
| Main Menu | — |
| Sub Menu | — |
| Tab Order | — |
| Description | Abstract — base layout, not a routed screen. Reusable sortable, filterable project/prototype list. Screens that extend this declare `Parent: SCREEN-DEFAULT` and specify their middle columns. |

## Route Parameters

| Param | Default | Purpose |
|-------|---------|---------|
| `title` | DEFAULT | Section header and nav label |
| `columns` | Links,Actions,Help | Comma-separated middle column keys |
| `filter` | normal | Filter state: `normal` / `all` / `idea` / `archive` |
| `sort` | name | `name`, `status_asc`, `status_desc` |

## Layout

Full viewport width — no max-width cap. Sortable table. Column header click sorts; current direction shown with arrows.

## Filter Controls

Each screen that uses this baseline carries its own filter controls in the page action bar. The controls below are the standard set — screens may add extra controls (e.g. Rescan).

### Standard Filter Bar Controls

| Control | Type | Behavior |
|---------|------|----------|
| Text search | Text input | Free-form substring match on project name and description. Real-time client-side filter. Placeholder: "Search name or description…" |
| Status pills | Toggle buttons | Show/hide rows by status. State encoded as `?filter=` URL param. |
| Namespace dropdown | Dropdown | Filter by namespace. Hidden when only one namespace exists. State encoded as `?namespace=` URL param. |

Status filter states:

| State | Shows |
|-------|-------|
| `normal` | All except IDEA and ARCHIVED |
| `all` | All projects |
| `idea` | Status = IDEA only |
| `archive` | Status = ARCHIVED only |

## Table Structure

### Fixed Columns (every row)

| Position | Content | Source | Interaction |
|----------|---------|--------|-------------|
| First | Status badge | `projects.status` | Display-only by default. Screens that enable status editing (e.g. Configuration) specify click-to-cycle behavior explicitly. |
| Second | Namespace badge | `projects.namespace` | Hidden when value is `development` |
| Third | Icon + project name | `projects.project_type`, `projects.display_name` | Name links to `/project/{id}`; nowrap |
| Last | Settings cog | — | Links to `/project/{id}` |

### Middle Columns

| Column Key | Header | Source | Renders |
|------------|--------|--------|---------|
| `Tags` | Tags | `projects.tags` | Colored tag pills |
| `Port` | Port | `projects.port` | Port number; clickable inline edit |
| `Stack` | Stack | `projects.stack` | Monospace string |
| `Actions` | Actions | `operations` (category != maintenance) | Operation buttons per UI-GENERAL |
| `Links` | Links | `projects.extra.links` | Link buttons; fallback to server link if port set |
| `Claude` | CLAUDE.md | `projects.has_claude` | Opens AGENTS.md content in modal |
| `Help` | Help | `projects.has_docs` + `extra.doc_path` | Green Documentation button → proxy route → new tab; `has_docs` is true when any of `doc/index.htm`, `doc/index.html`, `docs/index.htm`, `docs/index.html` exists (glob: `doc*/index.htm*`) |
| `Maintenance` | Maintenance | `operations` (category = maintenance) | Operation buttons |
| `LastUpdate` | Updated | `projects.version` | Date portion only; strips `.N` suffix |
| `Configuration` | Configuration | `projects.port`, `card_show`, `tags` | Inline-editable fields per SCREEN-PROJECTS-CONFIGURATION |
| `Workflows` | Workflows | `workflow_types` (is_active = 1) + `projects.has_specs` | One button per active workflow type; disabled with "No specifications" tooltip when `has_specs = false` |

## Open Questions

- Should column selection be persisted per-user (localStorage) or always from URL params?
