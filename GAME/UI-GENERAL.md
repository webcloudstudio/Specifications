# UI General Standards

**Version:** 20260320 V1  
**Description:** Shared UI patterns and conventions across all screens

**Shared UI patterns, components, and conventions used across all screens.**

All SCREEN-*.md files reference this document for shared elements. Screen specifications define only what is unique to that screen.

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

Three-tier navigation. Top bar is always visible. Sub-bars appear when their respective top-level items are active.

### Top Bar

Fixed. Present on all screens. Components left to right:

| Element | Behavior |
|---------|----------|
| **Brand** (`cc-brand`) | App name (🎮 icon or command-line symbol). Click → Dashboard (`/`). |
| **Top-level tabs** | Icon + two-line label (see Tab Labels below). Left to right: Welcome, Prototypes, Projects, Processes, Monitoring, Workflow, Publisher, Catalog. Active tab highlighted. Welcome is leftmost and is the default. |
| **Settings** | ⚙️ gear icon + label "Settings". Far right, before Help. Click → activates Settings context and displays Settings sub-bar. |
| **Help** | 📖 book icon. Rightmost item. Click → navigates to `/help`. |
| **Running badges** | Green pill badges for each currently-running project. Click → project detail. |

### Tab Labels

Each top-level tab renders as a vertical stack: icon centered on top, text below in up to two lines. Long names split at a natural word boundary.

| Tab | Icon | Line 1 | Line 2 |
|-----|------|--------|--------|
| Welcome | 🏠 | Welcome | |
| Prototypes | 🚀 | Proto- | types |
| Projects | 📁 | Projects | |
| Processes | ⚙️ | Pro- | cesses |
| Monitoring | 📊 | Monitor- | ing |
| Workflow | 📋 | Simple | Workflow |
| Publisher | 📢 | Portfolio | Publisher |
| Catalog | 📚 | Service | Catalog |
| Settings | ⚙️ | Settings | |
| Help | 📖 | Help | |

CSS class: `cc-nav-tab`. Icon in a `cc-nav-icon` span above text in a `cc-nav-label` span. Max tab width: ~80px. Font size for label: 11px.

### Tab Defaults

Each top-level tab navigates to a defined default route when first selected:

| Tab | Default Route | Notes |
|-----|--------------|-------|
| Welcome (🏠) | `/welcome/summary` | Has sub-bar |
| Prototypes (🚀) | `/prototypes` | Single screen, no sub-bar |
| Projects (📁) | `/` (Dashboard) | Has sub-bar |
| Processes (⚙️) | `/processes` | Single screen, no sub-bar |
| Monitoring (📊) | `/monitoring` | Has sub-bar; Monitoring is the default |
| Workflow (📋) | `/workflow/kanban` | Has sub-bar; Kanban is the default |
| Publisher (📢) | `/publisher` | Single screen, no sub-bar |
| Catalog (📚) | `/servicecatalog` | Single screen, no sub-bar |
| Settings (⚙️) | `/settings/general` | Has sub-bar |
| Help (📖) | `/help` | Single screen, no sub-bar |

### Welcome Sub-Bar

Visible only when `Welcome` (🏠) is active in the top bar. Renders directly below the top bar.

| Element | Position | Behavior |
|---------|----------|----------|
| **Summary** tab | Left | Links to `/welcome/summary` — read-only configuration health view. Default. |
| **Prototypes** tab | Left | Links to `/welcome/prototypes` — searchable prototype list |
| **Projects** tab | Left | Links to `/welcome/projects` — searchable project list |

Summary is the default sub-tab when Welcome is first selected.

### Project Sub-Bar

Visible only when `Projects` is active in the top bar. Renders directly below the top bar. Contains tabs only — no action buttons.

| Element | Position | Behavior |
|---------|----------|----------|
| **Dashboard** tab | Left | Links to `/` — default project list |
| **Configuration** tab | Left | Links to `/project-config` — batch metadata editor |

Dashboard is the default sub-tab when Projects is first selected. The Dashboard screen carries its own action bar (filter + Rescan) within the page content — see SCREEN-PROJECTS-OVERVIEW.

### Monitoring Sub-Bar

Visible only when `Monitoring` is active in the top bar. Renders directly below the top bar.

| Element | Position | Behavior |
|---------|----------|----------|
| **Monitoring** tab | Left | Links to `/monitoring` — service health and event log. Default. |
| **Scheduler** tab | Left | Links to `/scheduler` — scheduled operations overview |

Monitoring is the default sub-tab when Monitoring is first selected.

### Workflow Sub-Bar

Visible only when `Workflow` is active in the top bar. Renders directly below the top bar.

| Element | Position | Behavior |
|---------|----------|----------|
| **Kanban** tab | Left | Links to `/workflow/kanban` — kanban board. Default. |
| **Add Ticket** tab | Left | Links to `/workflow/add` — ticket creation form |
| **Manage** tab | Left | Links to `/workflow/manage` — workflow types and label configuration |

Kanban is the default sub-tab when Workflow is first selected.

### Settings Sub-Bar

Visible only when `Settings` (gear icon in top bar) is active. Renders directly below the top bar, replacing the Project Sub-Bar.

| Element | Position | Behavior |
|---------|----------|----------|
| **General** tab | Left | Links to `/settings/general` — application settings |
| **Tags** tab | Left | Links to `/settings/tags` — tag color configuration |
| **Help** tab | Left | Links to `/settings/help` — application help |
| **Voice** tab | Left | Links to `/settings/voiceforward/config` — voice button management |
| **Voice Docs** tab | Left | Links to `/settings/voiceforward/docs` — phone setup documentation |

General is the default sub-tab when Settings is first selected.

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

List screens carry their own filter controls in the page action bar (not the sub-bar). Filters are client-side (no server round-trip) for responsiveness.

Dashboard filter controls (see SCREEN-PROJECTS-OVERVIEW):

| Control | Type | Behavior |
|---------|------|----------|
| Text search | Input field | Filters rows by name match |
| Status filter | Pill buttons | Toggle visibility by status |
| Namespace filter | Dropdown | Filter by namespace |
| Rescan button | Button | POST `/api/scan`; refreshes project list |

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

## Open Questions

- Should the nav bar's top-level tabs be configurable (show/hide per user preference)? Not in V1 — all tabs are always visible. A future settings option could hide infrequently-used tabs.
- Should running badges in the nav bar auto-dismiss after a configurable timeout? Yes — badges clear when the process exits (already the design). No timeout behavior needed.
