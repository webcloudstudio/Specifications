# Screen: Workflow [ROADMAP]

**Version:** 20260320 V1  
**Description:** Spec for the Workflow screen

Kanban board for project tickets.

## Route

```
GET /workflow
```

## Layout

Kanban columns matching ticket states. Cards are draggable between columns.

## Columns (States)

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
```

Rework path: TESTING → READY. Redesign path: IN DEVELOPMENT → PROPOSED.

## Card Content

| Field | Display |
|-------|---------|
| Title | Card heading |
| Project | Badge showing which project |
| Tags | Tag pills |
| Priority | Color indicator (Low/Medium/High/Critical) |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Create ticket | Click New Ticket | Modal with title, description, project, tags, priority |
| Move ticket | Drag to new column | Validate transition, update state |
| Edit ticket | Click card | Detail view with full description |

## Open Questions

- Per-project filter on the board?
- AI transaction log entries when ticket enters IN DEVELOPMENT?
- Archive done tickets after N days?
