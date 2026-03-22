# Documentation Branding Standards

**Version:** 20260322 V3
**Description:** Color variables, typography, and layout standards for project documentation
**Reference implementation:** `Specifications/doc/` (Prototyper — process-based, slate theme)

---

## Design Philosophy

Documentation uses a **dark chrome / light content** split:

- **Sidebar** (220px) — dark background, white text. Always dark.
- **Content area** — warm off-white background (`#FAFAF8`), dark text. Optimised for reading.
- **Sidebar header** — slightly darker than the sidebar body; reads as one continuous dark panel.
- **Navigation links** — no underline. Hover shows a 3px colored left border and subtle background lift.
- **Content hyperlinks** — standard blue `#1565C0`, always underlined. Web convention; not theme-overridden.

---

## Default Theme: Slate

The default and reference theme. Charcoal sidebar, teal accent, warm off-white content.

```css
/* Theme: Slate — charcoal sidebar, warm cream content, teal accent */
:root {
  /* Sidebar — neutral charcoal */
  --c-topbar-bg:     #1A1D23;   /* sidebar header (darkest) */
  --c-side-bg:       #22262E;   /* sidebar body */
  --c-side-border:   #363B44;   /* chrome/content divider, scrollbar */
  --c-side-section:  #8A8F9A;   /* muted section label text (uppercase, 9px) */
  --c-side-link:     #FFFFFF;   /* sidebar link text — always white */

  /* Accent — warm teal */
  --c-accent:        #2CB67D;   /* hover border, arrows, callout borders, active indicator */
  --c-accent-text:   #0E1012;   /* text on accent-colored elements */

  /* Content headings (on light bg) */
  --c-h1:            #1E2328;
  --c-h1-border:     #D0D4DA;
  --c-h2:            #2E3640;   /* also used as dark banner background for h2 in markdown */
  --c-h2-border:     #DDE0E5;
  --c-h3:            #505A68;

  /* Content area */
  --c-bg:            #FAFAF8;   /* warm off-white — not pure white */
  --c-text:          #2A2E35;   /* near-black body text */

  /* Tables */
  --c-th-bg:         #2E3640;
  --c-th-text:       #F0F1F3;
  --c-td-border:     #D5D8DE;
  --c-tr-alt:        #F3F4F2;
  --c-tr-hover:      #E8EAE6;

  /* Code */
  --c-code-bg:       #EDEEE8;   /* inline code background */
  --c-code-text:     #2E3640;   /* inline code text */
  --c-pre-bg:        #1A1D23;   /* code block — matches topbar-bg */
  --c-pre-text:      #C0C4CC;   /* code block text */

  /* Callout / blockquote */
  --c-callout-bg:    rgba(44,182,125,0.06);
  --c-callout-border:rgba(44,182,125,0.2);

  /* Footer */
  --c-foot-text:     #8A8F9A;
}
```

---

## Available Themes

| Theme | Character | Sidebar bg | Accent |
|-------|-----------|------------|--------|
| `slate` *(default)* | Charcoal + teal | `#22262E` | `#2CB67D` |
| `green` | Forest green | `#0C1E10` | `#7AE890` |
| `midnight` | Corporate navy | `#0D1B3E` | `#5B8DEF` |
| `purple` | Royal purple | `#2A1A4E` | `#B084F0` |
| `midnight-green` | Deep teal | `#002B30` | `#2ECAD6` |
| `mughal` | Rich forest | `#1E3A1E` | `#6ECF6E` |
| `rainforest` | Warm teal-green | `#003D32` | `#3DD6A4` |

All themes follow the same variable contract. To create a new theme, copy the slate block
above and replace values.

---

## Typography

No web fonts. OS system font stack — renders natively on Windows, Mac, and Linux.

```css
font-family: 'Segoe UI', 'Trebuchet MS', Arial, Helvetica, sans-serif;  /* all text */
font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;        /* code/pre */
```

