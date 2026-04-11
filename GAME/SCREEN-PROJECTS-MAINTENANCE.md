# Screen: Maintenance

**Version:** 20260326 V1
**Extends:** SCREEN-DEFAULT
**Description:** Specification for the Maintenance screen — project list showing maintenance-category operations for each project

## Menu Navigation

Main Menu: Projects
Sub Menu: Maintenance
Inherits From: SCREEN-DEFAULT

## Route

```
GET /project-maintenance
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Maintenance`.

## Maintenance Column

Shows all operations with `category = maintenance` for each project row. Uses the standard operation button pattern from UI-GENERAL: idle → running (green pulse) → done/error flash.

Maintenance operations are typically long-running or infrequently-triggered scripts (cleanup, backup, rebuild, batch jobs). Separating them from the main Dashboard keeps the primary action surface uncluttered.

If a project has no maintenance-category operations, the cell is empty.

## Open Questions

- Should rows with no maintenance operations be hidden by default, with a toggle to show all?
