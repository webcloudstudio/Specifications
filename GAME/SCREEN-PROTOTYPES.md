# Screen: Prototypes

**Version:** 20260324 V2
**Description:** Top-level screen listing all known prototypes (specification directories inside the Specifications repo) with their names and current status.

## Menu Navigation

`Prototypes / Prototypes` — default sub-tab when Prototypes is first selected.

## Route

```
GET /prototypes              → redirects to /prototypes/list
GET /prototypes/list
```

## Layout

Full-width single-panel list. Action bar at top (New Prototype button + filter/search), prototype rows below.

```
┌────────────────────────────────────────────────┐
│  [+ New Prototype]      [search] [status pills]│
│  ──────────────────────────────────────────── │
│  PROTOTYPE  MyApp       short description      │
│  IDEA       NewThing    short description      │
│  ACTIVE     CoreService short description      │
│  ...                                           │
└────────────────────────────────────────────────┘
```

## Prototype List

One row per prototype specification directory found in the Specifications repo. Sorted by name (default). Each row:

| Element | Content | Source |
|---------|---------|--------|
| Status badge | Colored pill (see UI-GENERAL status colors) | `METADATA.md → status` |
| Name | `display_name` | `METADATA.md → display_name` |
| Short description | One-line summary | `METADATA.md → short_description` |
| Specification link | `View Specification →` | Links to `/prototypes/{name}` (detail — future) |

Clicking a row (or the link) navigates to the prototype detail view (not yet implemented — placeholder route).

## New Prototype Button

Prominent primary button at the left of the action bar: `+ New Prototype`. Large enough to be the clear primary action on the screen.

Clicking opens the **New Prototype Modal**.

### New Prototype Modal

Bootstrap modal. Title: `New Prototype`.

| Field | Type | Validation |
|-------|------|------------|
| Short name | Text input | Required. Lowercase letters, digits, hyphens only (`[a-z0-9-]+`). Max 40 chars. |

Helper text below the input: *This becomes the directory name under Specifications/ (e.g. `my-app` → `Specifications/my-app/`).*

Buttons:
- `Create` (primary) — disabled until input passes validation. Submits the form.
- `Cancel` — closes modal, clears input.

### Create Sequence

1. User clicks `Create`.
2. Modal shows spinner; `Create` button disabled.
3. Client posts `POST /api/prototypes/create` with `{ "name": "<short-name>" }`.
4. Server runs `bash {SPECIFICATIONS_PATH}/bin/setup.sh <short-name>` in `SPECIFICATIONS_PATH`.
5. On success (exit 0): modal closes, list reloads (`GET /api/prototypes`), new row highlighted briefly.
6. On error (non-zero exit or stderr): modal stays open, error message shown below the input in red (include stderr output truncated to 3 lines).

### Validation rules (client-side, before submit)

| Rule | Error message |
|------|---------------|
| Empty | *Name is required.* |
| Invalid chars | *Only lowercase letters, digits, and hyphens allowed.* |
| Already exists | *A prototype named `{name}` already exists.* (checked against current list) |

## Filter Bar

Lives above the list. Client-side filtering (no round-trip).

| Filter | Behavior |
|--------|----------|
| Text search input | Filters rows by name + description match |
| Status pill buttons | Toggle visibility by status (IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED) |

Default state: all statuses shown.

## Empty State

If no prototypes are found (Specifications repo path not configured or empty):

> *Prototypes go here.*
> Configure `SPECIFICATIONS_PATH` in `.env` to point to your Specifications directory.

Shown centered, muted text, inside the list area.

## Data Flow

| Reads | Writes |
|-------|--------|
| `GET /api/prototypes` — list of prototype dirs with parsed METADATA.md fields | `POST /api/prototypes/create` — scaffold new prototype via `setup.sh` |

`GET /api/prototypes`: Server scans `SPECIFICATIONS_PATH` (from `.env`) for subdirectories containing `METADATA.md`, parses `name`, `display_name`, `short_description`, `status` fields, returns as JSON array.

`POST /api/prototypes/create`: Accepts `{ "name": "<short-name>" }`. Validates name format server-side. Runs `bash {SPECIFICATIONS_PATH}/bin/setup.sh <name>` as a subprocess. Returns `{ "ok": true }` on success or `{ "ok": false, "error": "<stderr>" }` on failure. Does not return until `setup.sh` completes.

## Open Questions

- Should clicking a row open a detail view (parsed specification files rendered as HTML) or just link to the raw Specifications directory? A future SCREEN-PROTOTYPES-DETAIL.md will define a rendered detail view. Until it exists, clicking a row shows the specification file list as a plain index.
- Should this screen also show prototypes that are missing `METADATA.md` (as "unconfigured")? Yes — show them with a dim "unconfigured" badge so the user can investigate. A missing METADATA.md is a setup issue, not a reason to hide the entry.
- Should status badges on this screen be clickable to cycle status? Read-only here — status changes go through SCREEN-DRILLDOWN-PROJECT or the Dashboard.
- Should `SPECIFICATIONS_PATH` default to a sibling directory? Yes — default to `../Specifications` relative to `PROJECTS_DIR` when `SPECIFICATIONS_PATH` is not explicitly set in `.env`.
