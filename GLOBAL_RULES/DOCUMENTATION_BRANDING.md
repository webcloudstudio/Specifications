# Documentation Branding Standards

**Version:** 20260320 V1
**Description:** Color variables, sidebar colors, and typography standards for documentation themes
**Maintainer:** Ed Barlow / Web Cloud Studio
**Reference implementation:** `/mnt/c/Users/barlo/projects/gem/doc/`

---

## Design Philosophy

Documentation uses a **dark chrome / light content** split:

- **Navigation chrome** (top bar, left sidebar) — dark background, light text. Always dark regardless of content mode.
- **Content area** — light background (`#F4FAF4` tinted white), dark text. Optimised for reading long documents.
- **Hyperlinks in content** — standard blue, always underlined. This is the web convention and should not be overridden for content links.
- **Navigation links** — no underline. Hover shows a colored left border (accent color) and subtle background lift.

The dark chrome and the content area create a natural frame. The sidebar and top bar read as **one continuous dark panel** — they use the same background color family, with the top bar slightly darker than the sidebar body.

---

## The Four-Color System

Every theme reduces to four visible color families:

| # | Role | Where used | Example (Evergreen) |
|---|---|---|---|
| 1 | **Top bar** (darkest) | `body.gem-topbar` background | `#071208` |
| 2 | **Sidebar + section banners** (slightly lighter) | `body.gem-sidebar`, content `<h1>` section dividers | `#0C1E10` |
| 3 | **Light text on dark** | Sidebar links, top bar text, GEM badge text, version, copyright | `#90C898` |
| 4 | **Accent** | GEM badge bg, sidebar hover indicator (3px left border), h1 underline, callout borders | `#7AE890` |

Content headings (h1/h2/h3) use progressively lighter shades of the theme's base hue on the light content background. Hyperlinks are always `#1565C0` blue regardless of theme.

**Rule:** If two things are in the dark chrome zone, they must either be the same color or clearly different shades of the same family. Never place dark green text on a dark green background.

---

## Available Themes

Six themes ship with the reference implementation. Each is defined as a single `:root {}` CSS variable block.

| Theme name | Base color | Hex | Character |
|---|---|---|---|
| `green` *(default)* | Evergreen | `#1B5E20` | Forest green, clean |
| `midnight` | Midnight Blue | `#0D3B8E` | Corporate navy |
| `purple` | Royal Purple | `#4527A0` | Distinctive, dramatic |
| `midnight-green` | Midnight Green | `#004953` | Deep teal |
| `mughal` | Mughal Green | `#306030` | Rich forest |
| `rainforest` | Tropical Rainforest | `#00755E` | Warm teal-green |

---

## Theme Variable Reference

The complete set of CSS custom properties required per theme. Copy this block and fill in values to create a new theme.

```css
/* GEM Theme: <Name>  |  gem-base.css must follow this file */
:root {
  /* ── Dark chrome (top bar + sidebar) ─────────────────── */
  --c-topbar-bg:     ;   /* darkest — top bar background */
  --c-side-bg:       ;   /* slightly lighter — sidebar body + content section banners */
  --c-side-border:   ;   /* border between chrome and content, scrollbar */
  --c-side-section:  ;   /* muted section label text (small uppercase in sidebar) */
  --c-side-link:     ;   /* sidebar link text, top bar version + copyright text */

  /* ── Accent ───────────────────────────────────────────── */
  --c-accent:        ;   /* GEM badge bg, sidebar hover left border, callout borders */
  --c-accent-text:   ;   /* text ON the GEM badge (usually very dark, matches topbar) */

  /* ── Content headings (on light bg — must be ≥4.5:1 contrast) ─ */
  --c-h1:            ;   /* darkest heading — close to base color */
  --c-h1-border:     ;   /* h1 underline (light tint of theme color) */
  --c-h2:            ;   /* medium heading */
  --c-h2-border:     ;   /* h2 underline (lighter) */
  --c-h3:            ;   /* lighter heading */

  /* ── Content area ─────────────────────────────────────── */
  --c-bg:            ;   /* page background (tinted white, not pure white) */
  --c-text:          ;   /* body text (very dark, near-black, slight tint of theme) */

  /* ── Tables ───────────────────────────────────────────── */
  --c-th-bg:         ;   /* table header background (use h1 color or darker) */
  --c-th-text:       ;   /* table header text (light) */
  --c-td-border:     ;   /* cell borders (light tint) */
  --c-tr-alt:        ;   /* alternating row background */
  --c-tr-hover:      ;   /* row hover background */

  /* ── Code ─────────────────────────────────────────────── */
  --c-code-bg:       ;   /* inline code background (light tint) */
  --c-code-text:     ;   /* inline code text (h1 or h2 color) */
  --c-pre-bg:        ;   /* code block background (match topbar-bg) */
  --c-pre-text:      ;   /* code block text (match side-link) */

  /* ── Callout box ──────────────────────────────────────── */
  --c-callout-bg:    ;   /* rgba(accent, 0.07) */
  --c-callout-border:;   /* rgba(accent, 0.25) */

  /* ── Footer ───────────────────────────────────────────── */
  --c-foot-text:     ;   /* muted copyright footer text */
}
```

