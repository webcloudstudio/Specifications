# Database: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | SQLite state schema for the Console. |

## Tables

### `document_state`

Single table for all Console state: questionnaire answers, review decisions, kanban overrides.

| Column | Type | Notes |
|--------|------|-------|
| `key` | TEXT PRIMARY KEY | Namespaced state key, e.g. `questionnaire.console_process` |
| `document_id` | TEXT NOT NULL | ID of the document or questionnaire |
| `state` | TEXT NOT NULL | Lifecycle state: `incomplete`, `answered`, `approved`, etc. |
| `payload_json` | TEXT NOT NULL | JSON-serialized answer or decision payload |
| `updated_at` | TEXT NOT NULL | ISO 8601 UTC timestamp |

## State Key Conventions

| Pattern | Example |
|---------|---------|
| `questionnaire.{id}` | `questionnaire.console_process` |
| `review.{doc_id}.{item_id}` | `review.idea_classification.50001` |
| `kanban.{phase_slug}` | `kanban.phase-3` |

## Lifecycle States

Valid `state` values:

| State | Meaning |
|-------|---------|
| `incomplete` | Not yet answered or reviewed |
| `answered` | Form submitted; not yet reviewed |
| `awaiting_review` | Queued for approval |
| `approved` | Decision made: accept |
| `revised` | Sent back for rework |
| `rejected` | Decision made: discard |
| `parked` | Deferred without timeline |
| `deferred` | Explicitly deferred with intent to revisit |

## Open Questions

-
