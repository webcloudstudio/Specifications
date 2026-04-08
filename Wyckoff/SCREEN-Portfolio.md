# Screen: Portfolio

**Route:** `/portfolio`
**Purpose:** Import holdings, view current allocation vs targets, manage target weights, and review proposed trades

## Layout

Three sections:

### 1. Holdings Import
- Upload area: drag-and-drop or path input for Fidelity positions CSV
- Mapping table: each holding → mapped bucket → current $ value → current weight %
- Unmapped holdings flagged for manual mapping (link to Settings for resolution)

### 2. Allocation View & Weight Editor
- Summary table: one row per bucket showing current % vs target % with drift and traffic-light coloring
- Bucket charts/KPIs inline (mini sparkline of Wyckoff phase history, current sell score)
- Editable target % column — operator adjusts values directly in table cells
- "Save Targets" button — persists to `target_weights` database table
- Target weights must sum to 100%; validation error shown if not

### 3. Proposed Trades
Generated after saving target weights. One row per bucket with non-zero drift:

| Column | Notes |
|--------|-------|
| Bucket | Asset class |
| Current $ | Sum of holdings in bucket |
| Current % | Current weight |
| Target % | Operator-defined (editable) |
| Drift | Current % − Target % |
| Proposed Action | "Sell $X" or "Buy $X" to reach target |
| Wyckoff Phase | Phase badge |
| Sell Score | Composite sell — context for timing |

**Note:** Proposed trades are advisory only — no broker integration. Operator executes manually.

## Open Questions

-
