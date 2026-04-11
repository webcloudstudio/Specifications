# Screen: Configuration

**Version:** 20260320 V1
**Extends:** SCREEN-DEFAULT
**Description:** Specification for the Configuration screen

A screen for editing project metadata across projects in a view

## Menu Navigation

Main Menu: Projects
Sub Menu: Configuration
Inherits From: SCREEN-DEFAULT

## Route

```
GET /project-config
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Configuration`.

## Configuration Column

Editable fields per project row:

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Port | `port:` | `projects.port` | number |
| Show on homepage | `show:` | `projects.card_show` | checkbox |
| Stack | `stack:` | `projects.stack` | text |
| Tags | `tags:` | `projects.tags` | text |

Fields persist on change per DATABASE.md rules. Each field saves independently — no Save button.

## Single-Project Editor

Clicking the cog icon navigates to SCREEN-PROJECT for full metadata editing organized by source.

## Open Questions

- Should the batch Configuration column include additional fields (namespace, desired_state)? The Configuration screen shows the most-commonly-edited fields. Full metadata editing (including namespace and desired_state) is available via SCREEN-DRILLDOWN-PROJECT when the cog is clicked. The batch column stays minimal.
