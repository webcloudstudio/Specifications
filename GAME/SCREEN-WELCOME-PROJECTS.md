# Screen: Welcome — Projects

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /welcome/projects` |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: Prototypes · 3: Projects |

Read-only searchable list of all discovered projects. No actions — navigation only. Mirrors Welcome — Prototypes layout applied to projects.

## List

One row per project from `GET /api/projects`. Sorted by name.

| Column | Source |
|--------|--------|
| Status badge | `projects.status` |
| Name | `projects.display_name` |
| Namespace | `projects.namespace` — omit if `development` |
| Short description | `projects.short_description` — truncate at 80 chars |

Search input filters on any visible field. Case-insensitive substring. Client-side, no round-trip.

## Empty State

> *No projects found. Configure `PROJECTS_DIR` in `.env`.*

## Data Flow

| Reads | Writes |
|-------|--------|
| `GET /api/projects` | None |

## Open Questions

- None.
