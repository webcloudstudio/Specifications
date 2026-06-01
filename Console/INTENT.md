# Intent: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Goals, constraints, and success criteria for the Console review surface. |

## Goals

- Provide a local browser UI that renders project documents, questionnaires, Kanban cards, and review queues from a `console.json` configuration file.
- Persist questionnaire answers and review decisions in local SQLite without touching source documents.
- Be fully config-driven: no project-specific logic in application code.
- Support any Prototyper project by copying the template and generating a project-specific `console.json`.
- Serve as the standard review surface produced by `oneshot2.sh` for agile-methodology projects.

## Constraints

- Must not write to source Markdown, CSV, or project data files during UI interaction.
- Must not call external model APIs or remote services.
- Must not require authentication for local use.
- Must not embed project-specific logic (story rules, manuscript generation, domain decisions) in `app.py`.
- All project bindings belong in `console.json` — the application is a generic renderer.

## Success Criteria

- Starting `bash Console/start.sh` from the project root launches the Console on the configured port.
- `GET /health` returns `{"status": "ok"}`.
- Every configured document path in `console.json` resolves and renders without error.
- Questionnaire form submissions persist to SQLite and are retrievable via `GET /api/state/{key}`.
- Review state writes (approve, revise, reject, park, defer) persist to SQLite only.
- The Kanban board derives cards from the configured roadmap document.
- No source file is modified by any UI action.

## Open Questions

-
