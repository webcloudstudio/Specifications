# Screen: Setup — Projects

| Field | Value |
|-------|-------|
| Version | 20260602 V6 |
| Header Background | `mn-hdr-bg--git` |
| Route | `GET /setup/projects` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Sortable dashboard of GitHub-enabled project directories. One row per project showing name, conform status from METADATA.md, lifecycle status, and actions. Namespace filter at top. Rescan reads METADATA.md and git status from disk. |
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
1. It contains a `.git/` folder, AND
2. `git remote get-url origin` returns a URL containing `github.com`

Directories without a `.git` folder, or with a non-GitHub remote, are silently excluded. The Rescan result always reflects the current disk state.

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
│    my-app        ✅ Conformed    ACTIVE       dev        [Publish ✅] │
│    old-tool      ⚠ Needs Update PROTOTYPE    tools      [Conform]   │
│    scratch       ❓ Unknown      —            —          [Conform]   │
└─────────────────────────────────────────────────────────────────────┘
```

## Namespace Filter

Toggle pills immediately above the action bar. Derived from distinct `namespace` values in `PROJECTS_DIR` METADATA.md files. `All` is the default and always present. State encoded in `?namespace=` URL param. Hidden when only one namespace exists.

## Action Bar

| Control | Behaviour |
|---------|-----------|
| Search input (left) | Client-side filter on project name. Instant — no server call. |
| `↻ Rescan` (right) | `POST /api/scan` — re-reads METADATA.md and git status for every qualifying directory. Returns updated table fragment via HTMX. |

## Project Table

One row per qualifying project. Default sort: Name ascending. Each column header is clickable to sort; active sort column shows ▲ / ▼.

| Column | Content | Sortable |
|--------|---------|---------|
| Name | `display_name` from METADATA.md; falls back to directory name | Yes |
| Conform Status | Single badge — see Conform Status below | Yes |
| Status | Lifecycle status pill from `status:` in METADATA.md | Yes |
| Namespace | `namespace:` from METADATA.md; `—` if absent | Yes |
| Actions | Conform button + Publish button | No |

**One row = one line.** No secondary lines, no expanded detail rows. All information fits inline. Row height matches standard Bootstrap table rows.

## Conform Status

Single badge derived from Prototyper validation output. Stored in `projects.conform_status` after each Rescan.

| Badge | CSS | Meaning |
|-------|-----|---------|
| `✅ Conformed` | `mn-badge--ok` (teal) | `bin/ProjectValidate.sh` exits 0 |
| `⚠ Needs Update` | `mn-badge--warn` (amber) | `bin/ProjectValidate.sh` exits non-0 |
| `❓ Unknown` | `mn-badge--muted` | No `METADATA.md` in directory |

Rescan re-runs `bin/ProjectValidate.sh` for each project and updates this badge. The badge does not persist between Marina restarts — Rescan is always required on first load.

## Lifecycle Status

Status pill from `status:` in METADATA.md. Valid values and colours per UI-GENERAL status badge specification: `ACTIVE`, `PROTOTYPE`, `ARCHIVED`, `IDEA`, `PRODUCTION`. `—` if no METADATA.md.

## Actions Column

Two buttons per row, rendered compactly inline.

### Conform Button

| State | Appearance |
|-------|-----------|
| Needs conforming / Unknown | `[Conform]` (outline secondary, small) |
| Already conformed | `[✓]` (muted icon-only, disabled) |
| In progress | spinner only (disabled) |
| Error | `[!]` (red, tooltip shows error) |

On click: `POST /api/projects/{id}/conform`. Marina invokes `bin/ProjectInitialize.sh {project_path}` (Unknown) or `bin/ProjectUpdate.sh {project_path}` (Needs Update). Returns updated row fragment. No page reload.

### Publish Button

| State | Appearance |
|-------|-----------|
| Never published | `[Publish]` (outline primary, small) |
| Published and current | `[☁ ✅]` (teal icon-only, disabled) |
| Stale | `[Re-pub]` (outline amber, small) |
| marina_org not set | Disabled, tooltip: `Set Marina Org on the AWS tab` |
| MARINA_API_URL not set | Disabled, tooltip: `Deploy Terraform first` |
| In progress | spinner only (disabled) |
| Error | `[!]` (red, tooltip shows error) |

On click: `POST /api/projects/{id}/publish`. Returns updated row fragment.

## Rescan Behaviour

`POST /api/scan` does the following for every directory under `PROJECTS_DIR`:
1. Check for `.git/` and a `github.com` remote — exclude if absent
2. Read `METADATA.md` fields: `display_name`, `status`, `namespace`, `name`
3. Run `bin/ProjectValidate.sh {path}` — set `conform_status` from exit code
4. Read `git status --short` — stored in `projects.git_status` (not displayed in V1)
5. Upsert `projects` table row

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
| POST | `/api/projects/{id}/conform` | — | Updated row fragment |
| POST | `/api/projects/{id}/publish` | — | Updated row fragment |

## Data Flow

| Reads | Writes |
|-------|--------|
| `PROJECTS_DIR` filesystem (directory listing) | `projects` table (Rescan) |
| `METADATA.md` per project | None (Conform writes to project files, not Marina DB) |
| `git remote get-url origin` per directory | None |
| `bin/ProjectValidate.sh` exit code | None |
| `settings.marina_org`, `MARINA_API_URL` | DynamoDB catalog (Publish) |

## Open Questions

- Should `Conform All` and `Publish All` bulk actions be added? V1: one at a time only.
- Should git status (clean/dirty/ahead/behind) be shown in the table in V2? V1: read during Rescan but not displayed.
- Should the table persist sort state in the URL (`?sort=name&dir=asc`)? V1: client-side sort only, no URL persistence.
