# Feature: Config

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Configuration loading and exposure for the Console. |
| Provides    | GET /api/config, GET /api/tabs |
| Phase       | 1 |

## Purpose

Load `Console/console.json` at module startup and expose it via API. No dynamic reload — the app must be restarted to pick up config changes.

## Trigger

Module import (startup). `GET /api/config` and `GET /api/tabs` on demand.

## Sequence

1. On startup: read `Console/console.json` relative to `BASE_DIR` (the `Console/` directory).
2. Parse as JSON. Raise `FileNotFoundError` or `json.JSONDecodeError` on failure — startup fails loudly.
3. Bind `CONFIG` as a module-level constant.
4. `GET /api/config` returns `CONFIG` as JSON.
5. `GET /api/tabs` returns `CONFIG["tabs"]` as JSON.

## Configuration Shape

Required top-level fields: `console`, `project`, `tabs`, `kanban`, `review`.

```json
{
  "console": { "name": "...", "version": "...", "state_db": "data/console_state.sqlite" },
  "project": { "id": "...", "name": "...", "root": "..", "description": "..." },
  "tabs": [...],
  "kanban": { "source_document": "roadmap", "columns": [...] },
  "review": { "actions": [...], "states": [...] }
}
```

## Open Questions

-
