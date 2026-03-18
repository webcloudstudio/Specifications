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

Example: `/default?title=DEFAULT&columns=Links,Actions,Help`

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

#### Fixed Columns (always present)

| Position | Element | Source | Interaction |
|----------|---------|--------|-------------|
| First | Status badge | `status` from METADATA.md | Click → rotate through IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED, persist immediately via HTMX |
| Second | Namespace badge | `namespace` from METADATA.md | Display only; hidden if value is `development` (default) |
| Third | Project name | `display_name` from METADATA.md | Click → `/project/{id}` |
| Last | Settings cog ⚙️ | — | Click → `/project/{id}` |

#### Middle Columns (configurable)

Middle columns appear in the order they are listed in the `columns` argument.

| Column Key | Header Title | Source | Renders |
|------------|-------------|--------|---------|
| `Tags` | Tags | `tags` from METADATA.md | Colored tag pills |
| `Port` | Port | `port` from METADATA.md | Port number; clickable to edit inline |
| `Stack` | Stack | `stack` from METADATA.md | Monospace stack string |
| `Actions` | Actions | `bin/` scripts where Category != maintenance | Operation buttons (one per script); click launches script |
| `Links` | Links | `## Links` table in METADATA.md | Link buttons with ↗; falls back to Server link if port defined |
| `Claude` | CLAUDE.md | `has_claude` flag | CLAUDE.md button → opens modal with AGENTS.md content |
| `Help` | Help | `doc/index.html` presence or Documentation link | 📖 button → opens project documentation page in new tab |
| `Maintenance` | Maintenance | `bin/` scripts where Category = maintenance | Operation buttons; click launches script |
| `LastUpdate` | Updated | `version_date` field (from `version:` in METADATA.md) | Date string; falls back to `updated_at` timestamp |

**Notes on column behavior:**
- `Actions` shows all operations where category is NOT `maintenance`
- `Maintenance` shows only operations where category IS `maintenance`
- `Help` looks for a link labeled "Documentation" in the project's METADATA.md links first; if absent but `has_docs = true`, constructs `file://{project_path}/doc/index.html`
- `Tags`: duplicate entry removed from original spec — appears once
- `LastUpdate`: on scan, GAME reads the last git commit date if `has_git = true`; otherwise falls back to the `version:` date field

---

## Startup Behavior

Operations are registered from `bin/` scripts containing within the first 20 lines:
- `# CommandCenter Operation` — marks the script as an operation
- `# Category: <name>` — used to route to Actions vs Maintenance column (optional; defaults to `local`)

---

## Data Flow

| Reads | Writes |
|-------|--------|
| Projects table (all fields) | Status click → `status` field (immediate HTMX update) |
| Operations table (category filter) | Operation button → `op_runs` table (via operations engine) |
| Extra JSON (links, bookmarks) | |
| `doc/index.html` presence flag | |

---

## Open Questions / Design Decisions

- **Filter button**: Implemented as a cycling link-button (GET request to same URL with next filter state). Does not require JavaScript — each state is a link.
- **Namespace column**: Spec shows namespace as a separate second column. Current implementation renders it as a badge in the name cell for compactness. Second column option is cleaner for sorting purposes — requires decision.
- **LastUpdate source**: Currently uses `version_date` (from METADATA.md `version:` field). Richer option is `git log --format=%ci -1` run on scan and stored in a `git_last_commit_date` DB column (not yet implemented).
- **Help URL**: Local `file://` URLs work for same-machine browser access. For networked GAME access, GAME would need to proxy/serve the project's `doc/` directory.
