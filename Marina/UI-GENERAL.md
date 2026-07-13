# UI-GENERAL: Marina

| Field       | Value |
|-------------|-------|
| Version     | 20260603 V7 |
| Description | Shared UI patterns and conventions across all Marina screens. |

All SCREEN-*.md files reference this document for shared elements. Screen specifications define only what is unique to that screen.

---

## Theme

**Default: light-body, dark-nav scheme.** Deep navy navigation with teal accent. Theme is configurable via the `MARINA_THEME` environment variable (`light` | `dark`). Default is `light` when unset.

`base.html` reads `MARINA_THEME` and conditionally sets `data-bs-theme`:

```html
<html lang="en" {% if theme == 'dark' %}data-bs-theme="dark"{% endif %}>
```

The route layer passes `theme = os.environ.get('MARINA_THEME', 'light')` to every template render context.

`.env.sample` entry: `MARINA_THEME=light  # light|dark`

> **PROHIBITED:** Do NOT hardcode `data-bs-theme="dark"` on `<html>`. Do NOT use grey text on dark backgrounds.

| Element | Background | Text / Icon Color |
|---------|-----------|-------------------|
| Top navigation bar | `#0f172a` (deep navy) | `#f1f5f9` (near-white) |
| Sub-navigation bar | `#f1f5f9` (light gray) | `#334155` (slate-700) |
| Active top-tab | `#0d9488` (teal) | `#ffffff` |
| Active sub-tab | `#ffffff` | `#0d9488` (teal) |
| Page body | `#ffffff` | `#1e293b` |
| Cards / panels | `#ffffff` | `#1e293b` |
| Muted / secondary text | — | `#64748b` (slate-500) |
| Borders | — | `#e2e8f0` |

Add the following custom button CSS variables alongside the existing variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `--mn-btn-primary-bg` | `#0d9488` | Primary action button background |
| `--mn-btn-danger-bg` | `#dc2626` | Danger action button background |
| `--mn-btn-caution-bg` | `#d97706` | Caution action button background |
| `--mn-btn-action-bg` | `#3b82f6` | Info/action button background |
| `--mn-btn-secondary-border` | `#94a3b8` | Secondary outline button border |

CSS variables in `static/style.css`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `--mn-nav-bg` | `#0f172a` | Top nav background |
| `--mn-nav-text` | `#f1f5f9` | Top nav text and icons |
| `--mn-nav-active-bg` | `#0d9488` | Active top-tab highlight |
| `--mn-subnav-bg` | `#f1f5f9` | Sub-bar background |
| `--mn-subnav-text` | `#334155` | Sub-bar text |
| `--mn-subnav-active-bg` | `#ffffff` | Active sub-tab background |
| `--mn-subnav-active-text` | `#0d9488` | Active sub-tab text |
| `--mn-body-bg` | `#ffffff` | Page body background |
| `--mn-surface` | `#ffffff` | Card/panel background |
| `--mn-border` | `#e2e8f0` | Border color |
| `--mn-muted` | `#64748b` | Secondary / muted text |
| `--mn-accent` | `#0d9488` | Teal accent for highlights |

---

## Screen Header Template

**MANDATORY.** Every SCREEN-*.md file MUST open with a `# Screen: {Name}` heading followed immediately by this metadata table and a one-line description.

```markdown
# Screen: {Display Name}

| Field | Value |
|-------|-------|
| Version | YYYYMMDD Vn |
| Route | `GET /path` |
| Parent | — |
| Main Menu | SETUP |
| Sub Menu | {sub-tab label} · default  ← omit "· default" if not the default |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Header Background | `mn-hdr-bg--default`  ← see Header Background Types |
| Header Help Text | One sentence shown in the right column of the page header. |
| Description | One-sentence description. |
| Depends On | UI-GENERAL.md |
| Provides | GET /path |
```

---

## Navigation Bar

Two-tier navigation. Top bar is always visible. Sub-bar appears when the active top-level tab has sub-tabs.

### Top Bar

Fixed. Present on all screens. Background: `--mn-nav-bg`.

| Element | Position | Behavior |
|---------|----------|----------|
| **Brand** | Far left | `⚓ Marina` text. Click → `/`. |
| **Left tabs** | Left group | SETUP, PROJECTS, and MONITORING. |
| **Right area** | Far right | Reserved for future tabs. |

### Tab Definitions

