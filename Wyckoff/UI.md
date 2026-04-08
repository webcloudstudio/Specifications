# UI Standards

**Version:** 20260408 V1
**Description:** Shared UI patterns across all screens

## Theme

| Component | Technology | Notes |
|-----------|-----------|-------|
| CSS framework | Tailwind CSS (CDN) | Utility-first; no build step |
| Charts | Plotly.js (CDN) | Interactive price/volume charts, heatmaps |
| Tables | DataTables.js (CDN) | Sortable, filterable |
| Dynamic updates | HTMX (CDN) | Degrades to full page load without JS |
| Server | Flask + Jinja2 | Localhost only; no authentication |

## Navigation

Top nav bar: **Dashboard | Flows | Portfolio | Alerts | Settings**. Active page highlighted. Data freshness timestamp in header — red if >24 hours stale.

## Shared Components

**Phase badge** — colored pill for Wyckoff phase:
- Accumulation: green
- Markup: blue
- Distribution: orange
- Markdown: red
- Undetermined: gray

**Score cell** — heat-colored table cell (0–1 scale). Sell score: red gradient. Buy score: green gradient.

**Relative volume indicator** — numeric with background color: >2.0 = red, 1.2–2.0 = yellow, <1.2 = neutral.

## Open Questions

-
