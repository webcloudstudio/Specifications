# Feature: Review

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Review action vocabulary and state exposure. |
| Depends On  | FEATURE-Config.md, FEATURE-State.md |
| Provides    | GET /api/review |
| Phase       | 2 |

## Purpose

Expose the review action vocabulary and state list from config. Review decisions are stored as state writes — they do not modify source documents.

## Trigger

`GET /api/review` returns actions and states from `CONFIG["review"]`.

## Response

```json
{
  "actions": ["approve", "revise", "reject", "park", "defer"],
  "states": ["incomplete", "answered", "awaiting_review", "approved", "revised", "rejected", "parked", "deferred"]
}
```

## Review State Writes

A review decision for document `{doc_id}` item `{item_id}` is stored as:

```
POST /api/state/review.{doc_id}.{item_id}
{ "document_id": "{doc_id}", "state": "approved", "payload": { "note": "..." } }
```

The UI calls `POST /api/state/{key}` directly — no separate review write endpoint is required.

## Required Actions

| Action | State Result |
|--------|-------------|
| `approve` | `approved` |
| `revise` | `revised` |
| `reject` | `rejected` |
| `park` | `parked` |
| `defer` | `deferred` |

## Open Questions

-
