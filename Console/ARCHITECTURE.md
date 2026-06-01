# Architecture: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Modules, routes, and directory layout for the Console application. |

## Modules

| Module | Responsibility |
|--------|---------------|
| `Console/app.py` | FastAPI application: config loading, route handlers, markdown rendering, questionnaire rendering, Kanban derivation, SQLite state |
| `Console/console.json` | Project-specific configuration: tabs, documents, kanban, review settings |
| `Console/start.sh` | Start script — launches uvicorn from parent project directory as `Console.app:app` |

## Stack

Python / FastAPI / Uvicorn / SQLite / `markdown` library. No ORM. No external services.

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | `/` | Console UI (HTMLResponse) |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/api/config` | Full active configuration JSON |
| GET | `/api/tabs` | Configured tabs array |
| GET | `/api/document/{tab_id}/{doc_id}` | Rendered document HTML |
| GET | `/raw/{tab_id}/{doc_id}` | Raw file (FileResponse for links) |
| GET | `/api/kanban` | Kanban model: columns + derived cards |
| GET | `/api/state/{key}` | State record by key |
| POST | `/api/state/{key}` | Upsert state record |
| GET | `/api/review` | Review actions and states from config |
| GET | `/api/questionnaires` | Questionnaire index with completion state |
| GET | `/api/reports` | Report index |

## Directory Layout

```
Console/
  app.py                         FastAPI application (generic — no project logic)
  console.json                   Project-specific configuration
  start.sh                       Service start script
  requirements.txt               Python dependencies
  README.md
  data/
    console_state.sqlite         SQLite state database (gitignored)
  evidence/
    README.md                    Evidence index
  questionnaires/
    README.md
    console_process.json         Default questionnaire template
  reports/
    README.md                    Report index
```

The `Console/` directory lives inside the project root. `start.sh` runs from the project root so Python can import `Console.app` as a module.

## Configuration Loading

`app.py` loads `Console/console.json` at module import time. `BASE_DIR` is the `Console/` directory. All relative paths in `console.json` are resolved relative to `BASE_DIR`.

## State Schema

```sql
create table if not exists document_state (
  key text primary key,
  document_id text not null,
  state text not null,
  payload_json text not null,
  updated_at text not null
);
```

State keys are namespaced: `questionnaire.{id}`, `review.{doc_id}.{item_id}`, `kanban.{phase_id}`.

## Open Questions

-
