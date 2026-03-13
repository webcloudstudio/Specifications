# Workflow States [ROADMAP]

**Feature ticket lifecycle.** Structured states from idea to done with AI audit trail.

---

## States

| State | Meaning |
|-------|---------|
| IDEA | First capture, not reviewed |
| PROPOSED | Has summary and plan |
| READY | Has acceptance criteria, scheduled for AI work |
| IN DEVELOPMENT | AI session running or recently finished |
| TESTING | AI work complete, human validating |
| DONE | Accepted and complete |

## Transitions

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                                ↑              |
                             READY ←───────────┘  (rework)
                           PROPOSED ←─────────────  (redesign)
```

## Capabilities

- Create feature tickets per project
- Move tickets through states
- Attach notes, images, audio
- All-projects Kanban view
- AI Transaction Log per ticket (acceptance criteria, features built, intent)

## Screens

**Tickets List (Project Detail):** Grouped by state. New Ticket button.

**Ticket Detail:** Title, description, attachments, feature plan, acceptance criteria, AI transaction log, test notes, state history.

**Kanban (separate page):** Columns per state. Cards show project + title. Filter by project or tag.

## Persistence

- Tickets in platform database
- Transaction log optionally committed to project git repo
