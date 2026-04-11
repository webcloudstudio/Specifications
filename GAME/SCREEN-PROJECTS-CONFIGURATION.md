# Screen: Configuration

| Field | Value |
|-------|-------|
| Version | 20260320 V1 |
| Route | `GET /project-config` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Projects |
| Sub Menu | Configuration |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance · 5: Setup |

Batch metadata editor. Edit project fields (port, stack, tags, visibility) across all projects in a single view. Renders SCREEN-DEFAULT with `columns=Configuration`.

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

- Should the batch Configuration column include additional fields (namespace, desired_state)? The Configuration screen shows the most-commonly-edited fields. Full metadata editing (including namespace and desired_state) is available via SCREEN-PROJECTS-DETAIL when the cog is clicked. The batch column stays minimal.