| Tab Label | Routes | Default Sub-tab |
|-----------|--------|----------------|
| `SETUP` | `/setup/*` | `/setup/summary` |
| `PROJECTS` | `/projects/*` | `/projects` |
| `MONITORING` | `/monitoring/*` | `/monitoring` |

### Sub-Navigation Bar — Tab Groups

Shown for the active tab. Background: `--mn-subnav-bg`. Tabs are always rendered for the active section and
organised into visual groups separated by a 1px `var(--mn-border)` vertical divider.

| Group | Tabs | Purpose |
|-------|------|---------|
| SETUP | Summary · AWS · Terraform · GitHub · Git Scan · Repositories · Projects · Settings | Onboarding and integration setup |
| PROJECTS | Dashboard · Capabilities · Workflow · Configuration · Validation · Maintenance | Registry, discovery, organization, standards, and project work |
| MONITORING | Health · Scheduler · Processes | Command center and operations |

A 1px `var(--mn-muted)` vertical divider is rendered between each group (not before the first, not after the last). Group separators are purely visual — they do not affect tab behaviour, routing, or ARIA roles.

Some tabs may be **disabled** (not hidden) when their prerequisites are unmet.

| # | Sub-tab | Route | Disabled when |
|---|---------|-------|---------------|
| 1 | Summary | `/setup/summary` | Never — default landing |
| 2 | AWS | `/setup/aws` | Never |
| 3 | Terraform | `/setup/terraform` | Never |
| 4 | GitHub | `/setup/github` | Never |
| 5 | Git Scan | `/setup/scan` | GitHub not configured (auth ❌ or SSH ❌ or no sources), or no PROJECTS_DIR |
| 6 | Repositories | `/setup/repositories` | GitHub header light ❌ or ⚠️ (auth, SSH, or no sources), or PROJECTS_DIR not set |
| 7 | Projects | `/setup/projects` | PROJECTS_DIR not set |
| 8 | Settings | `/setup/settings` | Never |

PROJECTS sub-tabs:

| Sub-tab | Route | Disabled when |
|---------|-------|---------------|
| Dashboard | `/projects` | Never |
| Capabilities | `/projects/capabilities` | Never; empty state if no discovery data |
| Workflow | `/projects/workflow` | Deferred from the initial build |
| Configuration | `/projects/configuration` | Never |
| Validation | `/projects/validation` | Deferred from the initial build |
| Maintenance | `/projects/maintenance` | Deferred from the initial build |

**Disabled tab appearance:** muted text (`--mn-muted`), no pointer cursor, `aria-disabled="true"`. Clicking a disabled tab shows a tooltip: `Complete {prerequisite} first.` Do not navigate.

### Template Structure

| File | Contains |
|------|---------|
| `templates/_nav_top.html` | Top navigation bar (brand + top-level tabs) |
| `templates/_nav_sub.html` | Sub-navigation bar — section-conditional per `active_section` |
| `templates/base.html` | Shell only: includes both partials |

All screen templates extend `base.html` and set `active_section` and `active_page` in route handlers.

---

## Page Header

**MANDATORY on every SETUP screen.** A full-width dark header block rendered below the sub-navigation bar and above the page content. The header is always rendered on `--mn-nav-bg` (deep navy `#0f172a`) regardless of the body light/dark theme.

