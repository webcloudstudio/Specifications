# Feature: Questionnaires

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Questionnaire rendering and state persistence. |
| Depends On  | FEATURE-Config.md, FEATURE-State.md |
| Provides    | GET /api/questionnaires |
| Phase       | 2 |

## Purpose

Render JSON questionnaires as HTML forms and persist answers to SQLite. Never write back to the questionnaire source file.

## Questionnaire File Shape

```json
{
  "id": "questionnaire_id",
  "title": "Display Title",
  "state": "incomplete",
  "purpose": "Why this questionnaire exists.",
  "questions": [
    {
      "id": "question_id",
      "label": "Display Label",
      "prompt": "Question text shown to the user.",
      "input": "select",
      "options": ["option1", "option2"]
    }
  ]
}
```

## Supported Input Types

| Type | HTML Control |
|------|-------------|
| `text` | `<input type="text">` |
| `textarea` | `<textarea rows="4">` |
| `select` | `<select>` |
| `multiselect` | `<select multiple>` |
| `number` | `<input type="number">` |
| `slider` | `<input type="range" min max>` |

## Form Submission (Client-Side)

On submit, JavaScript collects all form field values into a payload object and POSTs to `POST /api/state/questionnaire.{id}` with `state: "answered"`. Multi-select fields accumulate into arrays.

## Completion Index

`GET /api/questionnaires` returns all configured questionnaire documents with their current `state` from SQLite (defaulting to `"incomplete"` if no state record exists).

## Open Questions

-
