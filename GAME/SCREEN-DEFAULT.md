# Screen: Baseline Layout

**Version:** 20260320 V1
**Type:** abstract — base layout, not a routed screen
**Description:** Reusable project list layout. Named views extend this by declaring `Extends: SCREEN-DEFAULT` and specifying their middle columns.

**Inherited by:** SCREEN-DASHBOARD, SCREEN-CONFIGURATION

A sortable, filterable, configurable project list. Middle columns are passed as arguments, making this a reusable base for named views.

## Route

```
GET /default?title=DEFAULT&columns=Links,Actions,Help&filter=normal&sort=name
```

| Param | Default | Purpose |
|-------|---------|---------|
| `title` | DEFAULT | Section header and nav label |
| `columns` | Links,Actions,Help | Comma-separated middle column keys |
| `filter` | normal | Filter state: `normal` / `all` / `idea` / `archive` |
| `sort` | name | `name`, `status_asc`, `status_desc` |

## Layout

Full viewport width — no max-width cap. Sortable table. Column header click sorts; current direction shown with arrows.

## Filter Button

Single cycling button in the section header:

```
normal → all → idea → archive → normal
```

| State | Shows |
|-------|-------|
| `normal` | All except IDEA and ARCHIVED |
| `all` | All projects |
| `idea` | Status = IDEA only |
| `archive` | Status = ARCHIVED only |

State is a URL query param; clicking generates a link with the next state.

## Table Structure

### Fixed Columns (every row)

| Position | Content | Source | Interaction |
|----------|---------|--------|-------------|
| First | Status badge | `projects.status` | Click → cycle IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED; writes DB + METADATA.md |
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
| `Help` | Help | `projects.has_docs` + `extra.doc_path` | Green Documentation button → proxy route → new tab |
| `Maintenance` | Maintenance | `operations` (category = maintenance) | Operation buttons |
| `LastUpdate` | Updated | `projects.version` | Date portion only; strips `.N` suffix |
| `Configuration` | Configuration | `projects.port`, `card_show`, `tags` | Inline-editable fields per SCREEN-CONFIGURATION |

## Open Questions

- Should column selection be persisted per-user (localStorage) or always from URL params?
