# Screen: Project Workflow

**Status: REMOVED** — Ticket creation moved to `Workflow / Add Ticket` (SCREEN-DASHBOARDS-WORKFLOW.md). This screen and its route (`/project-workflow`) are no longer active.

~~**Version:** 20260326 V1~~
~~**Extends:** SCREEN-DEFAULT~~
~~**Description:** Specification for the Project Workflow screen — create specification ticket files for any project from a configurable set of workflow types~~

One-click entry point for raising specification tickets (PATCH-NNN, SCREEN-NNN, FEATURE-NNN, etc.) against any project that has a linked specification directory. Each active `workflow_types` row appears as a button per project row. Clicking opens a modal; submitting writes the file to disk and records it in `spec_tickets`.

## Menu Navigation

(REMOVED — no navigation entry)

## Route

```
GET /project-workflow
```

Renders SCREEN-DEFAULT (Baseline) with `columns=Workflows`.

## Workflows Column

One button per row in `workflow_types` where `is_active = 1`, ordered by `sort_order`.

| State | Appearance |
|-------|------------|
| Project has specifications (`has_specs = true`) | Active buttons, one per workflow type |
| Project has no specifications (`has_specs = false`) | Buttons rendered dim/disabled; tooltip: "No specification directory found" |

Buttons use the workflow type's `name` as label. Style: small outline buttons, consistent width within the column.

## Create Ticket Modal

Opens when any workflow button is clicked.

**Title:** `New {workflow_type.name} — {project.display_name}`

### Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Short description | Text input | Yes | Becomes the filename slug: lowercased, spaces → hyphens, non-alphanumeric stripped. Max 60 chars. Preview of resulting filename shown below input. |
| Body | Textarea | No | Free-form markdown. Pre-filled with `workflow_types.template` where `{title}` is substituted. User edits before submitting. |

### Filename Preview

Live preview below the description input:

```
PATCH-004-fix-nav-scroll.md
```

NNN is calculated server-side on submit (scan for highest existing `{PREFIX}-NNN-*` in the specification directory + 1). Preview shows `NNN` as `???` until submit.

### Buttons

| Button | Behaviour |
|--------|-----------|
| `Create` (primary) | Disabled until description passes validation. Submits the form. |
| `Cancel` | Closes modal, discards input. |

### Validation (client-side)

| Rule | Message |
|------|---------|
| Empty description | *Description is required.* |
| Description too short (< 3 chars) | *Description must be at least 3 characters.* |

### Submit Sequence

1. `POST /api/specification-tickets` with `{ project_id, workflow_type_id, title, body }`
2. Server scans `{SPECIFICATIONS_PATH}/{project.name}/` for existing `{PREFIX}-NNN-*` files → calculates next NNN
3. Renders file content from `workflow_types.template` substituting `{title}` and `{body}`
4. Writes file: `{SPECIFICATIONS_PATH}/{project.name}/{PREFIX}-{NNN}-{slug}.md`
5. Inserts row into `spec_tickets` (status = `pending`)
6. Emits `spec_ticket_created` event
7. Returns `{ ok: true, filename }` — modal closes, brief success toast shown on the row

On error: modal stays open, error shown in red below the Body field.

## Pending Tickets Indicator

In the Workflows column, if a project has any `spec_tickets` rows with `status = pending`, a small amber badge shows the count next to the button group: e.g. `3 pending`. Clicking it links to the specification directory (if `has_specs` and `SPECIFICATIONS_PATH` configured).

## Data Flow

| Reads | Writes |
|-------|--------|
| `workflow_types` (active rows, ordered) | File on disk: `{SPECIFICATIONS_PATH}/{project.name}/{file}` |
| `projects` (has_specs, display_name) | `spec_tickets` table (new row, status = pending) |
| `spec_tickets` (pending count per project) | `events` table (`spec_ticket_created`) |
| Filesystem (NNN calculation on submit) | |

## Workflow Type Configuration

Workflow types are managed via Settings (future: Settings / Workflow Types screen). Until that screen exists, types are edited directly in the `workflow_types` table. Seed data is inserted on first startup if the table is empty — see DATABASE.md.

## Open Questions

- Should the Body textarea render a live markdown preview pane? Yes — split-pane preview is useful given that body content is markdown. Implement as a toggle (Edit / Preview) rather than always-split to keep the modal compact.
- Should submitting a ticket also trigger a git commit in the Specifications repo? Yes — auto-commit with message `Add {PREFIX}-{NNN}-{slug}.md for {project_name}` immediately after the file is written. No-op if the Specifications repo has no `.git/` or git is unavailable.
- Should the pending badge click navigate to the Prototypes screen filtered to that project? Yes — navigate to `/prototypes?filter={project.name}` so the user sees all specification files for that project in context.