### Three-Column Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [KPI BLOCK — left]           ⚓  Marina                  [spacer]       │
│                               (large, centered)                           │
└──────────────────────────────────────────────────────────────────────────┘
```

The header is a CSS grid: `grid-template-columns: 1fr auto 1fr; align-items: center`. This guarantees the center column is mathematically centered regardless of KPI width.

| Column | Grid | Content |
|--------|------|---------|
| Left | `1fr` | KPI block. Empty `<div>` when the page has no KPIs — preserves centering of the title. |
| Center | `auto` | ⚓ icon + `Marina` title. Always present. See Center Column Detail. |
| Right | `1fr` | Page help text. Short sentence describing what this section is for. Right-aligned, muted (`--mn-hdr-muted`), 0.8rem, max 2 lines. Each SCREEN-*.md declares its `Header Help Text`. Empty `<div>` when no help text is defined. |

### Center Column Detail

| Element | Spec |
|---------|------|
| Icon | Always `bi-anchor` (⚓). 28px. Near-white (`--mn-nav-text`). 0.5rem gap before title. |
| Title | `Marina`. Near-white (`--mn-nav-text`). 28px bold. No sub-page suffix on any screen — page identity comes from the active sub-tab. |
| Padding | `1rem 1.5rem` on the outer header. |

> **PROHIBITED:** Do NOT render `Marina — {Page Name}` in the header. Do NOT place the page title in the right column. The title is always just `Marina`, always centered.

---

## Header Background Types

Each screen declares a `Header Background` in its metadata table. The value is a CSS class applied to the outer header `<div>`. This lets each screen type have a distinct visual treatment without changing the layout.

| Class | Background | Use |
|-------|-----------|-----|
| `mn-hdr-bg--default` | `--mn-nav-bg` (#0f172a deep navy) | All setup screens — default |
| `mn-hdr-bg--cloud` | `#0c1a2e` (darker blue-black) | AWS and Terraform screens |
| `mn-hdr-bg--git` | `#0f1e17` (dark green-black) | GitHub, Git Scan, Repositories, Projects |
| `mn-hdr-bg--settings` | `#1a1a2e` (dark indigo) | Settings screen |
| `mn-hdr-bg--summary` | `--mn-nav-bg` (#0f172a deep navy) | Summary screen |

CSS definition in `static/style.css`:

```css
.mn-hdr-bg--default  { background: var(--mn-nav-bg); }
.mn-hdr-bg--cloud    { background: #0c1a2e; }
.mn-hdr-bg--git      { background: #0f1e17; }
.mn-hdr-bg--settings { background: #1a1a2e; }
.mn-hdr-bg--summary  { background: var(--mn-nav-bg); }
```

All backgrounds are dark enough that `--mn-hdr-*` text variables remain legible without adjustment.

---

## Header KPI CSS

KPI elements live on the always-dark header surface. They use their own CSS variable set, separate from the body theme variables, so they remain legible on `--mn-nav-bg` whether the body is light or dark.

```css
/* Always dark-surface — do NOT reference --mn-body-bg or Bootstrap body vars here */
--mn-hdr-text:       #f1f5f9;   /* primary text on dark header */
--mn-hdr-muted:      #94a3b8;   /* secondary / label text on dark header */
--mn-hdr-ok-bg:      #0d9488;   /* teal — "setup / all good" chip */
--mn-hdr-warn-bg:    #d97706;   /* amber — "partial / attention" chip */
--mn-hdr-error-bg:   #dc2626;   /* red — "not set up / failing" chip */
--mn-hdr-count-text: #ffffff;   /* count number colour */
--mn-hdr-count-label:#94a3b8;   /* count label colour */
--mn-hdr-btn-border: #f1f5f9;   /* ghost action button border on dark */
```

### KPI Component Types

Four reusable KPI components. Each is a compact inline block. Multiple components sit side-by-side in the left column with `gap: 1.5rem`.

---

#### 1. Status Chip — `mn-hdr-chip`

A rounded-pill badge. Used for "Setup" / "Not Set Up" / "Partial" on pages with a single readiness state.

```html
<span class="mn-hdr-chip mn-hdr-chip--ok">Setup</span>
<span class="mn-hdr-chip mn-hdr-chip--warn">Partial</span>
<span class="mn-hdr-chip mn-hdr-chip--error">Not Set Up</span>
```

```css
.mn-hdr-chip {
  display: inline-block; padding: 0.2rem 0.75rem;
  border-radius: 999px; font-size: 0.8rem; font-weight: 600;
  color: #fff; letter-spacing: 0.02em;
}
.mn-hdr-chip--ok    { background: var(--mn-hdr-ok-bg); }
.mn-hdr-chip--warn  { background: var(--mn-hdr-warn-bg); }
.mn-hdr-chip--error { background: var(--mn-hdr-error-bg); }
```

---

#### 2. Count Block — `mn-hdr-count`

A stacked number + label. Used for repo counts, project counts, etc.

```html
<div class="mn-hdr-count">
  <span class="mn-hdr-count__number">42</span>
  <span class="mn-hdr-count__label">Repos</span>
</div>
```

```css
.mn-hdr-count { display: flex; flex-direction: column; align-items: center; }
.mn-hdr-count__number { font-size: 1.4rem; font-weight: 700;
                        color: var(--mn-hdr-count-text); line-height: 1; }
.mn-hdr-count__label  { font-size: 0.75rem; color: var(--mn-hdr-count-label);
                        margin-top: 0.1rem; }
```

Multiple count blocks side-by-side are separated by a 1px `var(--mn-hdr-muted)` vertical divider.

---

#### 3. All-Good Indicator — `mn-hdr-allgood`

Used on Summary and Terraform. Shows overall system health at a glance.

```html
<!-- All clear -->
<div class="mn-hdr-allgood mn-hdr-allgood--ok">
  <i class="bi bi-check-circle-fill"></i>
  <span>All systems ready</span>
</div>
<!-- Attention needed -->
<div class="mn-hdr-allgood mn-hdr-allgood--warn">
  <i class="bi bi-exclamation-triangle-fill"></i>
  <span>3 items need attention</span>
</div>
```

```css
.mn-hdr-allgood { display: flex; align-items: center; gap: 0.5rem;
                  font-size: 0.9rem; font-weight: 600; }
.mn-hdr-allgood i { font-size: 1.2rem; }
.mn-hdr-allgood--ok   { color: var(--mn-hdr-ok-bg); }
.mn-hdr-allgood--warn { color: var(--mn-hdr-warn-bg); }
.mn-hdr-allgood--error { color: var(--mn-hdr-error-bg); }
```

---

#### 4. Status Light — `mn-hdr-light`

A vertical traffic light: three stacked circles (red top, amber middle, green bottom) in a dark housing. The active state circle is bright; the other two are dimmed to 15% opacity. Used on setup screens where the KPI is a readiness indicator. Must render as a recognisable traffic light — not a single dot.

```html
<div class="mn-hdr-light mn-hdr-light--ok">
  <div class="mn-hdr-light__dot mn-hdr-light__dot--red"></div>
  <div class="mn-hdr-light__dot mn-hdr-light__dot--amber"></div>
  <div class="mn-hdr-light__dot mn-hdr-light__dot--green"></div>
</div>
```

```css
.mn-hdr-light {
  display: flex; flex-direction: column; align-items: center;
  gap: 3px; padding: 5px 7px;
  background: #0a0a0a; border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.15);
  flex-shrink: 0;
}
.mn-hdr-light__dot {
  width: 14px; height: 14px; border-radius: 50%;
}
.mn-hdr-light__dot--red   { background: var(--mn-hdr-error-bg); }
.mn-hdr-light__dot--amber { background: var(--mn-hdr-warn-bg); }
.mn-hdr-light__dot--green { background: var(--mn-hdr-ok-bg); }

/* OK — green lit, others dim */
.mn-hdr-light--ok .mn-hdr-light__dot--green { box-shadow: 0 0 6px var(--mn-hdr-ok-bg); }
.mn-hdr-light--ok .mn-hdr-light__dot--amber,
.mn-hdr-light--ok .mn-hdr-light__dot--red   { opacity: 0.15; }

/* Warn — amber lit, others dim */
.mn-hdr-light--warn .mn-hdr-light__dot--amber { box-shadow: 0 0 6px var(--mn-hdr-warn-bg); }
.mn-hdr-light--warn .mn-hdr-light__dot--green,
.mn-hdr-light--warn .mn-hdr-light__dot--red   { opacity: 0.15; }

/* Error — red lit, others dim */
.mn-hdr-light--error .mn-hdr-light__dot--red   { box-shadow: 0 0 6px var(--mn-hdr-error-bg); }
.mn-hdr-light--error .mn-hdr-light__dot--green,
.mn-hdr-light--error .mn-hdr-light__dot--amber { opacity: 0.15; }
```

---

#### 5. Header Action Button — `mn-hdr-btn`

A ghost (outline) button rendered on the dark header surface. Used when the page's primary trigger belongs in the header (e.g. Scan Now). Different from body `btn-mn-*` classes — do not use those inside the header.

```html
<button class="mn-hdr-btn" hx-post="/api/repositories/sync" ...>
  <i class="bi bi-arrow-clockwise"></i> Scan GitHub Now
</button>
```

```css
.mn-hdr-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.35rem 1rem; border-radius: 6px;
  border: 1.5px solid var(--mn-hdr-btn-border);
  background: transparent; color: var(--mn-hdr-text);
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
}
.mn-hdr-btn:hover { background: rgba(255,255,255,0.1); }
.mn-hdr-btn:disabled { opacity: 0.45; cursor: not-allowed; }
```

---

### KPI Assignments per Page

| Page | KPI Type | Content | Source |
|------|----------|---------|--------|
| Summary | All-Good | ✅ "All systems ready" / ⚠️ "N items need attention" | Count of ❌/⚠️ rows in SETUP STATUS card |
| AWS | Status Light | Green / Amber / Red dot | `python_aws_ok` + `aws_profile` |
| Terraform | All-Good | ✅ "Deployed" / ❌ "Not deployed" | `MARINA_API_URL` set + `endpoint_reachable` |
| GitHub | Status Light | Green / Amber / Red dot | auth + SSH + ≥1 scan source |
| Git Scan | Action Button | `[↻ Scan GitHub Now]` | Button triggers `POST /api/repositories/sync` |
| Repositories | Count Block | `{N}` · `Repos` | `github_repos` count |
| Projects | Count Blocks (×2) | `{N}` · `Conformed` + `{N}` · `Total` | `projects.is_conformed` aggregates |
| Settings | _(none)_ | — | — |

---

## Page Icons

Icons identify each screen. Two icon sources are used — both loaded via CDN:

| Library | CDN | Usage |
|---------|-----|-------|
| **Bootstrap Icons** (`bi-*`) | `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11/font/bootstrap-icons.min.css` | Marina-native UI icons and GitHub |
| **Simple Icons** (`si-*`) | `https://cdn.simpleicons.org/{slug}/{color}` — inline SVG `<img>` | Brand logos: AWS, Terraform |

Both CDN links are included in `base.html`. Simple Icons are used as `<img src="https://cdn.simpleicons.org/{slug}/f1f5f9" width="20" height="20">` (near-white tint for header use) or with brand colour for card headers.

### Page Icon Assignments

| Tab | Page Name | Bootstrap Icon class | Simple Icons slug | Icon description |
|-----|-----------|---------------------|-------------------|-----------------|
| Summary | Marina | `bi-house-fill` | — | Home / landing |
| AWS | AWS | — | `amazonaws` | Amazon Web Services logo |
| Terraform | Terraform | — | `terraform` | HashiCorp Terraform logo |
| GitHub | GitHub | `bi-github` | — | GitHub mark (Bootstrap Icons built-in) |
| Git Scan | Git Scan | `bi-arrow-clockwise` | — | Refresh / scan cycle |
| Repositories | Repositories | `bi-folder2-open` | — | Open folder |
| Projects | Projects | `bi-kanban` | — | Kanban / project board |
| Settings | Settings | `bi-sliders2` | — | Sliders / configuration |

**Implementation:** In the page header template, emit the icon before the title text. For Bootstrap Icons: `<i class="bi {class}"></i>`. For Simple Icons: `<img src="https://cdn.simpleicons.org/{slug}/0d9488" width="22" height="22" alt="">` (teal in header, brand colour in card headers).

Card headers within a page may repeat the page icon in brand colour for visual hierarchy — this is optional, not mandatory.

---

## Button Standards

**ALL buttons across every screen MUST use one of these five semantic variants.** Do not use ad-hoc Bootstrap `btn-primary`, `btn-success`, etc. — every button has a colour because of its meaning, not its position on the page.

### Variants

| Class | Background | Text | Semantic meaning | Example uses |
|-------|-----------|------|-----------------|-------------|
| `btn-mn-primary` | `#0d9488` teal | white | Save, confirm, proceed — the positive forward action | Save Settings, Conform, Publish, Re-check |
| `btn-mn-danger` | `#dc2626` red | white | Destructive, irreversible remove | Remove source account, Delete |
| `btn-mn-caution` | `#d97706` amber | white | Creates real external resources or side effects outside Marina | Run Apply (Terraform), Save to .env |
| `btn-mn-action` | `#3b82f6` blue | white | Informational trigger — no data change, just checks or navigation | Test Connection, Check AWS Identity, Scan Now, Re-check Auth |
| `btn-mn-secondary` | transparent | `#334155` slate | Cancel, back, neutral secondary | Cancel, Back, Show steps again |

### Rules

1. **One primary per card.** Each `mn-card` has at most one `btn-mn-primary`. Use `btn-mn-secondary` for accompanying cancel/back.
2. **Caution requires a warning.** Any `btn-mn-caution` button must have a visible ⚠️ warning statement on the same card describing the side effect.
3. **Disabled state.** Disabled buttons use `opacity: 0.45`, `cursor: not-allowed`, and retain their colour class. Do not swap to a grey class — the disabled colour still communicates meaning.
4. **In-progress state.** Replace button text with a spinner + `{verb}ing…` (e.g. `Saving…`, `Scanning…`). Keep the same colour class. Button is `disabled` during the operation.
5. **Size.** Default size for all buttons. Use `btn-sm` equivalent (0.8rem, reduced padding) only for inline table-row actions.

### CSS definition (in `static/style.css`)

```css
.btn-mn-primary   { background: var(--mn-btn-primary-bg);  color: #fff; border: none; }
.btn-mn-danger    { background: var(--mn-btn-danger-bg);   color: #fff; border: none; }
.btn-mn-caution   { background: var(--mn-btn-caution-bg);  color: #fff; border: none; }
.btn-mn-action    { background: var(--mn-btn-action-bg);   color: #fff; border: none; }
.btn-mn-secondary { background: transparent; color: var(--mn-subnav-text);
                    border: 1px solid var(--mn-btn-secondary-border); }

.btn-mn-primary:hover   { filter: brightness(1.1); }
.btn-mn-danger:hover    { filter: brightness(1.1); }
.btn-mn-caution:hover   { filter: brightness(1.1); }
.btn-mn-action:hover    { filter: brightness(1.1); }
.btn-mn-secondary:hover { background: #f1f5f9; }

[class^="btn-mn"]:disabled,
[class^="btn-mn"].disabled { opacity: 0.45; cursor: not-allowed; pointer-events: none; }
```

---

## Status Badges

Used across screens to show project lifecycle state.

| Status | Color | Hex |
|--------|-------|-----|
| IDEA | Slate | `#94a3b8` |
| PROTOTYPE | Amber | `#fdab3d` |
| ACTIVE | Teal | `#0d9488` |
| PRODUCTION | Green | `#00c875` |
| ARCHIVED | Gray | `#4a5568` |
| UNKNOWN | Muted | `#64748b` |

---

## Checklist Icons

Used on the Setup Summary checklist and inline status indicators.

| Icon | Meaning |
|------|---------|
| ✅ | Configured and accessible |
| ⚠️ | Set but may need attention |
| ❌ | Missing or inaccessible |
| 📌 | Informational — no action required |

---

## Cards

Content panels use a card pattern:

```html
<div class="mn-card">
    <div class="mn-card-header">Section Title</div>
    <div style="padding: 1rem">
        <!-- content -->
    </div>
</div>
```

Cards have a 1px `var(--mn-border)` border, 8px radius, white surface background.

---

## Inline-Editable Fields

Settings-backed fields on the Summary and Settings screens use always-visible text inputs (not hidden until click):

- Border: `1px solid var(--mn-border)`, 4px radius, white background, 4px 8px padding
- On focus: `2px solid var(--mn-accent)` border
- Tab-out or blur triggers `POST /api/setup/config`

**Save feedback:** Toast fixed top-right (green on success, red on error). Fades after 2 seconds.

---

## HTMX Conventions

| Pattern | Usage |
|---------|-------|
| `hx-get` | Load fragments (repo table refresh, project row) |
| `hx-post` | Trigger actions (conform, download, scan, config save) |
| `hx-target` | Replace specific DOM element with response |
| `hx-swap` | Usually `innerHTML` or `outerHTML` |

Server returns HTML fragments for partial updates; full page for initial loads.

---

## Responsive Behavior

Designed for desktop use. Minimum supported width: 1024px. Nav bar scrolls horizontally on smaller screens.

---

## Typography

System font stack (no web fonts). Monospace for logs and code output.

| Element | Font | Size |
|---------|------|------|
| Body | System sans-serif | 14px |
| Headings | System sans-serif | 16–20px |
| Nav tab labels | System sans-serif | 13px |
| Sub-bar tab labels | System sans-serif | 13px |
| Log / code output | System monospace | 13px |
| Badges/pills | System sans-serif | 12px |

---

## Flash Messages

Standard Bootstrap 5 alert dismissible pattern. Categories: `success`, `danger`, `warning`, `info`.

---

## Open Questions

- Should Marina support a dark-mode toggle in the UI rather than via env var? Future — add to SCREEN-SETUP-SETTINGS when implemented.