### Evergreen (default) — complete example

```css
:root {
  --c-topbar-bg:     #071208;
  --c-side-bg:       #0C1E10;
  --c-side-border:   #1A4828;
  --c-side-section:  #5A9868;
  --c-side-link:     #90C898;

  --c-accent:        #7AE890;
  --c-accent-text:   #071208;

  --c-h1:            #1B5E20;
  --c-h1-border:     #B8DFC0;
  --c-h2:            #2E7D32;
  --c-h2-border:     #C8EAC8;
  --c-h3:            #388E3C;

  --c-bg:            #F4FAF4;
  --c-text:          #0D2010;

  --c-th-bg:         #1B5E20;
  --c-th-text:       #E8F5E9;
  --c-td-border:     #B8DFC0;
  --c-tr-alt:        #EDF7EE;
  --c-tr-hover:      #D4EDDA;

  --c-code-bg:       #DFF0E0;
  --c-code-text:     #1B5E20;
  --c-pre-bg:        #071208;
  --c-pre-text:      #90C898;

  --c-callout-bg:    rgba(74,200,112,0.07);
  --c-callout-border:rgba(74,200,112,0.25);

  --c-foot-text:     #6A9F72;
}
```

---

## Typography

No web fonts. Uses the OS system font stack — renders natively on Windows, Mac, and Linux.

```css
/* All text */
font-family: 'Segoe UI', 'Trebuchet MS', Arial, Helvetica, sans-serif;

/* Code and pre blocks */
font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
```

| Element | Size | Weight | Notes |
|---|---|---|---|
| Body | 16px | 400 | `line-height: 1.7` |
| h1 | 26px | 700 | Theme h1 color + thin underline |
| h2 | 20px | 600 | Theme h2 color + thin underline |
| h3 | 17px | 600 | Theme h3 color, no decoration |
| h4–h6 | 15–13px | 600 | Theme h3 color |
| Sidebar links | 13.5px | 400 | White (`#FFFFFF`) — always white on dark chrome |
| Sidebar section labels | 9.5px | 700 | `--c-side-section` color, uppercase, `letter-spacing: 1px` |
| Top bar title | 15px | 500 | White (`#FFFFFF`) always |
| Top bar nav links | 13px | 600 | White (`#FFFFFF`) always |
| Version badge | 11px | 500 | `rgba(255,255,255,0.75)`, pill border |
| Copyright | 11.5px | 400 | `rgba(255,255,255,0.65)` |
| Code inline | 13px | 400 | Monospace, tinted bg |
| Code block | 13px | 400 | Monospace, dark bg matching topbar |
| Footer | 12.5px | 400 | `--c-foot-text` |

---

## Link Rules

| Context | Style | Rationale |
|---|---|---|
| Content body (`<a>`) | `color: #1565C0; text-decoration: underline` | Standard web hyperlink convention |
| Content visited | Same blue `#1565C0` | Prevents the default browser purple, which clashes with dark themes |
| Content hover | Darker blue `#0D3B8E`, still underlined | Feedback without color drama |
| Sidebar nav links | White (`#FFFFFF`), no underline | Navigation item, not a body link — white text on dark chrome |
| Sidebar nav hover | White text + subtle bg + 3px accent left border | Conquer 2026 / ezdocs pattern |
| Top bar nav links | Same as sidebar links | Unified chrome |
| Top bar nav hover | White text + subtle bg + 2px accent bottom border | Horizontal nav variant |
| Links inside section banners (dark bg) | `rgba(255,255,255,0.88)`, underlined | Must be readable on dark background |

---

## Page Structure

### Three-panel (frameset — legacy projects like GEM)

```
┌──────────────────────────────────────────────────────────┐
│  TOP BAR (top.htm) — 56px                               │
│  [GEM] [Build/version] Title  │  Nav links  │ Copyright │
│  bg: --c-topbar-bg             │             │           │
├──────────────────┬───────────────────────────────────────┤
│ SIDEBAR          │  CONTENT                              │
│ (toc.htm) 24%   │  (readme.htm) 76%                    │
│ bg: --c-side-bg  │  bg: --c-bg (light)                  │
│                  │                                       │
│ [Section label]  │  [dark banner — bg: --c-side-bg]     │
│   Nav link       │    h1 heading (white on dark)         │
│   Nav link       │  [dark banner ...]                    │
│   Nav link ◀▌    │                                       │
│   (hover: left   │  Body text, tables, code              │
│    accent bar)   │                                       │
│                  │  [footer — copyright]                 │
└──────────────────┴───────────────────────────────────────┘
```

The sidebar title strip uses `--c-topbar-bg` — same as the top bar — so the top-left corner reads as one unified dark header.

