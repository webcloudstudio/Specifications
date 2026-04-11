# Screen: Workflow — Kanban Board

| Field | Value |
|-------|-------|
| Version | 20260407 V2 |
| Route | `GET /workflow/kanban`, `GET /workflow` (redirect) |
| Parent | — |
| Main Menu | Workflow |
| Sub Menu | Workflow · default |
| Tab Order | 1: Workflow · 2: Add Ticket · 3: Manage |
| Description | Full-width kanban board of all tickets grouped by state. |

## Action Bar

Client-side filters above the board.

| Control | Type | Behavior |
|---------|------|----------|
| Project filter | Dropdown | Show tickets for one project or all. Default: all. |
| Type filter | Pill buttons | ALL / PATCH / SCREEN / FEATURE / AC |
| Priority filter | Pill buttons | ALL / Low / Medium / High / Critical |

## Board

One column per state, fixed order:

| Column | `kanban_state` |
|--------|----------------|
| Idea | `idea` |
| Proposed | `proposed` |
| Ready | `ready` |
| In Development | `in_development` |
| Testing | `testing` |
| Done | `done` |

Drag a card between columns to transition state. Valid transitions enforced on drop:
`IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE` with back-paths to READY and PROPOSED for rework.

## Ticket Card

| Field | Source |
|-------|--------|
| Title | `spec_tickets.title` — click to open detail panel |
| Type badge | `workflow_types.name` pill |
| Project | `projects.display_name` |
| Priority | Low / Medium / High / Critical |
| Age | Time since `spec_tickets.created_at` |
| File | `spec_tickets.filename` — amber if pending, green if applied |

## Ticket Detail Panel

Slide-out on card click. Editable in-place.

| Section | Content |
|---------|---------|
| Title | Editable text |
| Description | Editable markdown |
| State | Current state + transition buttons for valid next states |
| Acceptance criteria | Required before moving to READY |
| Tags | Editable tag pills |
| AI Transaction Log | Populated during IN DEVELOPMENT; read-only |
| History | State transition timeline |

## Data Flow

| Reads | Writes |
|-------|--------|
| `spec_tickets` | `spec_tickets.kanban_state` (drag / transition) |
| `workflow_types` | `spec_tickets` body, priority, tags (detail edits) |
| `projects` | `events` table (`ticket_transition`) |

## Open Questions

- None.
