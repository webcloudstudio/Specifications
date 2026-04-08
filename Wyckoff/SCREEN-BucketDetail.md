# Screen: Bucket Detail

**Route:** `/bucket/<bucket_name>`
**Purpose:** Deep dive into a single asset class bucket — price/volume chart with Wyckoff annotations and full signal history

## Layout

- Header: bucket name, current phase badge, phase duration (days in current phase)
- Chart area (Plotly, two panels):
  - Top panel: price line/candlestick + SMA20/SMA50/SMA200 overlays + Wyckoff event markers (springs, upthrusts, tests, SOS/SOW as arrows/icons) + phase period shading (color by phase)
  - Bottom panel: volume bars colored by up/down day
- Signal table: all current signal values for this bucket, grouped by family (V, P, W, R, M)
- History table: last 60 days of composite sell/buy scores

## Interactions

- Date range selector: HTMX-driven, re-renders chart panel only
- Toggle overlays: SMAs on/off, Wyckoff annotations on/off
- History table: sortable via DataTables.js

## Open Questions

-