| Element | Size | Weight | Notes |
|---------|------|--------|-------|
| Body | **14px** | 400 | `line-height: 1.65` |
| h1 (markdown) | 22px | 700 | `var(--c-accent)` color + 2px underline |
| h2 (markdown) | 14px | 700 | Dark banner: `var(--c-side-bg)` bg, 3px accent left border |
| h3 (markdown) | 14px | 600 | `var(--c-h3)` color, no decoration |
| Sidebar primary links | 13px | 400 | White, `padding: 3px 16px` |
| Sidebar sub-links | 11px | 400 | `rgba(255,255,255,.8)`, `padding: 2px 16px 2px 28px` |
| Sidebar section labels | 9px | 700 | `var(--c-side-section)`, uppercase, `letter-spacing: 1px` |
| Code inline | 12.5px | 400 | Monospace, `var(--c-code-bg)` background |
| Code block | 12.5px | 400 | Monospace, `var(--c-pre-bg)` background |
| Workflow box label | 12px | 700 | White |
| Workflow box script | 10px | 400 | White, monospace |
| Workflow box path | 9.5px | 400 | White, monospace |

---

## Page Structure: Single-Page Sidebar Layout

The standard layout for all new projects. Used by Prototyper (process-based) and all
new documentation builds.

```html
<body>                              <!-- bg: --c-bg, display:flex, height:100vh -->
  <nav class="sidebar">             <!-- width:220px, bg:--c-side-bg, overflow-y:auto -->
    <div class="sidebar-header">    <!-- bg:--c-topbar-bg, logo image + project name -->
    </div>
    <div class="nav-section">WORKFLOW</div>
    <a class="sn" onclick="...">Step 1 — Setup</a>
    <a class="sn-sub" onclick="...">setup.sh</a>
    <div class="nav-sep"></div>
    <div class="nav-section">CURRENT PROJECTS</div>
    <a class="sn" onclick="...">GAME</a>
  </nav>
  <main>                            <!-- flex:1, overflow-y:auto, padding:28px 36px 48px -->
    <!-- content sections, shown/hidden via JS -->
  </main>
</body>
```

Sidebar header uses `--c-topbar-bg` (darker than sidebar body) so it reads as a unified
dark panel. Logo is a `<img>` (100px wide), not a text badge.

---

## Workflow Diagram (Process-Based Projects)

For projects without a web server, the primary content is a workflow pipeline diagram.
CSS classes (all in the inline `<style>` block of the generated page):

```css
.wf-diagram  — flex column, gap 2px, margin-bottom 20px
.wf-row      — flex row, left-aligned, no wrap
.wf-box      — dark sidebar-bg box: padding 5px 10px, border-radius 4px, centered
.wf-terminal — green terminal box: border-color --c-accent, background #0a5c38
.wf-label    — 12px bold white text
.wf-script   — 10px white monospace (script name)
.wf-path     — 9.5px white monospace (path)
.wf-arr      — right arrow (→), 22px bold, --c-accent color, padding 0 6px
```

Two independent rows, both left-aligned, no connecting arrows between rows.

---

## CSS File Assembly

```bash
# Built at documentation build time — do not edit spec.css directly
cat doc/styles/themes/slate.css doc/styles/spec-base.css > doc/styles/spec.css
```

| File | Location | Edit? |
|------|----------|-------|
| `spec.css` | `doc/styles/spec.css` | Never — generated |
| `slate.css` (or other theme) | `doc/styles/themes/` | Yes — theme colors only |
| `spec-base.css` | `doc/styles/` | Rarely — structural CSS, no colors |

For a new project: copy `doc/styles/` from `Specifications/doc/styles/` and choose a theme.

---

## Logo / Sidebar Header

Two supported formats — choose based on available assets:

**Full image header** (preferred when a project image exists):
```html
<div class="sidebar-header" onclick="show('workflow')">
  <img src="images/prototyper.webp" alt="Prototyper" style="width:100px;height:75px;">
  <h1>Project<br>Prototyper</h1>
</div>
```
Logo image: `doc/images/<project>.webp`, 100×75px display, `object-fit:contain`.
Generate with `bin/generate_image.py` (see `doc/DOC-CREATE-IMAGE.md`).

