# Feature: Workflow Service

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Generic workflow ticket service for project work, screen work, feature work, patches, and acceptance criteria. |
| Depends On  | DATABASE.md, FEATURE-SCANNER.md |
| Provides    | GET /api/workflow/tickets, POST /api/workflow/tickets, PATCH /api/workflow/tickets/{id}, POST /api/workflow/tickets/{id}/transition |

**Description:** Stores and transitions project work tickets through Marina's board, add-ticket, and
workflow-management screens.

## Trigger

- Workflow Board load.
- Add Ticket form submit.
- Ticket drag/drop transition.
- Manage screen changes to workflow types and labels.

## Sequence

1. Load active projects and workflow types.
2. Create tickets in `idea`.
3. Enforce configured state transitions.
4. Persist edits to title, body, priority, tags, type, and state.
5. Emit event rows for create, edit, and transition actions.

## States

`idea -> proposed -> ready -> in_development -> testing -> done`

Back paths: `testing -> ready`, `in_development -> proposed`.

## Reads

- Projects registry.
- Workflow tickets.
- Workflow types.
- Labels.

## Writes

- Workflow tickets.
- Workflow types.
- Labels.
- Marina events.

## Open Questions
- None.
