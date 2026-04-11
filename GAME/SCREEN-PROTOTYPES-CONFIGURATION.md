# Screen: Prototypes Configuration

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /prototypes/configuration` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Prototypes |
| Sub Menu | Configuration |
| Tab Order | 1: List · 2: Configuration · 3: Validation · 4: Maintenance |
| Description | Batch metadata editor for prototype specification directories. Mirrors Projects / Configuration. |

## Layout

Full-width list. One row per prototype. Editable metadata fields inline. Same row structure as Projects/Configuration but sourced from `SPECIFICATIONS_PATH` directories rather than the projects database.

## Prototype Row

| Element | Content | Editable |
|---------|---------|----------|
| Status badge | `METADATA.md → status` | Yes — click to cycle IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED; writes `METADATA.md` |
| Name | `METADATA.md → display_name` | No (display only — name is the directory) |
| Configuration fields | See below | Yes |

## Configuration Fields (per row)

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Display name | `display_name:` | `METADATA.md → display_name` | Text input |
| Short description | `description:` | `METADATA.md → short_description` | Text input |
| Namespace | `namespace:` | `METADATA.md → namespace` | Text input |
| Status | `status:` | `METADATA.md → status` | Dropdown (IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED) |

Fields save on blur/tab-out. Writes go directly to the prototype's `METADATA.md` file on disk via the server.

## Action Bar

| Control | Behavior |
|---------|----------|
| Text filter | Client-side filter by name or description |
| Status pills | Show/hide rows by status; default shows all |

## Data Flow

| Reads | Writes |
|-------|--------|
| `SPECIFICATIONS_PATH` directory scan | `METADATA.md` files (field updates) |
| `METADATA.md` per prototype (all fields) | `events` table (`prototype_metadata_updated`) |

## Open Questions

- Should status changes here also update the scanner's in-memory state, or only the file? File write is authoritative; scanner re-reads on next rescan.
