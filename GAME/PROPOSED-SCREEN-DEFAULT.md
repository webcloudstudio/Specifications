# Screen: Baseline

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

---

## Layout

- Full viewport width — no max-width cap, no centering margin.
- Sortable table. Column header click sorts; current direction shown with ↑↓.

---

## Filter Button

Single cycling button in the section header. Clicking advances to the next state:

```
normal → all → idea → archive → normal
```

| State | Shows |
|-------|-------|
| `normal` | All except IDEA and ARCHIVED |
| `all` | All projects |
| `idea` | Status = IDEA only |
| `archive` | Status = ARCHIVED only |

State is a URL query param; clicking generates a link to the same page with the next state.

---

## Table Structure

### Header Row

| Status | (blank) | Project | ...middle columns... | (blank) |
|--------|---------|---------|---------------------|---------|

Columns with no title render an empty `<th>`.

### Fixed Columns (every row)

| Position | Content | Source | Interaction |
|----------|---------|--------|-------------|
| First | Status badge | `projects.status` | Click → cycle IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED; writes DB + METADATA.md |
| Second | Namespace badge | `projects.namespace` | Hidden when value is `development` |
| Third | Icon + project name | `projects.project_type`, `projects.display_name` | Name links to `/project/{id}`; must not wrap |
| Last | Settings cog ⚙️ | — | Links to `/project/{id}` |

Status badge and icon+name cells: `white-space: nowrap`.

### Middle Columns

| Column Key | Header | Source | Renders |
|------------|--------|--------|---------|
| `Tags` | Tags | `projects.tags` | Colored tag pills |
| `Port` | Port | `projects.port` | Port number; clickable inline edit |
| `Stack` | Stack | `projects.stack` | Monospace string |
| `Actions` | Actions | `operations` (category ≠ maintenance) | Operation buttons |
| `Links` | Links | `projects.extra.links` | Link buttons ↗; fallback to server link if port set |
| `Claude` | CLAUDE.md | `projects.has_claude` | Opens AGENTS.md content in modal |
| `Help` | Help | `projects.has_docs` + `projects.extra.doc_path` | Green Documentation button → Flask proxy route `/project/{id}/doc/<path>` → opens in new tab |
| `Maintenance` | Maintenance | `operations` (category = maintenance) | Operation buttons |
| `LastUpdate` | Updated | `projects.version` | Date portion only; strips `.N` build suffix |
| `Configuration` | Configuration | `projects.port`, `projects.card_show`, `projects.tags` | Inline-editable fields; see SCREEN-CONFIGURATION.md |
