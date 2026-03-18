# UI General Standards

**Shared UI patterns, components, and conventions used across all screens.**

All SCREEN-*.md files reference this document for shared elements. Screen specs define only what is unique to that screen.

---

## Theme

Dark theme using Bootstrap 5 `data-bs-theme="dark"`. Custom CSS in `static/style.css` extends Bootstrap with platform-specific variables:

| Variable | Purpose | Value |
|----------|---------|-------|
| `--cc-surface` | Card/panel background | Dark surface |
| `--cc-border` | Border color | Subtle dark border |
| `--cc-muted` | Secondary text | Muted gray |

No JS build step. Bootstrap 5 via CDN. HTMX via CDN.

---

## Navigation Bar

Fixed top bar present on all screens. Components left to right:

| Element | Behavior |
|---------|----------|
| **Brand** (`cc-brand`) | App name with command icon. Click --> project list. |
| **Tab links** | Projects, Configuration, GIT-Homepage, Processes, Monitoring, Workflow. Active tab highlighted. |
| **Documentation button** | Opens `doc/index.html` in new tab. |
| **Settings dropdown** | Hamburger icon. Contains: Settings, Tags, Help. |
| **Running badges** | Green pill badges for each currently-running project. Click --> project detail. |

---

## Standard Row Header

Several screens share a standard row header pattern for project rows:

| Column | Content | Width |
|--------|---------|-------|
| Status badge | Colored pill: IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED | Fixed |
| Project icon | Emoji or type icon | Fixed |
| Display name | `display_name` from METADATA.md, clickable | Flex |

This pattern appears on: Dashboard, Configuration, Processes (as project column), Publisher.

Status badge colors:

| Status | Color | Hex |
|--------|-------|-----|
| IDEA | Slate | `#94a3b8` |
| PROTOTYPE | Amber | `#fdab3d` |
| ACTIVE | Blue | `#0073ea` |
| PRODUCTION | Green | `#00c875` |
| ARCHIVED | Gray | `#4a5568` |

---

## Settings Icon (Cog)

Used on multiple screens. The cog icon opens a detail/edit view for the project's METADATA.md fields. Context-dependent behavior:

| Screen | Cog Action |
|--------|------------|
| Dashboard | Opens project detail with inline editing |
| Configuration | Opens full METADATA.md field editor |
| Publisher | Opens publication field editor |

---

## Tag Pills

Tags render as small colored pills. Color from `tag_colors` table/config. Inline editable on some screens.

```html
<span class="badge" style="background: {tag_color}">{tag_name}</span>
```

---

## Cards

Content panels use a card pattern:

```html
<div class="cc-card">
    <div class="cc-card-header">Section Title</div>
    <div style="padding: 1rem">
        <!-- content -->
    </div>
</div>
```

---

## Modals

Two global modals defined in `base.html`:

| Modal | ID | Purpose |
|-------|----|---------|
| CLAUDE.md Viewer | `claudeModal` | Shows AGENTS.md content for a project |
| Command Output | `opOutputModal` | Shows operation stdout/stderr output |

Modals use dark surface background with themed borders.

---

## HTMX Conventions

All screen interactions use HTMX partial page updates:

| Pattern | Usage |
|---------|-------|
| `hx-get` | Load fragments (project detail, log content) |
| `hx-post` | Trigger actions (run op, stop, push, scan) |
| `hx-target` | Replace specific DOM element with response |
| `hx-swap` | Usually `innerHTML` or `outerHTML` |
| `hx-trigger` | Click (default), or custom events |

Server returns HTML fragments, never JSON (except `/health`).

---

## Operation Buttons

Rendered per-operation on dashboard rows and project detail:

| State | Appearance | Action |
|-------|------------|--------|
| Idle | `op-btn` styled button with operation name | Click --> run |
| Running | Green pulsing indicator, "Stop" label | Click --> SIGTERM |
| Recently completed | Brief success/error flash | Auto-reverts to idle |

Category determines button style:

| Category | Style Class |
|----------|-------------|
| `service` | `op-btn--service` |
| `local` | `op-btn--local` |
| `maintenance` | `op-btn--maintenance` |

---

## Filter Bar

Dashboard and other list screens share a filter pattern:

| Filter | Type | Behavior |
|--------|------|----------|
| Text search | Input field | Filters rows by name/description match |
| Status filter | Pill buttons | Toggle visibility by status |
| Tag filter | Pill buttons | Filter by selected tags |
| Namespace filter | Dropdown | Filter by namespace |

Filters are client-side (no server round-trip) for responsiveness.

---

## Flash Messages

Standard Bootstrap 5 alert dismissible pattern. Categories: `success`, `danger`, `warning`, `info`.

---

## Typography

System font stack (no web fonts). Monospace for logs and code output.

| Element | Font | Size |
|---------|------|------|
| Body | System sans-serif | 14px |
| Headings | System sans-serif | 16-20px |
| Log output | System monospace | 13px |
| Badges/pills | System sans-serif | 11px |

---

## Responsive Behavior

Designed for desktop use (operations center). Minimum supported width: 1024px. Nav bar scrolls horizontally on smaller screens. No mobile-first breakpoints.
