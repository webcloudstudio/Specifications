# Intent: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260601 V2 |
| Description | Goals, constraints, and success criteria for the Console review surface. |

## Goals

- Replace `teamai_console` as the agile build gate and product-owner review surface.
- Deploy to every promoted project via `ProjectUpdate/ProjectInitialize` — the app lives in `Prototyper/Console/` and is copied to each project's `Console/` directory. No per-project build step.
- Auto-configure via `build_plan.sh --analysis`: writes `console.json` alongside `AGILE_PLAN.md` in the spec directory; `ProjectUpdate` deploys it to `ProjectName/Console/console.json`.
- Read `AGILE_PLAN.md` as the live state database: parse spikes, stories, and ACs with inline state; write approve/revise/reject decisions back atomically (flock + temp-swap).
- Show per-object evidence artifacts (STEP_*.md) written by `oneshot2.sh`.
- Render configured documents (BUILD_PLAN_INTENT.md, BUILD_PLAN.md, questionnaires, reports) from relative paths in `console.json`.
- Persist questionnaire answers in local SQLite without touching source documents.

## Constraints

- Must not write to source Markdown, CSV, or project data files during UI interaction (decisions write to AGILE_PLAN.md only — this is the intended gate mechanism).
- Must not call external model APIs or remote services.
- Must not require authentication for local use.
- Must not embed project-specific logic in `app.py` — all bindings belong in `console.json`.
- `app.py` must not import from `teamai_console/` — the AGILE_PLAN.md state machine is replicated inline.

## Success Criteria

- `ProjectUpdate.sh ProjectName` copies `Prototyper/Console/` to `ProjectName/Console/` and deploys `console.json` from the spec dir.
- `build_plan.sh --analysis ProjectName` writes `Specifications/ProjectName/console.json` with correct relative paths.
- `bash ProjectName/Console/start.sh` starts the Console; `GET /health` returns ok.
- The AGILE tab renders spikes and stories from `AGILE_PLAN.md` in the correct Kanban columns.
- Approve/revise/reject decisions are written back into `AGILE_PLAN.md` immediately.
- `oneshot2.sh` polling detects the state change and continues the build.
- Evidence (STEP_*.md) renders per-object in the detail panel.
- Questionnaire answers persist to SQLite only.

## Open Questions

-
