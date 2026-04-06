# Screen: Project Detail

**Version:** 20260320 V1  
**Description:** Specification for the Project Detail screen

**Single-project deep view.** Shows all configuration information for a project grouped by source.  Fields are correctly edittable.  Script headers and other items can be just described (ie. all bin scripts should have a listing for their relevant metadata) .env file variables etc.  ALl metadata for one project should be editable. Lets users edit file based  serves as the metadata editor for the project.

## Menu Navigation

Top bar: `Projects` (active — detail drill-down, not a direct nav item). No project sub-bar on this screen.

This page is navigated to when the gear icon is selected to see details of individual projects.

## Route

```
GET /project/{id}
```

Rest call should return service catalog data for the project enabling completed layouts. 

## Behavior

- Should the metadata editor support adding new custom fields not in the METADATA.md template?
    METADATA.md template needs to be updated in RulesEngine but i think it is possible the template version in the project is out of date.  this is a display program - The UI should render it after the other fields.  Indicate on the UI that the field is newly discovered / out of specification and colorize it - MAKE IT NOTICEABLE SO I CAN UPDATE THE TEMPLATE. 

## Layout

Two-column layout. Left: project info card + metadata editor. Right: operations + recent activity.

## Project Info Card (top-left)

| Field | Source | Editable |
|-------|--------|----------|
| Display name | `projects.display_name` | Yes |
| Status badge | `projects.status` | Yes (click to cycle) |
| Short description | `projects.description` | Yes |
| Stack | `projects.stack` | Yes |
| Port | `projects.port` | Yes |
| Namespace | `projects.namespace` | Yes |
| Tags | `projects.tags` | Yes (inline tag editor) |
| Version | `projects.version` | Display only |
| Health endpoint | `projects.health_endpoint` | Yes |
| Desired state | `projects.desired_state` | Yes (toggle) |

Fields save on blur/tab-out. Writes go to both database and METADATA.md per DATABASE.md rules.

## Metadata Editor (below info card)

Organized by source:

**From METADATA.md** — editable key:value fields, grouped by category (Identity, Technology, Portfolio).

**From Scanner** — read-only detected flags: `has_git`, `has_venv`, `has_node`, `has_claude`, `has_docs`, `has_tests`, `has_specs`. Shown as boolean indicators.

**From bin/ scripts** — read-only operations list with script name, category, schedule, timeout.

## Operations Panel (top-right)

All registered operations for this project. Each shows:

| Element | Content |
|---------|---------|
| Button | Operation name, styled by category per UI-GENERAL |
| Status | Running indicator if active |
| Last run | Timestamp and exit status of most recent run |

## Recent Activity (bottom-right)

Last 20 events for this project from the `events` table. Each row: timestamp, event type, summary.

## Quick Links

| Link | Source | Behavior |
|------|--------|----------|
| Server | `port` | Opens `localhost:{port}` in new tab |
| Documentation | `extra.doc_path` | Opens doc index in new tab |
| CLAUDE.md | `has_claude` | Opens AGENTS.md content in modal |
| Git repo | `extra.links` | Opens repo URL in new tab |
| Specifications | `has_specs` | Opens specification directory index in new tab |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Edit field | Tab out / blur | Saves to DB + METADATA.md |
| Run operation | Click button | Launches script |
| View log | Click last-run link | Navigates to log in SCREEN-PROCESSES |
| Back to list | Back button or nav | Returns to Dashboard |

## Open Questions