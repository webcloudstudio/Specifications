# UI General Standards

**Version:** 20260411 V2
**Description:** Shared UI patterns and conventions across all screens

All SCREEN-*.md files reference this document for shared elements. Screen specifications define only what is unique to that screen.

---

## Theme

**Default: light-body, dark-nav professional scheme.** Theme is configurable via the `GAME_THEME` environment variable (`light` | `dark`). Default is `light` when unset.

`base.html` reads `GAME_THEME` and conditionally sets `data-bs-theme`:
```html
<html lang="en" {% if theme == 'dark' %}data-bs-theme="dark"{% endif %}>
```

The route layer passes `theme = os.environ.get('GAME_THEME', 'light')` to every template render context.

`.env.sample` entry: `GAME_THEME=light  # light|dark`

> **[ROADMAP] Settings UI:** A theme selector in Settings → General will allow switching without editing `.env`.

**Light mode (default).** Custom CSS in `static/style.css`. The colors below apply when `GAME_THEME=light`.

> **PROHIBITED:** Do NOT hardcode `data-bs-theme="dark"` on `<html>`. Do NOT use grey text on dark backgrounds. Do NOT use grey icons on dark backgrounds.

| Element | Background | Text / Icon Color |
|---------|-----------|-------------------|
| Top navigation bar | `#1e293b` (dark navy) | `#f1f5f9` (near-white) |
| Sub-navigation bar | `#f1f5f9` (light gray) | `#334155` (slate-700) |
| Active top-tab | `#0073ea` (blue accent) | `#ffffff` |
| Active sub-tab | `#ffffff` | `#0073ea` (blue accent) |
| Page body | `#ffffff` | `#1e293b` |
| Cards / panels | `#ffffff` | `#1e293b` |
| Muted / secondary text | — | `#64748b` (slate-500) |
| Borders | — | `#e2e8f0` |

CSS variables in `static/style.css`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `--cc-nav-bg` | `#1e293b` | Top nav background |
| `--cc-nav-text` | `#f1f5f9` | Top nav text and icons |
| `--cc-nav-active-bg` | `#0073ea` | Active top-tab highlight |
| `--cc-subnav-bg` | `#f1f5f9` | Sub-bar background |
| `--cc-subnav-text` | `#334155` | Sub-bar text |
| `--cc-subnav-active-bg` | `#ffffff` | Active sub-tab bg |
| `--cc-subnav-active-text` | `#0073ea` | Active sub-tab text |
| `--cc-body-bg` | `#ffffff` | Page body background |
| `--cc-surface` | `#ffffff` | Card/panel background |
| `--cc-border` | `#e2e8f0` | Border color |
| `--cc-muted` | `#64748b` | Secondary / muted text |

---

## Screen Navigation Convention

Every routed screen file declares its position in the navigation using this block immediately after the description header:

```
## Menu Navigation

Main Menu: {tab name}
Sub Menu: {sub-tab name} (Default)
Inherits From: SCREEN-DEFAULT
```

Rules:
- **Main Menu** — the top-bar tab label exactly as shown in the Tab Definitions table below.
- **Sub Menu** — the sub-bar tab label. Add `(Default)` if this screen is the default sub-tab for its top-level tab. Omit the line entirely for single-screen top-level tabs with no sub-bar.
- **Inherits From** — present only when the screen extends `SCREEN-DEFAULT`. Omit otherwise.
- Settings and Help use `[right]` annotation: `Main Menu: Settings [right]`
- Standalone pages with no GAME navigation bar (e.g. VoiceForward mobile recorder) use: `(standalone — no GAME navigation bar)`

---

## Navigation Bar

Two-tier navigation. Top bar is always visible. Sub-bar appears below the top bar when the active top-level tab has sub-tabs.

### Top Bar

Fixed. Present on all screens. Background: `--cc-nav-bg` (`#1e293b`).

