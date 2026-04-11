# Screen: VoiceForward — Button Configuration

| Field | Value |
|-------|-------|
| Version | 20260328 V1 |
| Route | `GET /settings/voiceforward/config`, `GET /settings/voiceforward` (redirect) |
| Parent | — |
| Main Menu | Settings [right] |
| Sub Menu | Voice |
| Tab Order | 1: General · 2: Tags · 3: Voice · 4: Voice Docs · 5: Help |

Manage voice recorder buttons — set label, target file, color, and display order.

## Layout

Single-column, max-width 700px. Button list in a `cc-card`. Add button at the top right.

```
┌──────────────────────────────────────────────────────────────┐
│  Voice Buttons                              [+ Add Button]   │
│  ──────────────────────────────────────────────────────────  │
│  ■  BOOK IDEAS    TheTruth/ideas.md              ↑↓  ✏  🗑  │
│  ■  GAME SPEC     Specifications/GAME/ideas.md   ↑↓  ✏  🗑  │
│  ■  GAME          GAME/queue.md                  ↑↓  ✏  🗑  │
│                                                              │
│  (empty state: "No buttons configured. Add one above.")      │
└──────────────────────────────────────────────────────────────┘
```

Add/Edit form (appears inline below the list):

```
┌──────────────────────────────────────────────────────────────┐
│  Button Text      [ BOOK IDEAS                             ] │
│  File to Append   [ TheTruth/ideas.md                      ] │
│  (relative to $PROJECTS_DIR)                                 │
│  Color            [■ #fdab3d ]                               │
│  Active           [✓]                                        │
│                                                              │
│  [Save]  [Cancel]                                            │
└──────────────────────────────────────────────────────────────┘
```

## Button List Columns

| Column | Content |
|--------|---------|
| Color swatch | 20×20px square; background = `color` hex value |
| Label | Button text in normal weight |
| Target file | Relative path in muted monospace (`--cc-muted`, `font-family: monospace`) |
| Reorder | ↑↓ arrows; PUT `/api/voice/buttons/{id}/reorder` with swapped sort_order values |
| Edit | Pencil icon; expands inline form pre-populated with current values |
| Delete | Trash icon; opens confirm modal before DELETE call |

## Add / Edit Form Fields

| Field | Key | Type | Validation | Helper text |
|-------|-----|------|-----------|-------------|
| Button Text | `label` | Text input | Required; must be unique | Displayed on the recorder button |
| File to Append To | `target_file` | Text input | Required | Relative to `$PROJECTS_DIR` — e.g. `TheTruth/ideas.md` |
| Color | `color` | Color picker (hex) | Required | Background color of the recorder button |
| Active | `active` | Toggle/checkbox | — | Hidden from recorder when off |

## Interactions

| Action | Trigger | Behavior |
|--------|---------|----------|
| Add button | Click `+ Add Button` | Inline form appended below list; Save → POST `/api/voice/buttons`; success refreshes list |
| Edit | Click pencil | Row expands to form with current values; Save → PUT `/api/voice/buttons/{id}` |
| Delete | Click trash | Confirm modal: "Delete {label}?" — Yes → DELETE `/api/voice/buttons/{id}`; list refreshes |
| Reorder | Click ↑ or ↓ | Swaps sort_order with adjacent row; PUT to update both; list re-renders |
| Cancel | Click Cancel in form | Collapses form; no write |

## Data Flow

| Reads | Writes |
|-------|--------|
| `voice_buttons` (all rows, ORDER BY sort_order) | `voice_buttons` INSERT / UPDATE / DELETE |

HTMX partial updates: list fragment replaces on each successful write. No full-page reload.

## Open Questions

- Should inactive buttons be shown in the list (greyed out) or hidden? Show them greyed so the user knows they exist.
- Should there be a max button count? No constraint in V1 — the mobile recorder will scroll if there are many buttons.
