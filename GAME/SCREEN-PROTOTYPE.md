# Screen: Prototypes

**Version:** 20260324 V1
**Description:** Top-level screen listing all known prototypes (spec directories inside the Specifications repo) with their names and current status.

## Menu Navigation

Top-level tab in the navigation bar: `Prototypes`. Added to the right of the existing tabs.

## Route

```
GET /prototypes
```

## Layout

Full-width single-panel list. Filter bar at top, prototype rows below.

```
┌────────────────────────────────────────────────┐
│  Prototypes                    [filter/search] │
│  ──────────────────────────────────────────── │
│  PROTOTYPE  MyApp       short description      │
│  IDEA       NewThing    short description      │
│  ACTIVE     CoreService short description      │
│  ...                                           │
└────────────────────────────────────────────────┘
```

## Prototype List

One row per prototype spec directory found in the Specifications repo. Sorted by name (default). Each row:

| Element | Content | Source |
|---------|---------|--------|
| Status badge | Colored pill (see UI-GENERAL status colors) | `METADATA.md → status` |
| Name | `display_name` | `METADATA.md → display_name` |
| Short description | One-line summary | `METADATA.md → short_description` |
| Spec link | `View Spec →` | Links to `/prototypes/{name}` (detail — future) |

Clicking a row (or the link) navigates to the prototype detail view (not yet implemented — placeholder route).

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
| `GET /api/prototypes` — list of prototype dirs with parsed METADATA.md fields | None |

Server scans `SPECIFICATIONS_PATH` (from `.env`) for subdirectories containing `METADATA.md`, parses `name`, `display_name`, `short_description`, `status` fields, returns as JSON array.

## Open Questions

- Should clicking a row open a detail view (parsed spec files rendered as HTML) or just link to the raw Specifications directory?
- Should this screen also show prototypes that are missing `METADATA.md` (as "unconfigured")?
- Should status badges on this screen be clickable to cycle status (like Dashboard) or read-only?
- Should `SPECIFICATIONS_PATH` default to a sibling directory (`../Specifications`) when not set?
