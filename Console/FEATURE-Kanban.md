# Feature: Kanban

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Kanban board derived from configured roadmap documents. |
| Depends On  | FEATURE-Config.md, FEATURE-Documents.md |
| Provides    | GET /api/kanban |
| Phase       | 2 |

## Purpose

Parse roadmap Markdown into Kanban cards and render them as a column board. Cards are derived from headings — no project-specific parsing logic.

## Trigger

- Appended to roadmap document render in `GET /api/document/{tab_id}/{doc_id}` when `document_type == "roadmap"`.
- `GET /api/kanban` returns the full model (columns + cards) as JSON.

## Card Derivation

1. Read roadmap file contents.
2. Find all `## Heading` lines using `re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)`.
3. Filter to headings that start with `heading_prefix` (from doc kanban config, default `"## Phase"`).
4. For each match: generate a slug from the title (`re.sub(r"[^a-z0-9]+", "-", title.lower())`).
5. Assign `default_state` (from doc config, default `"backlog"`).

## Column Rendering

Cards are bucketed into columns from `CONFIG["kanban"]["columns"]`. Each column is rendered as a CSS grid cell with heading and card divs.

## API Response

```json
{
  "columns": ["backlog", "ready", "running", "needs_review", "approved", "parked", "rejected", "done"],
  "cards": [
    { "id": "phase-1", "title": "Phase 1: Foundation", "state": "backlog", "source": "roadmap" }
  ]
}
```

## Open Questions

-
