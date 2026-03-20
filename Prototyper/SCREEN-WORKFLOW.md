# Screen: Workflow

**Version:** 20260320 V1
**Description:** Spec for the Workflow screen

**Kanban board for prototype lifecycle management.** Tracks features and prototypes from idea through implementation to completion.

## Route

```
GET /workflow
```

## Layout

Kanban columns (one per state) spanning the viewport. Filter bar at top: filter by project, tag, priority. New Ticket button.

## States

| State | Meaning |
|-------|---------|
| IDEA | First capture, not reviewed |
| PROPOSED | Has summary and plan |
| READY | Has acceptance criteria, scheduled for work |
| IN DEVELOPMENT | AI session running or recently finished |
| TESTING | Work complete, human validating |
| DONE | Accepted |

States are configurable via `workflow.json`. New states can be added.

## Ticket Card

Each card shows:

| Field | Content |
|-------|---------|
| Title | Ticket title, clickable to open detail |
| Project | Project badge (colored by project) |
| Priority | Low / Medium / High / Critical indicator |
| Tags | Ticket-level tag pills |
| Age | Time since creation or last transition |

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
| `tickets` table | Ticket state transitions |
| `workflow.json` (state definitions) | AI transaction log entries |
| Project spec files | `events` table (ticket_transition) |

## Open Questions

- Should DONE tickets auto-archive after a configurable period?
- How should the AI agent integration be triggered — queue, webhook, or manual?
