# Screen: Workflow — Manage

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /workflow/manage` |
| Parent | — |
| Main Menu | WORKFLOW |
| Sub Menu | Manage |
| Tab Order | 1: Board · 2: Add Ticket · 3: Manage |
| Header Background | `mn-hdr-bg--default` |
| Header Help Text | Configure workflow types, labels, and board behavior. |
| Description | Management screen for workflow types and ticket labels. |
| Depends On | UI-GENERAL.md, FEATURE-WORKFLOW-SERVICE.md |
| Provides | GET /workflow/manage |

## Header KPIs

Left column uses two `mn-hdr-count` blocks: Types and Labels.

## Layout

Two `mn-card` sections stacked vertically: Workflow Types, Labels.

## Workflow Types

| Column | Editable |
|--------|----------|
| Name | Yes |
| File Prefix | Yes |
| Color | Yes |
| Active | Yes |

## Labels

| Column | Editable |
|--------|----------|
| Name | Yes |
| Color | Yes |
| Active | Yes |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Add type | Button click | POST /api/workflow/types |
| Edit type | Blur | PATCH /api/workflow/types/{id} |
| Delete type | Trash click | DELETE /api/workflow/types/{id}, blocked if in use |
| Add label | Button click | POST /api/workflow/labels |
| Edit label | Blur | PATCH /api/workflow/labels/{id} |
| Delete label | Trash click | DELETE /api/workflow/labels/{id}, blocked if in use |

## Open Questions
- None.
