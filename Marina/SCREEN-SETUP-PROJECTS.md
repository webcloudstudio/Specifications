# Screen: Setup — Projects

| Field | Value |
|-------|-------|
| Version | 20260603 V8 |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Projects are the Git Repositories downloaded to your projects directory. |
| Route | `GET /setup/projects` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Onboarding handoff view of repositories under `PROJECTS_DIR`; discovery happens here and ongoing organization belongs to PROJECTS. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/projects |

## Header KPIs

Left column of the page header. Component type: two **Count Blocks** (`mn-hdr-count`) separated by a vertical divider.

```html
<div class="mn-hdr-count">
  <span class="mn-hdr-count__number">{conformed}</span>
  <span class="mn-hdr-count__label">Conformed</span>
</div>
<div class="mn-hdr-kpi-divider"></div>
<div class="mn-hdr-count">
  <span class="mn-hdr-count__number">{total}</span>
  <span class="mn-hdr-count__label">Total</span>
</div>
```

Both counts reflect the active namespace filter and update on Rescan.

## What Qualifies as a Project

Only directories that are GitHub-enabled are shown. A directory qualifies if:
1. Its name does **not** start with `.` (hidden directories such as `.git`, `.cache`, `.venv` are always excluded)
2. It contains a `.git/` folder
3. `git remote get-url origin` returns a URL containing `github.com`

All three conditions must be met. Directories failing any condition are silently excluded. The Rescan result always reflects the current disk state.

## Unconfigured State

If `PROJECTS_DIR` is not set or path does not exist:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠  Projects directory not configured                        │
│                                                              │
│  Set PROJECTS_DIR on the Summary tab, then rescan.           │
└──────────────────────────────────────────────────────────────┘
```

## Layout

Full-width. Namespace filter pills at top, then action bar, then sortable project table. One row per project — no wrapping, no sub-rows.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Namespace:  [All ●]  [development]  [production]  [tools]           │
│  ─────────────────────────────────────────────────────────────────  │
│  [🔍 Search...]                                        [↻ Rescan]    │
│  ─────────────────────────────────────────────────────────────────  │
│  ▲ Name          Conform Status  Status      Namespace   Actions     │
│  ─────────────────────────────────────────────────────────────────  │
│    my-app        ✅ Conformed    ACTIVE       dev        [✓]         │
│    old-tool      ⚠ Needs Update PROTOTYPE    tools      [⚙ Conform] │
│    scratch       ❓ Unknown      —            —          [⚙ Conform] │
└─────────────────────────────────────────────────────────────────────┘
```

## Namespace Filter

Toggle pills immediately above the action bar. Derived from distinct `namespace` values in `PROJECTS_DIR` METADATA.md files. `All` is the default and always present. State encoded in `?namespace=` URL param. Hidden when only one namespace exists.

## Action Bar

| Control | Behaviour |
|---------|-----------|
| Search input (left) | Client-side filter on project name. Instant — no server call. |
| `↻ Discover` (right) | `POST /api/projects/scan` — discovers repositories and refreshes the handoff table. |
| `＋ Add to Projects` | Registers a selected repository without changing its files. |

## Project Table

One row per qualifying project. Default sort: Name ascending. Each column header is clickable to sort; active sort column shows ▲ / ▼.

| Column | Content | Sortable |
|--------|---------|---------|
| Name | `display_name` from METADATA.md; falls back to directory name | Yes |
| Conform Status | Single badge — see Conform Status below | Yes |
| Status | Lifecycle status pill from `status:` in METADATA.md | Yes |
| Namespace | `namespace:` from METADATA.md; `—` if absent | Yes |
| Actions | Conform button only | No |

**One row = one line.** No secondary lines, no expanded detail rows. All information fits inline. Row height matches standard Bootstrap table rows.

## Discovery Status

Single badge derived from Marina's configured standards adapter. Discovery does not run validation.

| Badge | CSS | Meaning |
|-------|-----|---------|
| `✅ Managed` | `mn-badge--ok` (teal) | Registered in the Projects registry |
| `⚠ Discovered` | `mn-badge--warn` (amber) | Found on disk but not registered |
| `❓ Identity Conflict` | `mn-badge--muted` | Missing or conflicting repository identity |

Discovery refreshes this badge. Validation and conformance state are owned by Projects → Validation.

## Lifecycle Status

Status pill from `status:` in METADATA.md. Valid values and colours per UI-GENERAL status badge specification: `ACTIVE`, `PROTOTYPE`, `ARCHIVED`, `IDEA`, `PRODUCTION`. `—` if no METADATA.md.

## Actions Column

Single button per row. All buttons are small pill-style (`btn-sm` + `rounded-pill`) with icons. Color is retained at reduced opacity in disabled state — do not swap to grey.

### Registration Action

| State | Appearance |
|-------|-----------|
| Discovered | `＋ Add to Projects` (primary pill, small) |
| Registered | `✓ Managed` (teal pill, disabled) |
| Identity conflict | `! Resolve` (red pill, opens detail) |

On click: `POST /api/projects/{id}/register`. Marina creates the local registry projection and leaves the
repository unchanged. Conformance and remediation are performed from Projects → Validation.

## Rescan Behaviour

`POST /api/scan` does the following for every directory under `PROJECTS_DIR`:
1. Check for `.git/` and a `github.com` remote — exclude if absent
2. Read `METADATA.md` fields: `display_name`, `status`, `namespace`, `name`
3. Read available metadata and service-catalog files; no external tool is required for discovery.
4. Read `git status --short` and remote identity.
5. Upsert the discovered-project handoff row; registration is explicit.

Rescan replaces the full table contents via HTMX fragment. Header KPI counts update in the same response.

## Empty State

If no qualifying projects found after scan:
> *No GitHub-enabled projects found in `{PROJECTS_DIR}`.*

If namespace filter yields no results:
> *No projects in the `{namespace}` namespace.*

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/setup/projects` | — | Full page |
| POST | `/api/scan` | — | Updated table HTML fragment + header KPI fragment |
| POST | `/api/projects/{id}/register` | — | Updated row fragment |

## Data Flow

| Reads | Writes |
|-------|--------|
| `PROJECTS_DIR` filesystem (directory listing) | `projects` table (Rescan) |
| `METADATA.md` per project | None (Conform writes to project files, not Marina DB) |
| `git remote get-url origin` per directory | None |
| Repository identity and standard metadata | None |

## Open Questions

- Should a bulk registration action be added? V1: one at a time only.
- Should git status (clean/dirty/ahead/behind) be shown in the table in V2? V1: read during Rescan but not displayed.
- Should the table persist sort state in the URL (`?sort=name&dir=asc`)? V1: client-side sort only, no URL persistence.