| Element | Position | Behavior |
|---------|----------|----------|
| **Brand** | Far left | App name + command-line icon. Click → `/`. |
| **Left tabs** | Left group | Welcome, Projects, Prototypes, Monitoring, Workflow, Catalog, Publisher — in that order. |
| **Running badges** | Center/flex spacer | Green pill badges for each currently-running project. Click → project detail. |
| **Settings** | Right group, first | `⚙️ Settings`. Click → activates Settings context, shows Settings sub-bar. |
| **Help** | Right group, last | `📖 Help`. Click → `/help`. |

Settings and Help are right-aligned (pushed to the far right by a flex spacer before them).

### Tab Definitions

Each tab renders as icon above label. Icon: 20px emoji rendered in native color (not filtered or recolored). Label: system sans-serif, 13px, white on the navy background. No word-splitting, no hyphenation.

| Tab | Icon | Label | Default Route | Sub-bar |
|-----|------|-------|---------------|---------|
| Welcome | 🏠 | Welcome | `/welcome/summary` | Yes |
| Projects | 📁 | Projects | `/` | Yes |
| Prototypes | 🚀 | Prototypes | `/prototypes/list` | Yes |
| Monitoring | 📊 | Monitoring | `/monitoring` | Yes |
| Workflow | 📋 | Workflow | `/workflow/kanban` | Yes |
| Catalog | 📚 | Service Catalog | `/servicecatalog` | No |
| Publisher | 📢 | Publisher | `/publisher` | No |
| Settings | ⚙️ | Settings | `/settings/general` | Yes — right-aligned |
| Help | 📖 | Help | `/help` | No — right-aligned |

"Service Catalog" renders as two lines: "Service" / "Catalog". All other labels are single-line. Max tab width: 90px.

CSS class: `cc-nav-tab`. Icon in `cc-nav-icon` span, label in `cc-nav-label` span.

> **IMPORTANT:** Tab icons are bare emoji characters in HTML — e.g. `<span class="cc-nav-icon">🏠</span>`. Do NOT use Bootstrap Icons (`<i class="bi bi-*">`) for top-nav tab icons. Emoji render in native color; Bootstrap Icons render monochrome.

### Sub-Bars

Sub-bar background: `--cc-subnav-bg` (`#f1f5f9`). Active tab: white background, blue text. Font: 13px system sans-serif, dark text.

#### Welcome Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| Summary | `/welcome/summary` | Default |
| Prototypes | `/welcome/prototypes` | Searchable prototype list |
| Projects | `/welcome/projects` | Searchable project list |

#### Projects Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| Dashboard | `/` | Default |
| Configuration | `/project-config` | Batch metadata editor |
| Validation | `/project-validation` | Compliance checks |
| Maintenance | `/project-maintenance` | Maintenance-category operations |
| Setup | `/project-setup` | Discover and register GitHub repos |

#### Prototypes Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| List | `/prototypes/list` | Default |
| Configuration | `/prototypes/configuration` | Batch METADATA.md editor |
| Validation | `/prototypes/validation` | Specification compliance checks |
| Maintenance | `/prototypes/maintenance` | Specifications bin/ script runner |

#### Monitoring Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| Monitoring | `/monitoring` | Default — service health and event log |
| Scheduler | `/scheduler` | Scheduled operations overview |
| Processes | `/processes` | Live log viewer and process control |

#### Workflow Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| Kanban | `/workflow/kanban` | Default |
| Add Ticket | `/workflow/add` | Ticket creation form |
| Manage | `/workflow/manage` | Workflow types and label configuration |

#### Settings Sub-Bar

| Tab | Route | Notes |
|-----|-------|-------|
| General | `/settings/general` | Default — application settings |
| Tags | `/settings/tags` | Tag color configuration |
| Voice | `/settings/voiceforward/config` | Voice button management |
| Voice Docs | `/settings/voiceforward/docs` | Phone setup documentation |
| Help | `/settings/help` | Application help |

---

### Template Structure

Navigation is split into two partial templates. `base.html` must NOT contain inline nav HTML — it includes the partials:

| File | Contains |
|------|---------|
| `templates/_nav_top.html` | Top navigation bar only (brand + all top-level tabs + running badges) |
| `templates/_nav_sub.html` | Sub-navigation bar — section-conditional (`{% if active_section == 'welcome' %}` … `{% elif %}` chain) |
| `templates/base.html` | Shell only: `{% include '_nav_top.html' %}` then `{% include '_nav_sub.html' %}` |

