# Screen: Workflow — Add Ticket

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /workflow/add` |
| Parent | — |
| Main Menu | WORKFLOW |
| Sub Menu | Add Ticket |
| Tab Order | 1: Board · 2: Add Ticket · 3: Manage |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Create a workflow ticket and place it on the board. |
| Description | Form for creating a new workflow ticket in the `idea` state. |
| Depends On | UI-GENERAL.md, FEATURE-WORKFLOW-SERVICE.md |
| Provides | GET /workflow/add |

## Header KPIs

None. Left KPI column is empty.

## Layout

Single-column, max-width 800px, centered. One `mn-card`: New Ticket.

## Fields

| Field | Key | Type | Required | Default |
|-------|-----|------|----------|---------|
| Title | `title` | Text | Yes | `Ticket NNN` |
| Project | `project_id` | Select | Yes | — |
| Type | `workflow_type_id` | Select | Yes | FEATURE |
| Priority | `priority` | Segmented control | No | Medium |
| Tags | `tags` | Tag input | No | — |
| Description | `body` | Textarea | No | — |

## Buttons

| Button | Result |
|--------|--------|
| Save Ticket | POST /api/workflow/tickets, redirect to board with new card highlighted |
| Clear | Reset form |

## Validation

| Rule | Error |
|------|-------|
| Title empty | Title is required. |
| Project empty | Select a project. |
| Title > 120 chars | Title must be 120 characters or fewer. |

## Open Questions
- None.
