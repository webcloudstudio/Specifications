# Feature: Workflow Service

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Project-scoped workflow ticket service for work, conformance, maintenance, and incidents. |
| Depends On  | DATABASE.md, FEATURE-SCANNER.md |
| Provides    | GET /api/workflow/tickets, POST /api/workflow/tickets, PATCH /api/workflow/tickets/{id}, POST /api/workflow/tickets/{id}/transition |

**Description:** Stores and transitions tickets through the Projects → Workflow board. Tickets belong to
a project or are explicitly platform-level; workflow is not a separate product area.

## Trigger

- Projects → Workflow board load.
- Add-ticket action.
- Ticket drag/drop transition.
- Projects → Configuration changes to workflow types and labels.

## Sequence

1. Load visible projects and each project's effective workflow configuration.
2. Create tickets in `idea`.
3. Enforce project-specific transitions, falling back to the global default.
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
