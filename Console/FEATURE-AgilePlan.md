# Feature: AgilePlan

| Field       | Value |
|-------------|-------|
| Version     | 20260601 V1 |
| Description | AGILE_PLAN.md state machine: parse, board, evidence, decisions, defects. |
| Depends On  | FEATURE-Config.md |
| Provides    | GET /api/summary, GET /api/objects, GET /api/board, GET /api/objects/{oid}/evidence, POST /api/objects/{oid}/decision, POST /api/objects/{oid}/defect |
| Phase       | 1 |

## Purpose

AGILE_PLAN.md IS the state database. The Console reads it to render the Kanban board and per-object detail. Decisions (approve/revise/reject) write state back into AGILE_PLAN.md atomically — this is what `oneshot2.sh` polls to decide whether to continue the build.

## Config Section

```json
"agile_plan": {
  "path": "../AGILE_PLAN.md",
  "evidence_dir": "../evidence"
}
```

Both paths are relative to `BASE_DIR` (`Console/` directory). Resolved at startup as module-level constants `PLAN_PATH` and `EVIDENCE_DIR`.

## AGILE_PLAN.md Format

Parsed by `_parse_plan()`. Objects are headed by `## spike N: title`, `## story N: title`, `## ac N: criterion`. Each block has inline field lines (`state:`, `summary:`, `evidence:`, etc.).

Object types and terminal states:

| Type | Terminal Good State |
|------|-------------------|
| `spike` | `approved` |
| `story` | `accepted` |
| `ac` | `verified` |

## Kanban Columns

Objects are assigned to Kanban columns by their `state` field:

| State(s) | Column |
|----------|--------|
| `pending`, `revise` | backlog |
| `running`, `built`, `tested` | progress |
| `awaiting_review` | review |
| `approved`, `accepted` | done |
| `rejected`, `failed` | blocked |

## Evidence

Each spike/story has an `evidence:` field listing filenames (comma-separated). Files are resolved from `EVIDENCE_DIR`. `_evidence_markdown(oid)` concatenates them with `---` separators and returns raw Markdown; the route renders it to HTML.

## Decision Writing

`POST /api/objects/{oid}/decision` body: `{action: "approve"|"revise"|"reject", feedback: "..."}`.

Implementation: `_set_plan_fields()` rewrites the `state:` line in AGILE_PLAN.md atomically using `fcntl.LOCK_EX` + `tempfile.mkstemp` + `os.replace`. This is the same mechanism as `teamai_console/app/store.py`.

When a spike/story is approved/accepted, all its open AC items are auto-verified.

## Defect Entry

`POST /api/objects/{oid}/defect` body: `{text: "criterion text"}`.

Appends a new `## ac N:` block to AGILE_PLAN.md with `origin: po`. Sends the parent ticket back to `revise` state so `oneshot2.sh` will re-run it.

## API Summary

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/summary` | `{spec, total, approved, awaiting, plan_present}` |
| GET | `/api/objects` | All objects with state, ACs, evidence_present |
| GET | `/api/board` | `{columns: [{key, label, tickets}]}` |
| GET | `/api/objects/{oid}/evidence` | `{oid, object, html}` — rendered evidence |
| POST | `/api/objects/{oid}/decision` | `{ok, id, status}` |
| POST | `/api/objects/{oid}/defect` | `{ok, ac, parent, status}` |

## Open Questions

-
