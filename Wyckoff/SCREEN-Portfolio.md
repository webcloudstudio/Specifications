# Screen: Portfolio

**Route:** `/portfolio`
**Purpose:** Map operator's Fidelity holdings to asset class buckets, show drift from target weights, surface rebalancing actions

## Layout

- Upload area: drag-and-drop or path input for Fidelity positions CSV
- Mapping table: each holding → mapped bucket → current weight → target weight → drift (traffic-light coloring)
- Unmapped holdings flagged for manual mapping
- Rebalance table: one row per bucket (see columns)

## Rebalance Table Columns

| Column | Notes |
|--------|-------|
| Bucket | Asset class |
| Current $ | Sum of holdings mapped to this bucket |
| Current % | Current weight |
| Target % | From target_weights.yaml |
| Drift | Current % − Target % |
| Wyckoff Phase | Phase badge |
| Sell Score | Composite sell |
| Suggested Action | "Trim" if drift >+2% AND sell_score elevated; "Add" if drift <−2% AND buy_score elevated; "Hold" otherwise |

## Open Questions

- OQ6: Which Fidelity account types are in scope? (Taxable, IRA, 401k export formats differ)
