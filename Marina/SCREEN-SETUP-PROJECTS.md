# Screen: Setup — Projects

| Field | Value |
|-------|-------|
| Version | 20260602 V3 |
| Route | `GET /setup/projects` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Lists all projects discovered in PROJECTS_DIR. Shows CLAUDE_RULES conformance status and cloud catalog sync state. Supports conforming individual projects and publishing them to the Marina DynamoDB catalog. |
| Depends On | UI-GENERAL.md |
| Provides | GET /setup/projects |

## Unconfigured State

If `PROJECTS_DIR` is not set or path does not exist:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠  Projects directory not configured                        │
│                                                              │
│  Set PROJECTS_DIR in .env to point to your projects folder,  │
│  then restart Marina.                                        │
│                                                              │
│  [→ Go to Summary]                                           │
└──────────────────────────────────────────────────────────────┘
```

If `marina_org` is not set, the project list renders normally but the `Publish` button on each row is disabled with tooltip: `Set Marina Org on the Summary tab to enable cloud publish.`

## Layout

Full-width. Namespace selector at top, then action bar, then project table.

```
┌────────────────────────────────────────────────────────────────┐
│  Namespace:  [All ●]  [development]  [tools]  [experiments]    │
│  ──────────────────────────────────────────────────────────── │
│  [🔍 Search projects...]                      [↻ Rescan]       │
│  ──────────────────────────────────────────────────────────── │
│  ┌──────────┬───────────┬───────────────────────┬────────────┐ │
│  │ Status   │ Name      │ Description            │ Actions    │ │
│  ├──────────┼───────────┼───────────────────────┼────────────┤ │
│  │ ✅ Conf  │ my-app    │ My web application     │ [✓][Pub ✅]│ │
│  │ ACTIVE   │           │                        │            │ │
│  ├──────────┼───────────┼───────────────────────┼────────────┤ │
│  │ ⚠ Needs  │ old-tool  │ A legacy script runner │ [Conform]  │ │
│  │ PROTOTYPE│           │                        │ [Publish]  │ │
│  ├──────────┼───────────┼───────────────────────┼────────────┤ │
│  │ ❓ Unkn  │ scratch   │ (no METADATA.md)       │ [Conform]  │ │
│  │ UNKNOWN  │           │                        │            │ │
│  └──────────┴───────────┴───────────────────────┴────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Namespace Selector

Toggle pills above the action bar. Derived from distinct `namespace` values in `PROJECTS_DIR`. `All` is the default. State encoded in `?namespace=` URL param (bookmarkable). Hidden when only one namespace exists.

## Action Bar

| Control | Behavior |
|---------|----------|
| Search input (left) | Client-side filter on project name and description. |
| `↻ Rescan` (right) | `POST /api/scan`; refreshes project list via HTMX. |

## Project Table

One row per project in `PROJECTS_DIR`. Sorted by name within namespace.

| Column | Source | Notes |
|--------|--------|-------|
| Status | Two-line cell: conformance badge (top) + lifecycle status badge (bottom) | See Status Column |
| Name | `projects.display_name` | Links to the project directory path. Plain text if UNKNOWN. |
| Namespace | `projects.namespace` | Shown only when `All` namespace is selected. |
| Description | `projects.short_description` | Truncated at 80 chars. Empty for UNKNOWN. |
| Actions | Conform button + Publish button | See buttons below |

### Status Column

**Top badge — Marina Standards:**

| Badge | Meaning |
|-------|---------|
| `✅ Conformed` (teal) | Project meets Marina standards — Prototyper scripts report clean. |
| `⚠ Needs Update` (amber) | Has `METADATA.md` but Prototyper reports standards gaps. |
| `❓ Unknown` (muted) | No `METADATA.md` — cannot assess conformance. |

**Bottom badge — Lifecycle status:**

Standard status pill from `projects.status` (ACTIVE, PROTOTYPE, ARCHIVED, UNKNOWN). Styled per UI-GENERAL status badge colors.

**Catalog status indicator** (inline, right of bottom badge):

| State | Display |
|-------|---------|
| Published | `☁ Published` (teal, small) |
| Never published | `☁ —` (muted) |
| Stale (local `METADATA.md` newer than last publish) | `☁ Stale` (amber) |

### Conform Button

Brings a project up to Marina standards by invoking the Prototyper as an external process. Marina calls `bin/ProjectUpdate.sh {project_path}` (or `bin/ProjectInitialize.sh {project_path}` for UNKNOWN projects) and reports the exit status. The internal logic — what the Prototyper does to the project — is owned by the Prototyper, not by Marina.

| State | Appearance |
|-------|-----------|
| Needs conforming | `Conform` (outline secondary) |
| Already conformed | `✓ Conformed` (muted, disabled) |
| In progress | Spinner + `Updating…` (disabled) |
| Success | `✓ Done` (teal, 2 s) → status updates to `✅ Conformed` without reload |
| Error | `Failed` (red), inline error below the row |

### Publish Button

Publishes the project's `METADATA.md` and capabilities to the Marina DynamoDB catalog. Calls `POST /api/projects/{id}/publish` which invokes `marina.catalog.publish()`.

| State | Appearance |
|-------|-----------|
| Never published | `Publish` (outline primary) |
| Published and current | `☁ Published` (teal, disabled) |
| Stale (`METADATA.md` changed since last publish) | `Re-publish` (outline amber) |
| marina_org not set | Disabled, tooltip: `Set Marina Org on the Summary tab` |
| MARINA_API_URL not set | Disabled, tooltip: `Deploy Marina API first — see AWS tab` |
| In progress | Spinner + `Publishing…` (disabled) |
| Success | `☁ Published` (teal, 2 s) → cloud sync indicator updates |
| Error | `Failed` (red), inline error below the row |

Publish is independent of Conform — a project can be published whether or not it is conformed. However, conforming first is recommended so `AGENTS.md` is accurate before it reaches the catalog.

## Metrics Bar

Above the table: aggregate counts across all visible projects.

| Metric | Content |
|--------|---------|
| Total | Count of projects in `PROJECTS_DIR` |
| Conformed | Projects meeting Marina standards |
| Needs Update | Projects with `⚠ Needs Update` |
| Published | Projects with `☁ Published` catalog status |

## Empty State

If no projects found:
> *No projects found in `{PROJECTS_DIR}`. Download or clone a project on the Repositories tab.*

If namespace filter yields no results:
> *No projects in the `{namespace}` namespace.*

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/setup/projects` | — | Full page |
| POST | `/api/scan` | — | Updated table HTML fragment |
| POST | `/api/projects/{id}/conform` | — | Updated row fragment (status + button states) |
| POST | `/api/projects/{id}/publish` | — | Updated row fragment (cloud sync indicator + Publish button state) |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (all columns) | Project files: `AGENTS.md`, templates, `METADATA.md` (Conform) |
| `PROJECTS_DIR` (env) | `projects` table (after Rescan or Conform) |
| `settings.marina_org`, `MARINA_API_URL` (env) | DynamoDB catalog (Publish — via marina library) |

## Open Questions

- Should `Conform All` and `Publish All` bulk actions be added? V1: one at a time.
- Should the Publish action also push heartbeat/event items, or metadata only? V1: metadata + capabilities only. Heartbeats are pushed by the local agent separately.
- Should a project that fails DynamoDB publish show the specific AWS error (e.g., missing permissions, wrong region)? Yes — surface the error message inline below the row.
