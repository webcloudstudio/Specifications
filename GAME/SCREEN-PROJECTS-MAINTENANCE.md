# Screen: Maintenance

| Field | Value |
|-------|-------|
| Version | 20260326 V1 |
| Route | `GET /project-maintenance` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Projects |
| Sub Menu | Maintenance |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance · 5: Setup |

Project list showing maintenance-category operations for each project. Renders SCREEN-DEFAULT with `columns=Maintenance`.

## Maintenance Column

Shows all operations with `category = maintenance` for each project row. Uses the standard operation button pattern from UI-GENERAL: idle → running (green pulse) → done/error flash.

Maintenance operations are typically long-running or infrequently-triggered scripts (cleanup, backup, rebuild, batch jobs). Separating them from the main Dashboard keeps the primary action surface uncluttered.

If a project has no maintenance-category operations, the cell is empty.

## Open Questions

- Should rows with no maintenance operations be hidden by default, with a toggle to show all?
