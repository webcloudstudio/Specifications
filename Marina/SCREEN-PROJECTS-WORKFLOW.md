# Screen: Projects — Workflow

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Route | `GET /projects/workflow` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Workflow |
| Tab Order | 1: Dashboard · 2: Workflow · 3: Configuration · 4: Validation · 5: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Move project work through the workflow configured for each project. |
| Description | Project-scoped workflow board for organizing work, conformance tasks, and operational follow-up. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-ORGANIZATION.md |
| Provides | GET /projects/workflow |

## Header KPIs

Open, In Progress, and Done ticket counts for the selected project/namespace/tag filters.

## Layout

Filter bar followed by a kanban board. The board shows the selected project's workflow. When no project
is selected, it shows the aggregate board for all visible projects and includes the Project column on cards.

## Filters

| Filter | Values |
|--------|--------|
| Project | All visible projects or one project |
| Namespace | All or one configured namespace |
| Tags | Zero or more configured tags |
| Type | All, task, feature, maintenance, conformance, incident |
| Priority | All, low, medium, high, critical |

## Board

The default workflow states are `idea`, `ready`, `in_progress`, `blocked`, `review`, and `done`.
Projects may define a smaller or extended state sequence on Configuration. Marina must reject transitions
not allowed by the active project workflow.

## Ticket Card

| Field | Source |
|-------|--------|
| Title | `workflow_tickets.title` |
| Project | project display name |
| Type | ticket type |
| Priority | ticket priority |
| State | workflow state |
| Tags | ticket tags |
| Age | `created_at` |
| Last activity | `updated_at` |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Add ticket | Button click | Open inline form; create ticket in the configured initial state |
| Move ticket | Drag or state action | Validate transition, persist state, emit event, refresh card |
| Edit ticket | Card click | Open detail drawer; save title, body, type, priority, and tags |
| Run linked operation | Ticket action | Start the allow-listed project operation and link the run to the ticket |
| Configure workflow | Button click | Open project Configuration workflow section |

## Open Questions

- None.
