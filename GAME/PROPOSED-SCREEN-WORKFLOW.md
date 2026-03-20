# Screen: Ticketing [ROADMAP]

**Kanban board for feature tickets.** Structured lifecycle from idea to done with AI audit trail.

---

## Layout

Kanban columns (one per state) across all projects. Filter by project or tag.

## States

| State | Meaning |
|-------|---------|
| IDEA | First capture, not reviewed |
| PROPOSED | Has summary and plan |
| READY | Has acceptance criteria, scheduled for work |
| IN DEVELOPMENT | AI session running or recently finished |
| TESTING | Work complete, human validating |
| DONE | Accepted |

STATES should be configurable and easily added

## Features 

Tickets that are READY can be submitted to claude automatically for implemenation
Tickets are merged into the specifcation file when Done

## Transitions

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                                ↑              |
                             READY ←───────────┘  (rework)
                           PROPOSED ←─────────────  (redesign)
```

## Ticket Detail

- Title and description
- Attachments (notes, images, audio)
- Feature plan (at PROPOSED)
- Acceptance criteria (at READY)
- AI Transaction Log (after IN DEVELOPMENT): what was decided, what was built, why
- Test notes (at TESTING)
- State history timeline

## Per-Project Ticket List

Compact list grouped by state within the project detail view. New Ticket button.

## Data Flow

| Reads | Writes |
|-------|--------|
| User input | Ticket state → dashboard |
| Usage analytics (cost for scheduling) | Transaction log → project git repo |
