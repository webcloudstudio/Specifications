# Feature: Workflow Service


| Field       | Value |
|-------------|-------|
| Version     | 20260419 V1 |

**Version:** 2026-04-06 V1
**Description:** Generic state machine service — one interface for all workflow types, differentiated by workflow-name and workflow-type with payload-driven behavior

## Design Intent

GAME already has a Kanban board (SCREEN-WORKFLOW.md) for specification ticket lifecycle. That board uses a fixed set of states (idea → proposed → ready → in_development → testing → done) tied to `spec_tickets`. The Workflow Service generalizes this into a platform service that any project can use for any kind of state machine — not just specification tickets.

**One interface, many workflows:** A deployment pipeline, a content review process, a bug triage queue, and the existing specification ticket lifecycle are all state machines. They differ in their states, transitions, and payloads — not in their fundamental operations (create, transition, query, list). The Workflow Service provides those operations as a generic interface. The specific workflow behavior comes from **workflow templates** that define states and allowed transitions.

**Workflow-name and workflow-type as arguments:** Every workflow call takes `workflow_name` (which specific instance, e.g., "deploy-myapp-v2.1") and `workflow_type` (which template, e.g., "deployment"). The type determines the allowed states and transitions. The name identifies the specific workflow instance. Payloads carry type-specific data.

**Integration with existing Kanban:** The existing `spec_tickets` system becomes one workflow type ("specification-ticket") managed by this service. The Kanban screen reads from the same data through the workflow service API. No migration needed — the existing states map directly to a workflow template.

**Integration with other services:** The workflow service is a state machine, not a task executor. When a transition fires (e.g., specification ticket moves to "in_development"), the workflow service emits an event. Other services (Batch Runner, AsyncQueue) can subscribe to these events to trigger work. The workflow service does not run scripts — it manages state.

---

## Service Manifest

```yaml
name: workflow
description: Generic state machine for project task and process lifecycle management
version: 1.0.0

transports:
  rest: true
  cli: true
  mcp: true
  async: false

tools:
  - name: create
    description: >
      Create a new workflow instance from a template. Returns a workflow_id
      for all subsequent operations. The workflow starts in the template's
      initial state.
    inputs:
      workflow_name:
        type: string
        required: true
        description: Human-readable name for this workflow instance (e.g. "deploy-myapp-v2.1")
      workflow_type:
        type: string
        required: true
        description: Template identifier (e.g. "deployment", "specification-ticket", "review")
      project:
        type: string
        required: true
        description: Project name slug this workflow belongs to
      payload:
        type: object
        required: false
        description: Type-specific initial data (e.g. ticket body, deployment target, review criteria)
    output:
      workflow_id: { type: integer }
      workflow_name: { type: string }
      workflow_type: { type: string }
      current_state: { type: string }
      created_at: { type: string }

  - name: transition
    description: >
      Move a workflow instance to a new state. Validates that the transition
      is allowed by the template. Records the transition in history with an
      optional comment. Returns the new state.
    inputs:
      workflow_id:
        type: integer
        required: true
      to_state:
        type: string
        required: true
        description: Target state (must be a valid transition from current state)
      comment:
        type: string
        required: false
        description: Reason for the transition (recorded in history)
      payload:
        type: object
        required: false
        description: Additional data to attach to this transition (e.g. test results, review notes)
    output:
      workflow_id: { type: integer }
      previous_state: { type: string }
      current_state: { type: string }
      valid: { type: boolean }
      error: { type: string, nullable: true }

  - name: status
    description: Get the current state and history of a workflow instance
    inputs:
      workflow_id:
        type: integer
        required: true
    output:
      workflow_id: { type: integer }
      workflow_name: { type: string }
      workflow_type: { type: string }
      project: { type: string }
      current_state: { type: string }
      payload: { type: object }
      history:
        type: array
        items:
          from_state: string
          to_state: string
          comment: string
          timestamp: string

  - name: list
    description: List workflow instances, optionally filtered by project, type, or state
    inputs:
      project:
        type: string
        required: false
        description: Filter to workflows for a specific project
      workflow_type:
        type: string
        required: false
        description: Filter to a specific workflow type
      state:
        type: string
        required: false
        description: Filter to workflows currently in a specific state
      limit:
        type: integer
        required: false
        description: Maximum results (default 50)
    output:
      workflows:
        type: array
        items:
          workflow_id: integer
          workflow_name: string
          workflow_type: string
          project: string
          current_state: string
          updated_at: string

  - name: list_types
    description: List available workflow templates with their states and transitions
    inputs: {}
    output:
      types:
        type: array
        items:
          name: string
          display_name: string
          description: string
          states: array
          initial_state: string
```

---

## Workflow Templates

