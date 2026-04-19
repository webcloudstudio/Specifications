# Screen: Workflow — Add Ticket

| Field | Value |
|-------|-------|
| Version | 20260407 V2 |
| Route | `GET /workflow/add` |
| Parent | — |
| Main Menu | Workflow |
| Sub Menu | Add Ticket |
| Tab Order | 1: Workflow · 2: Add Ticket · 3: Manage |
| Description | Simple form to create a new ticket. New tickets always enter the board at state `idea`. |
| Depends On  | UI-GENERAL.md |

## Fields

| Field | Key | Type | Required | Default |
|-------|-----|------|----------|---------|
| Title | `title` | Text input | Yes | `Ticket NNN` — auto-incremented from highest existing + 1, zero-padded to 3 digits. User may override. |
| Project | `project_id` | Dropdown (all projects) | Yes | — |
| Description | `body` | Textarea | No | — |
| Tags | `tags` | Tag pill input | No | — |
| Type | `workflow_type_id` | Dropdown (`workflow_types`) | No | FEATURE |
| Priority | `priority` | Radio buttons | No | Medium |

## Buttons

| Button | Behavior |
|--------|----------|
| `Save Ticket` (primary) | POST `/api/tickets`; flash "Ticket created"; clear form; redirect to Workflow board with new card highlighted |
| `Clear` (outline) | Reset all fields to defaults. No writes. |

## Validation

| Rule | Error |
|------|-------|
| Title empty | "Title is required." |
| No project selected | "Select a project." |
| Title > 120 chars | "Title must be 120 characters or fewer." |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` (dropdown) | `spec_tickets` (INSERT) |
| `workflow_types` (type dropdown) | `events` (`ticket_created`) |

## Open Questions

- Should the form stay on Add Ticket after saving, or auto-navigate to the Workflow board?
