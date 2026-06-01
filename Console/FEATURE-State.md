# Feature: State

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Generic SQLite state persistence for questionnaires, review decisions, and kanban overrides. |
| Depends On  | FEATURE-Config.md |
| Provides    | GET /api/state/{key}, POST /api/state/{key} |
| Phase       | 1 |

## Purpose

Key-value state store backed by a single SQLite table. Used by questionnaires and review actions. No ORM; direct `sqlite3` connection.

## Trigger

`GET /api/state/{key}` — read current state.
`POST /api/state/{key}` — upsert state record.

## GET Response

If the key exists:
```json
{ "key": "questionnaire.console_process", "document_id": "console_process", "state": "answered", "payload": {...}, "updated_at": "2026-05-31T..." }
```

If absent:
```json
{ "key": "questionnaire.console_process", "state": "incomplete", "payload": {}, "updated_at": null }
```

## POST Request Body

```json
{ "document_id": "console_process", "state": "answered", "payload": { "default_focus": "INTENT" } }
```

Uses `INSERT ... ON CONFLICT(key) DO UPDATE` (upsert). `updated_at` is set to current UTC ISO timestamp.

## Database Initialization

The `document_state` table is created (if not exists) on every `connect_db()` call. The database file is created at the path from `CONFIG["console"]["state_db"]` (relative to `BASE_DIR`); parent directories are created automatically.

## Open Questions

-