All screen templates extend `base.html` and set `active_section` and `active_page` in their route handlers.

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

Three global modals defined in `base.html`:

| Modal | ID | Purpose |
|-------|----|---------|
| CLAUDE.md Viewer | `claudeModal` | Shows AGENTS.md content for a project |
| Command Output | `opOutputModal` | Shows operation stdout/stderr output |
| Script Viewer | `scriptViewerModal` | Shows script file content with gateway endpoint — opened from Service Catalog |

Modals use white surface background with standard light borders.

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

Rendered per-operation on Dashboard rows, project detail, and the Service Catalog.

### Run States (Dashboard / Project Detail)

| State | Appearance | Action |
|-------|------------|--------|
| Idle | Category-styled button with operation name | Click → run |
| Running | Green pulsing ring, label becomes "Stop" | Click → SIGTERM |
| Recently completed | Brief success (green) or error (red) flash | Auto-reverts to idle after 2s |

### Category Button Styles

| Category | Style class | Color | Icon prefix | Meaning |
|----------|-------------|-------|-------------|---------|
| `Operations` | `op-btn--operations` | Green `#00c875` | ▶ / ■ / ⚙ / 🧪 | Core lifecycle: start, stop, build, test. Primary actions. |
| `Workflow` | `op-btn--workflow` | Blue `#0073ea` | → | Project tools: analysis, generation, maintenance scripts. Secondary. |
| `Global` | `op-btn--global` | Amber `#fdab3d` | ⤴ | Crosses repo boundaries. Visually distinct to signal cross-project impact. |

**Icon prefix rules** (Operations only):

| Script name | Icon |
|-------------|------|
| `start.sh` | ▶ |
| `stop.sh` | ■ |
| `build.sh`, `build_documentation.sh` | ⚙ |
| `test.sh` | 🧪 |

Button text is the script's `# Name:` header value.

### Service Catalog Buttons (reference mode)

On the Service Catalog screen, buttons are **not run buttons** — clicking shows the Script Viewer modal instead. Same category colors and icons apply. Tooltip on hover: "Click to view script".

---

## Script Viewer Modal

Global modal (`scriptViewerModal`) defined in `base.html`. Opened when a script button is clicked on the Service Catalog screen.

| Element | Content |
|---------|---------|
| Header | `{filename} — {# Name:}` (bold) |
| Subtitle | `Category: {category}  ·  {project display_name}` |
| Body | Full script content in a monospace scrollable `<pre><code>` block. Syntax highlighted (Bash or Python depending on extension). Max height 60vh, scrollable. |
| Footer | `Gateway endpoint: POST /api/{project_name}/run/{script_stem}` — muted monospace. `[Copy]` button copies endpoint to clipboard. |
| Close | × button (top right), click-outside, Escape key. |

Content fetched via `GET /api/{project_name}/script/{script_stem}` on modal open. Shows a loading spinner until the fetch resolves.

Global scripts (`Category: Global`) show an amber warning banner in the modal header:

> ⚠ This script modifies files in other repositories.

---

## Filter Bar

List screens carry their own filter controls in the page action bar (not the sub-bar). Filters are client-side (no server round-trip) for responsiveness.

Dashboard filter controls (see SCREEN-PROJECTS-DASHBOARD):

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
| Headings | System sans-serif | 16–20px |
| Nav tab labels | System sans-serif | 13px |
| Sub-bar tab labels | System sans-serif | 13px |
| Log output | System monospace | 13px |
| Badges/pills | System sans-serif | 12px |

---

## Responsive Behavior

Designed for desktop use (operations center). Minimum supported width: 1024px. Nav bar scrolls horizontally on smaller screens. No mobile-first breakpoints.

## Open Questions

- Should the nav bar's top-level tabs be configurable (show/hide per user preference)? Not in V1 — all tabs are always visible.
- Should running badges in the nav bar auto-dismiss after a configurable timeout? Yes — badges clear when the process exits. No timeout behavior needed.
