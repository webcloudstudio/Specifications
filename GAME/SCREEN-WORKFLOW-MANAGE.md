# Screen: Workflow — Manage

| Field | Value |
|-------|-------|
| Version | 20260407 V2 |
| Route | `GET /workflow/manage` |
| Parent | — |
| Main Menu | Workflow |
| Sub Menu | Manage |
| Tab Order | 1: Workflow · 2: Add Ticket · 3: Manage |
| Description | CRUD management for workflow types and ticket tags/labels. |
| Depends On  | UI-GENERAL.md |

## Workflow Types

CRUD table for `workflow_types`.

| Column | Editable |
|--------|----------|
| Name (e.g. FEATURE, PATCH) | Yes — inline |
| File prefix (e.g. `FEATURE-NNN-`) | Yes — inline |
| Color (pill hex) | Yes — color picker |
| Active | Yes — toggle |

`+ Add Type` appends a blank row. Delete: trash icon per row; confirm before delete; blocked if tickets of that type exist.

## Labels / Tags

Manage tag values used on tickets. Tag name + color. Same inline-edit pattern as workflow types.

## Data Flow

| Reads | Writes |
|-------|--------|
| `workflow_types` | `workflow_types` (INSERT / UPDATE / DELETE) |
| `ticket_tags` | `ticket_tags` (INSERT / UPDATE / DELETE) |

## Open Questions

- Should DONE tickets auto-archive after a configurable period? Configurable here if yes.
