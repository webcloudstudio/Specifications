# UI-GENERAL: Marina

| Field       | Value |
|-------------|-------|
| Version     | 20260602 V3 |
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
| **Left tabs** | Left group | SETUP — the only top-level tab in Phase 1. |
| **Right area** | Far right | Reserved for future tabs. |

### Tab Definitions

| Tab Label | Routes | Default Sub-tab |
|-----------|--------|----------------|
| `SETUP` | `/setup/*` | `/setup/summary` |

### Sub-Navigation Bar

Shown for the SETUP tab. Background: `--mn-subnav-bg`. Eight tabs always rendered; some may be **disabled** (not hidden) when their prerequisites are unmet.

| # | Sub-tab | Route | Disabled when |
|---|---------|-------|---------------|
| 1 | Summary | `/setup/summary` | Never — default landing |
| 2 | AWS | `/setup/aws` | Never |
| 3 | Terraform | `/setup/terraform` | Never |
| 4 | GitHub | `/setup/github` | Never |
| 5 | Git Scan | `/setup/scan` | GitHub not configured (auth ❌ or SSH ❌), or no PROJECTS_DIR |
| 6 | Repositories | `/setup/repositories` | GitHub not configured, or PROJECTS_DIR not set |
| 7 | Projects | `/setup/projects` | PROJECTS_DIR not set |
| 8 | Settings | `/setup/settings` | Never |

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

**MANDATORY on every SETUP screen.** A full-width dark header block rendered below the sub-navigation bar and above the page content.

```
┌────────────────────────────────────────────────────────────────────┐
│  [icon]  Marina — {Page Name}       {One-line page description}    │
│          (24px bold)                (14px muted, right block)      │
└────────────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Background | `--mn-nav-bg` (deep navy `#0f172a`) |
| Left: icon | Optional page icon (see Page Icons). 24px, rendered in teal (`--mn-accent`) for Bootstrap Icons / SVG. Inline before the title, 0.5rem gap. |
| Left: page title | `Marina — {Page Name}`. `Marina —` in teal accent (`--mn-accent`), `{Page Name}` in near-white (`--mn-nav-text`). Font: 24px bold. |
| Right: description | One-line description of what this screen does. 14px, `--mn-muted`. Text block flexed to the far right; not right-justified text alignment — it is a block anchored to the right edge. |
| Padding | `1rem 1.5rem` |

The **Summary** screen uses title "Marina" (no sub-page suffix) and description "Marina setup overview." All other screens use "Marina — {Page Name}" where `{Page Name}` matches the sub-tab label.

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