**Compact icon header** (for smaller projects or when a full image is unavailable):
```html
<div class="sidebar-header" onclick="show('workflow')">
  <span class="sidebar-icon">⚔️</span>
  <h1>Conquer<br>2026</h1>
</div>
```
```css
.sidebar-icon { font-size: 28px; line-height: 1; flex-shrink: 0; }
.sidebar-header h1 { font-size: 14px; font-weight: 700; color: #fff; line-height: 1.25; }
```
Emoji icons work well and render crisply at sidebar scale. Use the compact format
when a project image hasn't been generated yet — it is not a lesser choice.

---

## Link Rules

| Context | Style |
|---------|-------|
| Content body `<a>` | `color: #1565C0; text-decoration: underline` |
| Content visited | Same blue `#1565C0` — no purple |
| Sidebar nav | White, no underline; hover: subtle bg + 3px `--c-accent` left border |

---

## Callout Blocks

Callouts use the accent color for a left border and a very faint tinted background.
The font stays the same as body text — but a **label** in monospace adds technical clarity:

```html
<blockquote class="md">
  <code>NOTE</code> This is an important callout.
</blockquote>
```

Or with an explicit callout class (preferred for standalone HTML pages):
```html
<div class="callout">
  <span class="callout-label">NOTE</span>
  This is an important callout with a distinct label.
</div>
```
```css
.callout { border-left: 3px solid var(--c-accent); padding: 8px 14px;
  margin: 10px 0; background: var(--c-callout-bg); border-radius: 0 4px 4px 0; }
.callout-label { font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 11px; font-weight: 700; color: var(--c-accent);
  text-transform: uppercase; letter-spacing: .5px; display: block; margin-bottom: 3px; }
```

Callout variants: add `callout--warn` (amber border/bg) or `callout--danger` (red) for urgency.

---

## Global CSS Architecture

```
doc/styles/
  themes/
    slate.css          ← color variables only (edit this to retheme)
    midnight.css
    purple.css
    …
  spec-base.css        ← all structural CSS, zero colors (rarely edit)
  spec.css             ← GENERATED: themes/<active>.css + spec-base.css concatenated
```

**Rule:** Change colors by editing the theme file and rebuilding — never touch `spec.css`.
One command updates all colors across the entire documentation:
```bash
bin/build_documentation.sh --theme=midnight
```

All themes enforce the same two-zone rule: **right/content is always light** (`#FAFAF8`),
**left/sidebar is always dark** but never pure black (minimum `#22262E` charcoal).
This constraint is structural — `--c-bg` lives in `spec-base.css`, not in themes,
ensuring no theme can accidentally put dark text on a dark content background.

---

## Multi-Page Documentation

For projects with many pages (e.g., a game with separate guides per topic):

- Each page links `<link rel="stylesheet" href="style.css">` pointing to `spec.css`
- Sidebar nav uses `<a href="page.html">` standard links (not JS `show()`)
- All pages share the same sidebar markup — include via server-side template or duplicate
- Active page: add `class="active"` to the current nav link
- `doc/` folder: `index.html` is the landing page; other pages sit beside it

Single shared `spec.css` means one theme change re-styles the entire multi-page set.

---

## What Not to Do

| Don't | Do instead |
|-------|------------|
| Dark content area (`--c-bg` dark) | Content is always light — `#FAFAF8` or equivalent |
| Pure black sidebar (`#000` or `#0d1117`) | Minimum charcoal — `#22262E`; black reads as broken |
| Dark text on dark sidebar bg | `--c-side-section` must be lighter than `--c-side-bg` |
| Purple visited links | Keep `a:visited` the same blue as `a:link` |
| Arrows connecting separate workflow rows | Two independent left-to-right rows, no DOWN arrow |
| Expand/collapse toggles for script details | Always show details inline |
| Relative `../` paths escaping `doc/` | Copy project viewers into `doc/projects/` at build time |
| Edit `spec.css` directly | Edit the theme file and rebuild |
| `docs/` (plural) directory | Use `doc/` (singular) — the platform standard |
