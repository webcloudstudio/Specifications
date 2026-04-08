# Screen: Dashboard

**Route:** `/`
**Purpose:** At-a-glance view of all asset class buckets — current Wyckoff phase and composite scores

## Layout

- Header: "Wyckoff Accumulator" + last data update timestamp
- Summary bar: count of buckets per phase (e.g. "3 Accumulation | 12 Markup | 2 Distribution | 1 Markdown | 22 Undetermined")
- Main table: one row per asset class bucket

## Table Columns

| Column | Signal | Notes |
|--------|--------|-------|
| Bucket | asset_config.bucket | Clickable → /bucket/<bucket_name> |
| Asset Class | asset_config.asset_class | |
| Close | market_data.adj_close | Latest |
| Chg 1D | roc_1d | % |
| Chg 20D | P002 (roc_20d) | % |
| Rel Volume | V004 (rel_volume_20d) | Color coded |
| Buy Pressure | V007 (up_volume_ratio_10d) | |
| Wyckoff Phase | W001 | Phase badge component |
| Phase Conf. | W002 | 0.0–1.0 |
| Sell Score | composite sell | Heat colored; default sort descending |
| Buy Score | composite buy | Heat colored |
| Flow Rank | R007 | Percentile |

## Interactions

- Default sort: Sell Score descending
- Column headers: sortable via DataTables.js
- Row click: navigate to /bucket/<bucket_name>

## Open Questions

-
