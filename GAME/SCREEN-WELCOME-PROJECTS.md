# Screen: Welcome — Projects

| Field | Value |
|-------|-------|
| Version | 20260510 V2 |
| Route | `GET /welcome/projects` |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: GitHub · 3: Projects |
| Description | Lists all projects discovered in PROJECTS_DIR. Shows conformance status from the startup scan. Supports filtering by namespace and conforming individual projects to the latest template. |
| Depends On  | UI-GENERAL.md, FEATURE-SCANNER.md |

## Unconfigured State

If `PROJECTS_DIR` is not set or the path does not exist, the page shows a full-panel notice instead of the project list:

```
┌──────────────────────────────────────────────────────────┐
│  ⚠  Projects directory not configured                     │
│                                                           │
│  Set PROJECTS_DIR in .env to point to your projects       │
│  folder, then restart the application.                    │
│                                                           │
│  [→ Go to Summary]                                        │
└──────────────────────────────────────────────────────────┘
```

If `SPECIFICATIONS_PATH` is not set, the page renders the project list normally but the `Conform` button on each row is disabled with a tooltip: `Set SPECIFICATIONS_PATH in .env to enable conforming`.

## Layout

Full-width. Namespace selector at top, then action bar, then project table.

```
┌────────────────────────────────────────────────────────────────┐
│  Namespace:  [All ●]  [development]  [tools]  [experiments]    │
│  ──────────────────────────────────────────────────────────── │
│  [🔍 Search projects...]                      [↻ Rescan]       │
│  ──────────────────────────────────────────────────────────── │
│  ┌──────────┬───────────┬───────────────────────┬──────────┐  │
│  │ Status   │ Name      │ Description            │ Conform  │  │
│  ├──────────┼───────────┼───────────────────────┼──────────┤  │
│  │ ✅ Conf  │ my-app    │ My web application     │ [✓ Done] │  │
│  │ ACTIVE   │           │                        │          │  │
│  ├──────────┼───────────┼───────────────────────┼──────────┤  │
│  │ ⚠ Needs  │ old-tool  │ A legacy script runner │ [Conform]│  │
│  │ PROTOTYPE│           │                        │          │  │
│  ├──────────┼───────────┼───────────────────────┼──────────┤  │
│  │ ❓ Unkn  │ scratch   │ (no METADATA.md)       │ [Conform]│  │
│  │ UNKNOWN  │           │                        │          │  │
│  └──────────┴───────────┴───────────────────────┴──────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Namespace Selector

A row of toggle pills immediately above the action bar. Values are derived from the distinct `namespace` values across all projects in `PROJECTS_DIR`.

| Pill | Behavior |
|------|----------|
| `All` (default selected) | Shows all projects regardless of namespace |
| `{namespace}` (one per distinct value) | Filters the table to projects with that namespace only |

Selection is client-side (no round-trip). State is encoded in a `?namespace=` URL param so the filtered view is bookmarkable. When only one namespace exists, the namespace selector is hidden.

The `development` namespace is shown in the selector without special treatment — it is not hidden here (unlike the Dashboard where it is suppressed).

## Action Bar

| Control | Behavior |
|---------|----------|
| Search input (left) | Client-side filter on project name and description. Placeholder: `Search projects…`. |
| `↻ Rescan` button (right) | `POST /api/scan`; refreshes the project list in place via HTMX. |

## Project Table

One row per project found in `PROJECTS_DIR` by the startup scan. Sorted by name within each namespace group. If namespace filter is `All`, rows are sorted alphabetically without grouping.

| Column | Source | Notes |
|--------|--------|-------|
| Status | Two-line cell: conformance badge (top), lifecycle status badge (bottom) | See Status Column below |
| Name | `projects.display_name` | Links to `/project/{id}` if the project is registered (has `METADATA.md`). Plain text if UNKNOWN. |
| Namespace | `projects.namespace` | Shown only when `All` namespace is selected. Hidden when a specific namespace is filtered. |
| Description | `projects.short_description` | Truncated at 80 chars. Empty for UNKNOWN projects (no METADATA.md). |
| Conform | Conform button | See Conform Button below. |

### Status Column

The status cell shows two stacked badges:

**Top badge — Conformance:**

| Badge | Meaning |
|-------|---------|
| `✅ Conformed` (green) | Project has been conformed to the current template. `AGENTS.md` and template files are up to date. |
| `⚠ Needs Update` (amber) | Project exists and has `METADATA.md` but is missing template files or has an outdated `AGENTS.md`. |
| `❓ Unknown` (muted) | Directory found on disk but has no `METADATA.md`. Cannot assess conformance. |

Conformance is determined by the startup scan. It is updated after a successful Conform operation or Rescan.

**Bottom badge — Lifecycle status:**

Standard status pill from `projects.status` (ACTIVE, PROTOTYPE, ARCHIVED, UNKNOWN, etc.). Styled per UI-GENERAL status badge rules.

### Conform Button

Runs the conform operation for a single project — equivalent to `bin/project_manager.py update` for that project.

**What it does:**
1. Injects the latest `CLAUDE_RULES.md` into the project's `AGENTS.md`
2. Copies missing template files (`common.sh`, `common.py`, `index.html`)
3. Adds missing `METADATA.md` default fields
4. Triggers `POST /api/scan` to refresh the project record

**Button states:**

| State | Appearance |
|-------|-----------|
| Idle — needs conforming | `Conform` (outline secondary) |
| Idle — already conformed | `✓ Conformed` (muted, disabled) |
| Disabled — SPECIFICATIONS_PATH missing | `Conform` (disabled, tooltip: `Set SPECIFICATIONS_PATH in .env to enable`) |
| In progress | Spinner + `Updating…` (disabled) |
| Success | `✓ Done` (green, 2 s), then row status updates to `✅ Conformed` without page reload |
| Error | `Failed` (red), inline error message below the row |

Only one Conform operation runs at a time per row. Running multiple rows simultaneously is allowed.

## Empty State

If no projects are found in `PROJECTS_DIR`:

> *No projects found in `{PROJECTS_DIR}`. Clone or create a project to get started.*

If the namespace filter yields no results:

> *No projects in the `{namespace}` namespace.*

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (all columns) | Project files: `AGENTS.md`, template files, `METADATA.md` (Conform) |
| `PROJECTS_DIR` (env) | `projects` table (after `POST /api/scan` on Conform success) |
| `SPECIFICATIONS_PATH` (env) | None |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/welcome/projects` | — | Full page |
| POST | `/api/scan` | — | Updated project table HTML fragment (HTMX) |
| POST | `/api/project/{id}/conform` | — | Updated row HTML fragment (status + button state) |

## Open Questions

- Should UNKNOWN projects (no METADATA.md) also show a `Make a Project` button to initialise them with a minimal METADATA.md? V1: show Conform only — the conform step will add default METADATA.md fields.
- Should there be a `Conform All` bulk action? V1: one at a time.
