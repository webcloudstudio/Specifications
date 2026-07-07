# Screen: Workflow — Board

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /workflow`, `GET /workflow/board` |
| Parent | — |
| Main Menu | WORKFLOW |
| Sub Menu | Board · default |
| Tab Order | 1: Board · 2: Add Ticket · 3: Manage |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Track project work from idea through done. |
| Description | Kanban board of project workflow tickets grouped by state. |
| Depends On | UI-GENERAL.md, FEATURE-WORKFLOW-SERVICE.md |
| Provides | GET /workflow, GET /workflow/board |

## Header KPIs

Left column uses three `mn-hdr-count` blocks: Open, In Progress, Done.

## Navigation

Top tabs: SETUP · PROJECTS · WORKFLOW · MONITORING. WORKFLOW sub-tabs: Board, Add Ticket, Manage.

## Board

| Column | State |
|--------|-------|
| Idea | `idea` |
| Proposed | `proposed` |
| Ready | `ready` |
| In Development | `in_development` |
| Testing | `testing` |
| Done | `done` |

## Filters

| Filter | Values |
|--------|--------|
| Project | All projects or one project |
| Type | All / PATCH / SCREEN / FEATURE / AC |
| Priority | All / Low / Medium / High / Critical |

## Ticket Card

| Field | Source |
|-------|--------|
| Title | ticket title |
| Type | workflow type |
| Project | project display name |
| Priority | priority |
| Age | created_at |
| File | target filename if any |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Move ticket | Drag card | POST /api/workflow/tickets/{id}/transition |
| Edit ticket | Card click | Opens detail drawer |
| Save edit | Blur / Save | POST /api/workflow/tickets/{id} |

## Open Questions
- None.
