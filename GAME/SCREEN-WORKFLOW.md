# Screen: Workflow

**Version:** 20260407 V2
**Description:** Ticket-based workflow tracking for project and prototype work. Sub-tabbed screen.

## Menu Navigation

Main Menu: Workflow
Sub Menu: Kanban (Default)

## Routes

```
GET /workflow              → redirects to /workflow/kanban
GET /workflow/kanban       Kanban board. Default.
GET /workflow/add          Add Ticket form.
GET /workflow/manage       Workflow type and label management.
```

---

## Sub-Tab: Kanban

Default view. Full-width kanban board of all tickets grouped by state.

### Action Bar

Rendered above the board. Client-side filters.

| Control | Type | Behavior |
|---------|------|----------|
| Project filter | Dropdown | Show tickets for one project or all. Default: all. |
| Type filter | Pill buttons | Filter by workflow type: ALL / PATCH / SCREEN / FEATURE / AC |
| Priority filter | Pill buttons | Filter by priority: ALL / Low / Medium / High / Critical |

### Board

Kanban columns spanning the viewport width. One column per state, fixed order:

| Column | `kanban_state` value | Entry condition |
|--------|---------------------|-----------------|
| Idea | `idea` | All new tickets start here |
| Proposed | `proposed` | Has summary |
| Ready | `ready` | Has acceptance criteria |
| In Development | `in_development` | AI session running or recently assigned |
| Testing | `testing` | Work complete, human validating |
| Done | `done` | Accepted |

Drag a ticket card between columns to transition state. Validation is enforced on drop:

```
IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE
                               ↑                |
                             READY ←────────────┘ (rework)
                           PROPOSED ←──────────── (redesign)
```

### Ticket Card

| Field | Content | Source |
|-------|---------|--------|
| Title | Ticket title — click to open detail | `spec_tickets.title` |
| Type badge | PATCH / SCREEN / FEATURE / AC pill | `workflow_types.name` |
| Project | Project badge | `projects.display_name` |
| Priority | Low / Medium / High / Critical indicator | `spec_tickets.priority` |
| Age | Time since creation | `spec_tickets.created_at` |
| File | Filename pill — amber if pending, green if applied | `spec_tickets.filename` |

### Ticket Detail (slide-out panel)

Opens when a card is clicked. Editable in-place.

| Section | Content |
|---------|---------|
| Title | Editable text |
| Description | Editable markdown body |
| State | Current state; transition buttons for valid next states |
| Acceptance criteria | Required before moving to READY |
| Tags | Editable tag pills |
| AI Transaction Log | Populated during IN DEVELOPMENT; read-only |
| History | State transition timeline |

### Data Flow — Kanban

| Reads | Writes |
|-------|--------|
| `spec_tickets` | `spec_tickets.kanban_state` (drag / transition) |
| `workflow_types` | `spec_tickets` body, priority, tags (detail edits) |
| `projects` | `events` table (`ticket_transition`) |

---

## Sub-Tab: Add Ticket

Simple form to create a new ticket. Navigates here from the sub-bar.

### Layout

```
┌───────────────────────────────────────────────────────┐
│  Add Ticket                                           │
│  ─────────────────────────────────────────────────── │
│                                                       │
│  Title *                                              │
│  [ Ticket 001                                      ]  │
│                                                       │
│  Project *                                            │
│  [ Select project ▼                                ]  │
│                                                       │
│  Description                                          │
│  [ Multi-line text area                            ]  │
│  [                                                 ]  │
│                                                       │
│  Tags                                                 │
│  [ tag pills / text input                          ]  │
│                                                       │
│  Type                                                 │
│  [ FEATURE ▼  ]                                       │
│                                                       │
│  Priority                                             │
│  ( ) Low  (●) Medium  ( ) High  ( ) Critical          │
│                                                       │
│  [Save Ticket]   [Clear]                              │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Fields

| Field | Key | Type | Required | Default |
|-------|-----|------|----------|---------|
| Title | `title` | Text input | Yes | `Ticket NNN` — auto-incremented from the highest existing ticket number + 1, zero-padded to 3 digits (e.g. `Ticket 001`, `Ticket 002`). User may override. |
| Project | `project_id` | Dropdown (all projects) | Yes | — |
| Description | `body` | Textarea | No | — |
| Tags | `tags` | Tag pill input | No | — |
| Type | `workflow_type_id` | Dropdown (from `workflow_types`) | No | FEATURE |
| Priority | `priority` | Radio buttons | No | Medium |

### Buttons

| Button | Behavior |
|--------|----------|
| `Save Ticket` (primary) | POST `/api/tickets`; on success: flash "Ticket created", clear form, redirect to Kanban with new card highlighted. |
| `Clear` (outline) | Resets all fields to defaults. No writes. |

### Validation

| Rule | Error |
|------|-------|
| Title empty | "Title is required." — shown inline below the field. |
| No project selected | "Select a project." |
| Title > 120 chars | "Title must be 120 characters or fewer." |

New tickets always enter the board at state `idea`.

### Data Flow — Add Ticket

| Reads | Writes |
|-------|--------|
| `projects` (dropdown population) | `spec_tickets` (INSERT) |
| `workflow_types` (type dropdown) | `events` table (`ticket_created`) |

---

## Sub-Tab: Manage

Metadata management for workflow configuration. Two sections: Workflow Types, Labels.

### Workflow Types

CRUD table for `workflow_types`. Each type maps to a ticket file prefix and a kanban label.

| Column | Content | Editable |
|--------|---------|----------|
| Name | Type name (e.g., FEATURE, PATCH) | Yes (inline) |
| File prefix | Specification file prefix (e.g., `FEATURE-NNN-`) | Yes (inline) |
| Color | Pill color hex | Yes (color picker) |
| Active | Toggle on/off | Yes |

Add button: `+ Add Type` — appends a new blank row. Delete: trash icon per row (confirm before delete; blocked if tickets of that type exist).

### Labels / Tags

Manage tag values used on tickets. Simple list: tag name + color. Same inline-edit pattern as workflow types.

### Data Flow — Manage

| Reads | Writes |
|-------|--------|
| `workflow_types` | `workflow_types` (INSERT / UPDATE / DELETE) |
| `ticket_tags` | `ticket_tags` (INSERT / UPDATE / DELETE) |

---

## Open Questions

- Should the Add Ticket form stay on the Add Ticket sub-tab after saving, or auto-navigate to Kanban?
- Should DONE tickets auto-archive after a configurable period? (configurable in Manage tab if yes)
