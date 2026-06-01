# Screen: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Single-page Console UI: tab navigation, document area, questionnaire forms, Kanban board. |
| Route       | / |
| Parent      | — |
| Main Menu   | — |
| Tab Order   | — |
| Depends On  | UI-GENERAL.md, FEATURE-Config.md, FEATURE-Documents.md, FEATURE-Kanban.md, FEATURE-Questionnaires.md, FEATURE-State.md |
| Phase       | 2 |

## Layout

See `UI-GENERAL.md` for color palette, grid, and typography.

- **Header**: fixed top bar, dark background, Console name.
- **Left nav**: tab buttons stacked vertically (full tab list from config). Below the active tab's button, document sub-buttons appear.
- **Content area**: renders the active document HTML returned by `GET /api/document/{tab_id}/{doc_id}`.

## Interactions

| Action | Behavior |
|--------|---------|
| Click tab button | Load first document of that tab; update doc button list |
| Click doc button | Load that document into content area |
| Submit questionnaire form | POST answers to `/api/state/questionnaire.{id}`; show alert on success |
| Page load | Auto-load the first document of the first tab (or `default_tab` from config) |

## State

All state is server-side (SQLite). No client-side state persists across page reloads. The full config is embedded in the page as a JS constant for client-side tab/doc navigation.

## Error Handling

- If a document fetch returns an error, the content area shows the error detail from the JSON response.
- Missing files return HTTP 404 from the server; the client displays the detail message.

## Open Questions

-
