# UI-GENERAL: Marina

| Field       | Value |
|-------------|-------|
| Version     | 20260529 V1 |
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
| Tab Order | 1: Summary · 2: AWS · 3: GitHub · 4: Repositories · 5: Projects · 6: Settings |
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

Shown for the SETUP tab. Background: `--mn-subnav-bg`.

| Sub-tab | Route | Notes |
|---------|-------|-------|
| Summary | `/setup/summary` | Default landing |
| AWS | `/setup/aws` | |
| GitHub | `/setup/github` | |
| Repositories | `/setup/repositories` | |
| Projects | `/setup/projects` | |
| Settings | `/setup/settings` | |

### Template Structure

| File | Contains |
|------|---------|
| `templates/_nav_top.html` | Top navigation bar (brand + top-level tabs) |
| `templates/_nav_sub.html` | Sub-navigation bar — section-conditional per `active_section` |
| `templates/base.html` | Shell only: includes both partials |

All screen templates extend `base.html` and set `active_section` and `active_page` in route handlers.

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
