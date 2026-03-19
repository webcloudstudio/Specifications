# Screen: Default

**Configurable project list.** A reusable project table where the middle columns are passed as arguments. Used to create named views with different column sets.

---

## Route

```
GET /default
```

### Query Parameters

| Param | Default | Purpose |
|-------|---------|---------|
| `title` | DEFAULT | Page title shown in the section header and nav |
| `columns` | Links,Actions,Help | Comma-separated list of middle columns to display |
| `filter` | normal | Active filter state (normal / all / idea / archive) |
| `sort` | name | Sort order: `name`, `status_asc`, `status_desc` |

Example: `/default?title=DEFAULT&columns=Links,Actions,Help`

---

## Data Access Rules

**All data is read from the SQLite database. No file I/O occurs during a page render.**

- Page renders call `db.get_all_projects()` and `db.get_all_operations_keyed()` — two queries total.
- The database is populated at startup and refreshed on demand via the Refresh button.
- The Refresh button (`/api/sync`) is the only path that reads the filesystem.

---

## Layout Rules

- Main content area is **100% width** — no max-width cap, no centering margin.
- The table expands to fill available viewport width.

---

## Nav Bar

The nav bar shows:
- Standard nav links (same as all other screens)
- Section header below: custom `title` + a cycling filter button

### Filter Button

A single button that cycles through filter states on click. Current state is shown as the button label. Clicking advances to the next state:

```
normal --> all --> idea --> archive --> normal (cycles)
```

| State | Shows |
|-------|-------|
| `normal` | All projects except IDEA and ARCHIVED |
| `all` | All projects |
| `idea` | Only status = IDEA |
| `archive` | Only status = ARCHIVED |

The filter state is passed as a URL query param (`?filter=normal`). Clicking the button links to the same page with the next filter state.

---

## Table Structure

Sortable table. Clicking a column header sorts by that column. Current sort direction indicated with ↑↓.

### Header Row

| Fixed: Status | Fixed: (blank) | Fixed: Project | ...middle columns... | Fixed: (blank) |

Columns without a header title render an empty `<th>`.

### Per-Project Row

#### No-Wrap Rules

**These cells must never wrap** — wrapping breaks the visual layout of the row:

| Cell | Rule |
|------|------|
| Status badge | `white-space: nowrap` |
| Icon + project name | `white-space: nowrap`; the icon (💻 or 📖) and name are in the same cell and must stay on one line |

Other columns (Links, Actions, Tags, etc.) may wrap freely.

#### Fixed Columns (always present)

| Position | Element | Source (DB column) | Interaction |
|----------|---------|---------------------|-------------|
| First | Status badge | `projects.status` | Click → rotate IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED via HTMX; writes to DB + METADATA.md |
| Second | Namespace badge | `projects.namespace` | Display only; hidden if value is `development` |
| Third | Icon + project name | `projects.project_type`, `projects.display_name` | Name links to `/project/{id}`; must not wrap |
| Last | Settings cog ⚙️ | — | Links to `/project/{id}` |

#### Middle Columns (configurable)

Middle columns appear in the order they are listed in the `columns` argument.

| Column Key | Header Title | DB Source | Renders |
|------------|-------------|-----------|---------|
| `Tags` | Tags | `projects.tags` | Colored tag pills |
| `Port` | Port | `projects.port` | Port number; clickable to edit inline |
| `Stack` | Stack | `projects.stack` | Monospace stack string |
| `Actions` | Actions | `operations` where `category != 'maintenance'` | Operation buttons; click launches script |
| `Links` | Links | `projects.extra.links` | Link buttons with ↗; falls back to Server link if port set |
| `Claude` | CLAUDE.md | `projects.has_claude` | CLAUDE.md button → opens modal with AGENTS.md content |
| `Help` | Help | `projects.has_docs` + `projects.extra.doc_path` | Green "Documentation" button → opens docs in new tab |
| `Maintenance` | Maintenance | `operations` where `category = 'maintenance'` | Operation buttons; click launches script |
| `LastUpdate` | Updated | `projects.version` | Date portion of version field (strips `.N` build suffix) |

**Notes on column behavior:**
- `Actions` shows all operations where category is NOT `maintenance`
- `Maintenance` shows only operations where category IS `maintenance`
- `Help`: displays only when `has_docs = true`. Renders as a green "Documentation" button (white text, `op-btn--success` style). URL is `/project/{id}/doc/index.html` — served through Flask's `/project/<id>/doc/<path>` route, which proxies files from the project's `doc/` or `docs/` directory. Opens in a new tab. Note: `file://` URLs cannot be used — browsers block navigation to `file://` from `http://` pages (cross-origin policy).
- `LastUpdate`: uses `version` field, strips `.N` suffix (e.g., `2026-03-13.4` → `2026-03-13`)

---

## Startup Behavior

Operations are registered from `bin/` scripts containing within the first 20 lines:
- `# CommandCenter Operation` — marks the script as an operation
- `# Category: <name>` — used to route to Actions vs Maintenance column (optional; defaults to `local`)

Documentation presence (`has_docs`) is detected during scan by the equivalent of:

```sh
ls */doc*/index.htm*
```

Any immediate subdirectory whose name starts with `doc` (`doc/`, `docs/`, `documentation/`, etc.) that contains `index.html` or `index.htm`. The first match wins. The relative path (e.g. `docs/index.html`) is stored as `doc_path` in the project's `extra` JSON.

---

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (all fields) | Status click → `projects.status` (DB) + METADATA.md (file) |
| `operations` table (all projects, one query) | Operation button → `op_runs` table |
| `projects.extra` JSON (links, doc_path) | |

No file I/O on page render. All data pre-loaded into DB at startup or Refresh.

---

## Resolved Design Decisions

- **Help URL**: `file://` URLs are correct. GAME is a local-machine console; it does not serve remote projects. No proxy needed.
- **Namespace column**: Rendered as a badge inline in the name cell (compact). A separate sortable column can be added later if needed.
- **LastUpdate source**: Uses `version` field from METADATA.md (stored as `projects.version`). Git commit date not yet implemented; would require a `git_last_commit_date` column added in a future schema pass.
