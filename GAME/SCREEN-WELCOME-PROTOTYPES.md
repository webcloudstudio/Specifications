# Screen: Welcome — Prototypes

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /welcome/prototypes` |
| Parent | — |
| Main Menu | Welcome |
| Sub Menu | Prototypes |
| Tab Order | 1: Summary · 2: Prototypes · 3: Projects |
| Description | Read-only searchable list of all known prototypes. No actions — navigation only. |

## Layout

Full-width. Single search input above a list. Client-side filter, no round-trip.

## List

One row per prototype from `GET /api/prototypes`. Sorted by name.

| Column | Source |
|--------|--------|
| Status badge | `METADATA.md → status` |
| Name | `METADATA.md → display_name` |
| Namespace | `METADATA.md → namespace` — omit if empty |
| Short description | `METADATA.md → short_description` — truncate at 80 chars |

Search input filters on any visible field (name, status, namespace, description). Case-insensitive substring.

## Empty State

> *No prototypes found. Configure `SPECIFICATIONS_PATH` in `.env`.*

## Data Flow

| Reads | Writes |
|-------|--------|
| `GET /api/prototypes` | None |

## Open Questions

- None.
