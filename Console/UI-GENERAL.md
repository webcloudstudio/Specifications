# UI-GENERAL: Console

| Field       | Value |
|-------------|-------|
| Version     | 20260531 V1 |
| Description | Shared UI patterns for the Console single-page application. |

## Layout

Two-column grid: fixed left navigation (260px) + fluid content area. Full-height minus header.

```
┌─ header ─────────────────────────────┐
│ Console Name                         │
├─ nav (260px) ──┬─ article ───────────┤
│ [TAB BUTTONS]  │                     │
│                │  content area       │
│ [DOC BUTTONS]  │                     │
└────────────────┴─────────────────────┘
```

## Navigation

- **Tab buttons** in the left nav switch the active tab; clicking a tab loads its first document automatically.
- **Document buttons** appear below tab buttons, scoped to the active tab.
- Active tab is indicated by nav button state (browser default focus/active).

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#f6f7f9` | Page background |
| Surface | `#ffffff` | Cards, nav, question blocks |
| Border | `#d7dde5` | All borders |
| Border light | `#cbd5e1` | Input borders |
| Text primary | `#1b2430` | Body text |
| Header bg | `#111827` | Top header, form submit button |
| Header text | `#ffffff` | Header and submit button text |
| Hover | `#eef2f7` | Nav button hover, code background |
| Code bg | `#eef2f7` | Inline code, pre blocks |

## Typography

Font: Segoe UI, Arial, sans-serif. No external font loading.

## Document Area

Max-width 1100px, padding 24px top/bottom, 32px left/right. Markdown tables are full-width with bottom border cells. Code blocks use pre with overflow-x scroll.

## Questionnaire Forms

Each question is a card (white background, border, 12px padding). Form submit button is full-width within the form only (not the nav). On submit, answers are POSTed to `/api/state/questionnaire.{id}` and a browser alert confirms save.

## Kanban Board

CSS grid, auto-fit columns, min 160px each. Each column is a white bordered card with a heading. Phase cards show title + ID code.

## Open Questions

-
