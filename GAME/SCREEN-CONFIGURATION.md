# Screen: Configuration

**Version:** 20260320 V1
**Extends:** SCREEN-DEFAULT
**Description:** Spec for the Configuration screen

A Baseline screen for editing project metadata across all projects in a single list.

## Menu Navigation

`Projects / Configuration`

## Route

```
GET /project-config
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Configuration`.

## Configuration Column

Three editable fields per project row:

| Field | Label | Source | Input |
|-------|-------|--------|-------|
| Port | `port:` | `projects.port` | number |
| Show on homepage | `show:` | `projects.card_show` | checkbox |
| Tags | `tags:` | `projects.tags` | text |

Fields persist on change per DATABASE.md rules. Each field saves independently — no Save button.

## Single-Project Editor

Clicking the cog icon navigates to SCREEN-PROJECT for full metadata editing organized by source.

## Open Questions

- Should the batch Configuration column include additional fields (namespace, desired_state)?
