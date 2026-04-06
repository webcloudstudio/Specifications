# Screen: Workflow

**Version:** 20260320 V1  
**Description:** Specification for the Workflow screen

**Kanban board for prototype lifecycle management.** Tracks features and prototypes from idea through implementation to completion. Sources from `spec_tickets` — the same table used by the Projects / Workflow screen, so tickets created there appear here immediately.

## Menu Navigation

`Dashboards / Workflow`

## Route

```
GET /workflow
```

## Layout

Kanban columns (one per state) spanning the viewport. Filter bar at top: filter by project, tag, priority. New Ticket button.

## States

Kanban columns map to `spec_tickets.kanban_state`:

| State | Meaning |
|-------|---------|
| `idea` | First capture, not reviewed |
| `proposed` | Has summary and plan |
| `ready` | Has acceptance criteria, scheduled for work |
| `in_development` | AI session running or recently finished |
| `testing` | Work complete, human validating |
| `done` | Accepted |

States are fixed. New tickets enter at `idea` regardless of how they were created.

## Ticket Card

Each card shows:

| Field | Content | Source |
|-------|---------|--------|
| Title | Ticket title, clickable to open detail | `spec_tickets.title` |
| Type badge | Workflow type pill (PATCH / SCREEN / FEATURE / AC) | `workflow_types.name` via `spec_tickets.workflow_type_id`; omitted if NULL |
| Project | Project badge (colored by project) | `projects.display_name` |
| Priority | Low / Medium / High / Critical indicator | `spec_tickets.priority` |
| Tags | Ticket-level tag pills | `spec_tickets.tags` |
| File | Filename pill when a specification file has been written | `spec_tickets.filename`; amber if `file_status = pending`, green if `applied` |
| Age | Time since creation or last transition | `spec_tickets.created_at` |

## Ticket Detail (modal or slide-out)

| Section | Content |
|---------|---------|
| Title + description | Editable text |
| State | Current state with transition buttons |
| Acceptance criteria | Required at READY state |
| AI Transaction Log | What was decided, what was built, why (populated during IN DEVELOPMENT) |
| Test notes | Human validation notes (at TESTING) |
| History | State transition timeline |

## Transitions

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                               ↑                |
                             READY ←────────────┘ (rework)
                           PROPOSED ←──────────── (redesign)
```

Drag ticket between columns or click state buttons. Validation enforced:
- IDEA → PROPOSED requires summary
- PROPOSED → READY requires acceptance criteria
- IN DEVELOPMENT → TESTING requires work completed

## Prototype Lifecycle View

Filter to a single project to see its prototype lifecycle:
- All tickets for that project across all states
- Progress bar showing tickets by state
- Links to specification files if `has_specs = true`

## AI Integration

Tickets in READY state can be submitted to an AI agent for automated implementation. The agent:
1. Reads ticket description + acceptance criteria
2. Implements changes
3. Logs decisions to the AI Transaction Log
4. Moves ticket to TESTING when done

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Create ticket | New Ticket button | Opens creation form |
| Move ticket | Drag to column | Validates and transitions state |
| Open detail | Click card | Shows ticket detail |
| Filter | Project/tag/priority controls | Filters visible cards |
| Submit to AI | Button on READY tickets | Queues for automated implementation |

## Data Flow

| Reads | Writes |
|-------|--------|
| `spec_tickets` (kanban_state, all columns) | `spec_tickets.kanban_state` (drag / transition) |
| `workflow_types` (type badge labels) | `spec_tickets.priority`, `tags`, `body` (detail edits) |
| `projects` (display_name, has_specs) | `ai_decisions` table (during IN DEVELOPMENT) |
| | `events` table (`ticket_transition`) |

## Open Questions

- Should DONE tickets auto-archive after a configurable period?
- How should the AI agent integration be triggered — queue, webhook, or manual?