Templates define the state machine for each workflow type. Stored in the `workflow_templates` table, seeded from YAML files, and editable via the Settings screen.

### Built-in Templates

**specification-ticket** (maps to existing spec_tickets Kanban):

```yaml
name: specification-ticket
display_name: Specification Ticket
description: Specification lifecycle from idea through implementation to acceptance
initial_state: idea
states:
  - name: idea
    transitions: [proposed]
  - name: proposed
    transitions: [ready, idea]
    requires: [summary]
  - name: ready
    transitions: [in_development, proposed]
    requires: [acceptance_criteria]
  - name: in_development
    transitions: [testing, proposed]
  - name: testing
    transitions: [done, ready]
  - name: done
    transitions: []
```

**deployment** (example for project deployment tracking):

```yaml
name: deployment
display_name: Deployment Pipeline
description: Track deployments from build through staging to production
initial_state: building
states:
  - name: building
    transitions: [staging, failed]
  - name: staging
    transitions: [production, failed, building]
  - name: production
    transitions: []
  - name: failed
    transitions: [building]
```

**review** (example for content/code review):

```yaml
name: review
display_name: Review Process
description: Submit work for review, iterate on feedback, approve
initial_state: submitted
states:
  - name: submitted
    transitions: [in_review]
  - name: in_review
    transitions: [approved, changes_requested]
  - name: changes_requested
    transitions: [submitted]
  - name: approved
    transitions: []
```

Developers can create custom templates by adding YAML files to `{project}/workflows/` or through the Settings screen.

---

## New Database Tables

### `workflow_templates`

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| name | TEXT UNIQUE | — | Template identifier slug |
| display_name | TEXT | — | Human-readable name |
| description | TEXT | NULL | What this workflow type is for |
| states_json | TEXT | — | JSON array of state definitions (name, transitions, requires) |
| initial_state | TEXT | — | State name for new instances |
| source | TEXT | 'platform' | `platform` / `project:{name}` |
| is_active | INTEGER | 1 | |
| created_at | TEXT | datetime('now') | |
| updated_at | TEXT | datetime('now') | |

### `workflow_instances`

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER PK | auto | Auto-increment |
| workflow_name | TEXT | — | Human-readable instance name |
| template_id | INTEGER FK | — | References workflow_templates.id |
| project_id | INTEGER FK | — | References projects.id |
| current_state | TEXT | — | Current state name |
| payload | TEXT | '{}' | JSON blob of type-specific data |
| created_at | TEXT | datetime('now') | |
| updated_at | TEXT | datetime('now') | |

### `workflow_history`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| workflow_id | INTEGER FK | References workflow_instances.id |
| from_state | TEXT | Previous state |
| to_state | TEXT | New state |
| comment | TEXT | Transition reason |
| transition_payload | TEXT | JSON data attached to this transition |
| timestamp | TEXT | When the transition occurred |

---

## Event Emission

Every transition emits an event to the `events` table:

| event_type | summary | detail |
|------------|---------|--------|
| `workflow_transition` | "{workflow_name}: {from} → {to}" | JSON: workflow_id, template, project, from_state, to_state, comment |

Other services can query events to react to workflow state changes. The Batch Runner could be triggered by a "ready → in_development" transition on a specification-ticket to auto-launch the build.

---

## Migration from spec_tickets

The existing `spec_tickets` table and Kanban screen continue to work. The workflow service provides an additional, generic interface. Migration path:

1. Seed `workflow_templates` with the "specification-ticket" template
2. Create `workflow_instances` rows mirroring existing `spec_tickets` rows
3. Kanban screen reads from `workflow_instances` via the workflow service API
4. `spec_tickets` table becomes a view or is retired

This migration is not required for V1. Both systems can coexist — the workflow service is additive.

---

## New Routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/services/workflow/create` | Create workflow instance |
| POST | `/api/services/workflow/transition` | Transition state |
| GET | `/api/services/workflow/status?workflow_id=N` | Get workflow status + history |
| GET | `/api/services/workflow/list` | List workflows with filters |
| GET | `/api/services/workflow/list_types` | List available templates |
| GET | `/api/workflow/templates` | Template management (Settings integration) |
| POST | `/api/workflow/templates` | Create/update template |

---

## Open Questions

- Should workflow templates support "on_enter" hooks — a script or REST call fired automatically when entering a state? This would enable auto-triggering builds when a ticket enters "in_development" without requiring external event polling. Adds complexity but reduces integration glue.
- Should the "specification-ticket" template migration be automatic (V1) or deferred? Automatic means the Kanban screen switches to the workflow service immediately. Deferred means both systems coexist until the developer explicitly migrates.
- Should workflows support parallel states (e.g., "building" and "testing" simultaneously) or only linear state machines? Linear is simpler and covers all current use cases. Parallel adds power but significant complexity.
