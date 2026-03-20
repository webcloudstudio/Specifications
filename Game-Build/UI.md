# UI Standards

Shared patterns across all screens. Screen specs define only what is unique to that screen.

## Theme

Bootstrap 5 dark theme (`data-bs-theme="dark"`). Custom CSS in `static/style.css`.

| Variable | Purpose |
|----------|---------|
| `--cc-surface` | Card/panel background |
| `--cc-border` | Border color |
| `--cc-muted` | Secondary text |

No JS build step. Bootstrap 5 + HTMX via CDN.

## Navigation Bar

Fixed top. Left to right:

| Element | Behavior |
|---------|----------|
| Brand (`cc-brand`) | App name + icon → project list |
| Tab links | Dashboard, Configuration, GIT-Homepage, Processes, Monitoring, Workflow |
| Documentation button | Opens doc/index.html (green) |
| Settings dropdown | Hamburger → Settings, Tags, Help |
| Running badges | Green pill per running project → project detail |

## Standard Row Header

Shared across Dashboard, Configuration, Processes, Publisher:

| Column | Content |
|--------|---------|
| Status badge | Colored pill: IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED |
| Project icon | Emoji or type icon |
| Display name | Clickable `display_name` |

Status colors: IDEA=#94a3b8, PROTOTYPE=#fdab3d, ACTIVE=#0073ea, PRODUCTION=#00c875, ARCHIVED=#4a5568.

## Operation Buttons

| State | Appearance | Action |
|-------|------------|--------|
| Idle | Named button | Click → run |
| Running | Green pulse + "Stop" | Click → SIGTERM |
| Completed | Brief flash | Auto-reverts |

Categories: `service`, `local`, `maintenance` — each has a CSS class.

## Filter Bar

Client-side filtering (no server round-trip):
- Text search (name/description)
- Status pill toggles
- Tag pill toggles
- Namespace dropdown

## Modals

| Modal | Purpose |
|-------|---------|
| CLAUDE.md Viewer | Shows AGENTS.md content |
| Command Output | Shows operation stdout/stderr |

## HTMX Conventions

Server returns HTML fragments, never JSON (except `/health`). Patterns: `hx-get` for loading, `hx-post` for actions, `hx-target` for DOM replacement, `hx-swap` innerHTML or outerHTML.

## Typography

System font stack. Monospace for logs. Body 14px, headings 16-20px, badges 11px.

Desktop-first. Minimum 1024px width.

## Open Questions

- Mobile/tablet support needed or strictly desktop?
- Custom CSS variables vs Bootstrap defaults?
