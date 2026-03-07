# Styling & Design System

Single stylesheet: `static/style.css`. Dark theme only. No light mode.

## CSS Custom Properties

```css
:root {
    --cc-bg: #1a1a2e;           /* Page background */
    --cc-surface: #16213e;       /* Card/row backgrounds */
    --cc-surface-hover: #1a2744; /* Row hover */
    --cc-border: #0f3460;        /* Borders, dividers */
    --cc-text: #e2e8f0;          /* Primary text */
    --cc-muted: #94a3b8;         /* Secondary text */
    --btn-local: #0073ea;        /* Local operation buttons */
    --btn-remote: #a25ddc;       /* Remote operation buttons */
    --btn-danger: #e44258;       /* Stop/delete buttons */
    --btn-success: #00c875;      /* Success states */
    --btn-service: #0073ea;      /* Service operation buttons */
    --btn-git: #808080;          /* Git operation buttons */
    --btn-callout: #a25ddc;      /* Link callout buttons */
    --btn-claude: #fdab3d;       /* CLAUDE.md badge */
}
```

## Component Classes

### Navigation (`cc-nav`)
- Background: surface color, bottom border
- Links: uppercase, 0.9rem, 600 weight, 3px bottom border on active (blue)
- Brand: 800 weight, 1.1rem

### Project Table
- `project-table`: border-spacing 0.35rem vertical
- `project-row`: surface background, 8px border-radius on first/last td, hover slides right 2px

### Operation Buttons (`op-btn`)
- Size: 0.75rem, 600 weight, padding 0.25rem 0.65rem
- Variants: `--local` (blue), `--remote` (purple), `--danger` (red), `--success` (green), `--ghost` (transparent), `--service` (blue), `--git` (gray), `--callout` (purple), `--claude` (orange)
- Hover: opacity 0.85, translateY(-1px)

### Pipeline Buttons (`pipeline-btn`)
- Size: 1rem, 600 weight, padding 1rem 1.5rem, min-width 140px
- Layout: flex-column (icon above subtitle)
- Variants: `--rebuild` (blue), `--preview` (green), `--push` (purple)
- `--running`: pulse animation

### Badges
- `workflow-badge`: 0.65rem, 700 weight, 6px radius, uppercase, inline color via `style="background:{color}"`
- `running-badge`: 0.6rem, green with pulse animation
- `badge-unpushed`: 0.7rem, danger color, rounded
- `badge-claude` / `op-btn--claude`: orange (#fdab3d), matches op-btn sizing

### Cards (`cc-card`)
- Background: surface, border: 1px border color, radius: 10px, padding: 1.5rem
- Header (`cc-card-header`): 0.85rem, 700 weight, uppercase, muted color, bottom border

### Forms (`cc-form`)
- Inputs: bg background, border color border, text color
- Focus: blue border, blue box-shadow
- Labels: muted, 0.8rem, 600 weight, uppercase

### Log Viewer
- `log-output`: dark terminal background (#0d1117), monospace, 0.78rem, max-height 450px
- `log-status-running`: green tinted, pulse animation
- `log-status-done`: muted tinted
- `log-waiting`: text pulse animation

### Animations
```css
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0, 200, 117, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(0, 200, 117, 0); }
}

@keyframes pulse-text {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
```

### Responsive
- `@media (max-width: 768px)`: reduced padding, smaller buttons

## Typography
- Primary font: Segoe UI, system-ui, -apple-system, sans-serif
- Monospace: Courier New, Consolas, monospace (logs, code, ports)

## External Dependencies (CDN)
- Bootstrap 5.3.3 CSS + JS Bundle
- HTMX 2.0.4
- Plotly (usage page only, loaded in usage_analyzer.py output)