### Single-page (modern projects like ezdocs, conquer_2026, EdBarlowsStoredProcs)

```html
<body>                          <!-- bg: --c-bg -->
  <nav class="sidebar">         <!-- bg: --c-side-bg, left border -->
    <div class="sidebar-header"> <!-- bg: --c-topbar-bg -->
      <h1>Project Name</h1>
      <p>v1.0 — subtitle</p>
    </div>
    <div class="nav-section">SECTION</div>
    <a href="#anchor">Link text</a>
  </nav>
  <main>                        <!-- max-width: 860px, padding -->
    <h1>...</h1>
    ...
  </main>
</body>
```

---

## Section Divider Banners (Legacy HTML)

Legacy content files use `<TABLE BGCOLOR=#0066cc>` as section heading banners. The theme reskins these using `--c-side-bg` (sidebar color) so banners match the sidebar:

```css
table[bgcolor="#0066cc"] {
  background: var(--c-side-bg) !important;
  border: 1px solid var(--c-side-border) !important;
  border-radius: 4px;
  width: 100% !important;
  margin: 20px 0 12px 0 !important;
}
table[bgcolor="#0066cc"] h1,
table[bgcolor="#0066cc"] h2 {
  color: #FFFFFF !important;   /* CRITICAL: must be white on dark bg */
  border: none !important;
}
```

---

## Callout / Note Boxes

```html
<div class="gem-note">
  <strong>Note:</strong> important information here.
</div>
```

Or use a plain `<blockquote>` — both are styled identically:
- Background: `rgba(accent, 0.07)` tinted
- Left border: `4px solid --c-accent`
- Border: `1px solid rgba(accent, 0.25)`

---

## Implementation for a New Project

### Option A — Modern single-page doc (recommended for new projects)

1. Copy `gem/doc/styles/gem-base.css` to your project's `doc/styles/`.
2. Create `doc/styles/themes/` and copy the theme files you want.
3. In your build script, concatenate theme + base:
   ```bash
   cat doc/styles/themes/green.css doc/styles/gem-base.css > doc/styles/gem.css
   ```
4. Reference `gem.css` in your HTML:
   ```html
   <link rel="stylesheet" href="styles/gem.css">
   ```
5. Use `body` with no class for content pages. Classes `gem-topbar` and `gem-sidebar` are reserved for the navigation chrome.

### Option B — Legacy frameset project

Use `bin/build_documentation.sh` from the GEM project as a reference. It:
1. Generates `gem.css` from a theme file + base CSS.
2. Runs `bin/update_doc_theme.pl` to rebuild `top.htm`, `toc.htm`, update frameset heights, inject CSS + copyright footers into content files, and humanize CamelCase nav link text.

To port to a new project, copy both scripts and adjust the nav links in `process_top()`.

### Switching themes

```bash
./bin/build_documentation.sh --theme=green          # default
./bin/build_documentation.sh --theme=midnight
./bin/build_documentation.sh --theme=purple
./bin/build_documentation.sh --theme=midnight-green
./bin/build_documentation.sh --theme=mughal
./bin/build_documentation.sh --theme=rainforest
./bin/build_documentation.sh --theme=X --css-only   # rebuild CSS only, no HTML
```

---

## Reference Files

| File | Location | Purpose |
|---|---|---|
| `gem-base.css` | `gem/doc/styles/gem-base.css` | All structural CSS rules (no colors) |
| `themes/*.css` | `gem/doc/styles/themes/` | One file per theme — only `:root {}` variables |
| `gem.css` | `gem/doc/styles/gem.css` | Generated active theme (do not edit) |
| `build_documentation.sh` | `gem/bin/` | Build entry point |
| `update_doc_theme.pl` | `gem/bin/` | HTML processor (frameset projects) |
| `DOC_STANDARDS.md` | `gem/doc/DOC_STANDARDS.md` | GEM-specific build instructions |

---

## Copyright

Copyright notices appear in two places:
1. **Top bar** — extracted verbatim from the source `top.htm` file. Never modified by the build script.
2. **Page footer** — injected before `</body>` if not already present. Text is extracted from the page's own content, or falls back to `Copyright © 2026 Web Cloud Studio. All rights reserved.`

For new projects, put the copyright in the sidebar header or page footer as appropriate.

---

## What Not to Do

| ❌ Don't | ✓ Do instead |
|---|---|
| Dark text on dark background | Always verify: `--c-side-section` must be lighter than `--c-side-bg` |
| Purple visited links (`#6040a0`) | Keep `a:visited` the same blue as `a:link` |
| Gradient on top bar that differs from sidebar | Flat `--c-topbar-bg`, no gradient |
| Top bar background lighter than sidebar | Top bar = darkest shade; sidebar = slightly lighter |
| CamelCase nav text (`TheWin32Process`) | Run through humanizer or write with spaces from the start |
| Different link styles per theme | Links are always `#1565C0` blue + underlined in content |
| Font size chaos (mixing 8pt/16pt/12px) | Use the type scale above; body = 16px base |
