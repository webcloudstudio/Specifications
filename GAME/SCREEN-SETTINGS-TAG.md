# Screen: Tag Settings

**Version:** 20260325 V1
**Description:** Spec for the Tag Settings screen — assign display colors to tags from a curated preset palette

Tags are discovered automatically from `projects.tags` across all projects. This screen assigns a foreground/background color pair to each tag. Colors are drawn from a curated preset list chosen for legibility on the dark theme.

## Menu Navigation

`Settings / Tag`

(Accessed via the Settings dropdown in the top navigation bar.)

## Route

```
GET /settings/tags
```

## Layout

Two-column layout. Left: tag list with color assignment. Right: live preview panel showing tags as pills and buttons.

```
┌───────────────────────────────┬──────────────────────────┐
│  Tags                         │  Preview                  │
│  ─────────────────────────────│  ────────────────────────│
│  python    [● Emerald   ▼]    │  ● python   ● flask       │
│  flask     [● Coral     ▼]    │  ● ml       ● data        │
│  ml        [● Violet    ▼]    │  [python]  [flask]        │
│  data      [● Sky       ▼]    │  (button style preview)  │
│  ...                          │                           │
│                               │                           │
│  [Reset All]  [Save Changes]  │                           │
└───────────────────────────────┴──────────────────────────┘
```

## Tag List (left panel)

One row per distinct tag found across all projects. Tags are collected by scanning `projects.tags` (comma-separated) across all active projects. Sorted alphabetically.

### Row Structure

| Element | Content |
|---------|---------|
| Color swatch dot | Small filled circle in the currently assigned color |
| Tag name | The raw tag string |
| Color picker dropdown | Preset color selector (see Preset Palette below) |
| Usage count | Dim badge: number of projects carrying this tag |

### Color Picker Dropdown

A compact dropdown showing the preset palette. Each option renders as:

```
● Color Name     (swatch + label)
```

The currently selected color is highlighted. Selecting a new color updates the swatch immediately (client-side preview) but does not save until `Save Changes` is clicked.

### Unassigned Tags

Tags with no assigned color render with a default neutral color (`--cc-muted` background). The dropdown shows `○ None (default)` as the first option.

## Preset Palette

A fixed list of foreground/background pairs designed for legibility on the dark theme. All combinations meet 4.5:1 contrast ratio.

| Name | Background | Foreground | Use for |
|------|------------|------------|---------|
| Emerald | `#10b981` | `#fff` | Services, active |
| Sky | `#0ea5e9` | `#fff` | Frontend, UI |
| Violet | `#8b5cf6` | `#fff` | ML, AI |
| Coral | `#f43f5e` | `#fff` | Alerts, critical |
| Amber | `#f59e0b` | `#000` | In-progress, warning |
| Slate | `#64748b` | `#fff` | Neutral, infra |
| Teal | `#14b8a6` | `#fff` | Data, pipelines |
| Rose | `#fb7185` | `#000` | Deprecated, legacy |
| Indigo | `#6366f1` | `#fff` | Core, platform |
| Lime | `#84cc16` | `#000` | Scripts, tooling |
| Orange | `#f97316` | `#fff` | Prototypes, experiments |
| Zinc | `#a1a1aa` | `#000` | Archived, muted |

## Preview Panel (right panel)

Live preview updating as the user selects colors. Shows two views:

**Pill view** — tags rendered as `<span class="badge">` pills, same as they appear on the Dashboard.

**Button view** — tags rendered as small outline buttons, as they might appear in filters or the tag filter bar.

Preview pulls from the currently unsaved draft colors — updates on each dropdown change without a server round-trip.

## Save Behavior

`Save Changes` button (primary, bottom-left of tag list):
1. Collects all color assignments
2. `POST /settings/tags` with JSON payload: `{ "tag_colors": { "<tag>": { "bg": "#hex", "fg": "#hex" }, ... } }`
3. Server writes to `data/tag_colors.json` and updates the `tag_colors` table (if implemented per DATABASE.md open question)
4. Flash: "Tag colors saved." Success.
5. Dashboard and all tag pills reflect the new colors immediately on next page load.

`Reset All` button (outline, secondary): Clears all custom assignments, reverts to default neutral. Prompts a confirmation before executing.

## Data Sources

| Source | Content |
|--------|---------|
| `projects.tags` (all active projects) | Discover existing tags |
| `data/tag_colors.json` | Current color assignments (read on load) |
| `tag_colors` DB table | Future canonical source per DATABASE.md |

## Open Questions

- Should the palette be user-extensible (custom hex input) or strictly preset?
- Should tag color assignments be per-namespace (different colors in production vs development)?
- Should unused tags (no active projects carrying them) be hidden, greyed out, or shown with a dim indicator?
