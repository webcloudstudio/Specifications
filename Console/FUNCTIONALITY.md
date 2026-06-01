# Functionality: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Feature index for the Console application. |

## Features

### Agile Plan Gate (`FEATURE-AgilePlan.md`)

Reads `AGILE_PLAN.md` as the live state database. Parses spikes, stories, and ACs with their inline state. Derives a Kanban board from object states. Shows per-object evidence from the `evidence/` directory. Writes approve/revise/reject decisions back into `AGILE_PLAN.md` atomically — this is the gate that `oneshot2.sh` polls. Supports PO defect entry (adds AC to a ticket and sends it back to `revise`).

### Configuration Loading (`FEATURE-Config.md`)

Loads `Console/console.json` at startup. Exposes the full configuration at `GET /api/config` and the tab list at `GET /api/tabs`. Validates that the config is well-formed JSON; raises a startup error if not.

### Document Rendering (`FEATURE-Documents.md`)

Renders configured documents on demand via `GET /api/document/{tab_id}/{doc_id}`. Supports four document types: `markdown` (rendered HTML), `link` (hyperlink to local file or URL), `questionnaire` (rendered HTML form), and `roadmap` (markdown + Kanban board). Missing files return HTTP 404.

### Kanban Board (`FEATURE-Kanban.md`)

Derives Kanban cards from configured roadmap documents. Parses Markdown headings matching a configured prefix into cards. Assigns each card to a column from the `kanban.columns` list. Exposes the model at `GET /api/kanban`.

### Questionnaire State (`FEATURE-Questionnaires.md`)

Renders JSON questionnaire files as HTML forms. Persists form submissions to SQLite via `POST /api/state/{key}`. Exposes questionnaire index with completion state at `GET /api/questionnaires`. Never writes back to the questionnaire source file.

### State Persistence (`FEATURE-State.md`)

Generic key-value state store backed by SQLite. Used by questionnaires and review actions. `GET /api/state/{key}` returns current state (defaulting to `incomplete` if absent). `POST /api/state/{key}` upserts the record.

### Review Actions (`FEATURE-Review.md`)

Exposes review actions and state vocabulary from config at `GET /api/review`. Review decisions (approve, revise, reject, park, defer) are stored as state writes — they do not modify source documents.

## Open Questions

-
