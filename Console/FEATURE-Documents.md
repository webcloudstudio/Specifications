# Feature: Documents

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Document rendering for all configured document types. |
| Depends On  | FEATURE-Config.md |
| Provides    | GET /api/document/{tab_id}/{doc_id}, GET /raw/{tab_id}/{doc_id} |
| Phase       | 1 |

## Purpose

Render configured documents on demand. The renderer is generic: behavior is determined by `document_type` in the tab config, not by project-specific logic.

## Trigger

`GET /api/document/{tab_id}/{doc_id}`

## Document Types

| Type | Render Behavior |
|------|----------------|
| `markdown` | Read file → render via `markdown` library (tables + fenced_code extensions) → return HTML |
| `link` | Return a hyperlink (`<a href="/raw/{tab_id}/{doc_id}">`) — file served via `/raw/` |
| `questionnaire` | Read JSON questionnaire → render as HTML form (see FEATURE-Questionnaires.md) |
| `roadmap` | Render as markdown + append Kanban board HTML (see FEATURE-Kanban.md) |

## Path Resolution

All paths in document entries are resolved relative to `BASE_DIR` (`Console/` directory). If the resolved file does not exist, return HTTP 404 with `detail: "Missing file: {path}"`.

## Response Shape

```json
{
  "document": { "id": "...", "name": "...", "path": "...", ... },
  "html": "<rendered HTML string>"
}
```

For `link` type, `html` contains a hyperlink. The actual file is served at `GET /raw/{tab_id}/{doc_id}` as a `FileResponse`.

## Open Questions

-
