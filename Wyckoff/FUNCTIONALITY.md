# Functionality

**Version:** 20260408 V1
**Description:** What the Wyckoff Accumulator does

## Features

### Data Pipeline
Downloads and caches end-of-day price/volume data for ~40 asset class buckets (11 equity sectors, 6 fixed income, 8 commodities, 5 forex, 3 crypto, 3 alternatives) plus FRED macro indicators. Backfills 5 years on first run; incremental updates thereafter. Data stored in local SQLite. Validation report after each run.

### Signal Engine
Computes ~200–300 signals per bucket per day across five families:
- **Volume analytics (V)** — relative volume, buying/selling pressure, volume divergence, climax, dry-up
- **Price momentum (P)** — rate of change (5/20/60/120d), SMA crossovers (20/50/200), ATR, range position
- **Wyckoff phase detection (W)** — state machine classifying each bucket: accumulation, markup, distribution, or markdown; plus event detection (spring, upthrust, test, SOS, SOW)
- **Cross-asset relative strength (R)** — performance vs SPY, dollar flow share, percentile rankings across all buckets
- **Macro/regime context (M)** — yield curve slope, VIX percentile, gold/TLT ratios, dollar trend, credit spread

### Composite Scoring
Weighted composite sell score and buy score derived from signal families. Sell signals weighted higher and thresholds tuned more sensitive — detecting distribution before it's obvious is the operator's stated priority.

### Backtesting
Validates composite scores against historical forward returns (5/10/20/60d horizons). Outputs hit rates and information coefficients per asset class. Used to tune signal weights. Walk-forward only — no look-ahead.

### Portfolio Integration
Parses Fidelity positions CSV, maps holdings to asset class buckets (config file + yfinance fallback), computes drift vs operator-defined target weights, and generates rebalancing suggestions combining drift magnitude with Wyckoff phase and sell score.

### Alert Generation
Triggers when composite scores cross configurable thresholds, Wyckoff phase changes, relative volume spikes (V004 > 2.0), or flow rank shifts sharply (>20 percentile points in 5 days). Stored chronologically, filterable by type and asset class.

## Open Questions

- OQ1: Which sub-industry ETFs should be prioritized in Phase 2 — operator's 6–7 concentrated industries?
- OQ3: Target weights per asset class — placeholder is equal weight until operator defines
- OQ4: How frequently will the operator run data updates? (Placeholder: daily, manual trigger)
- OQ5: Does the operator have a FRED API key? (Register during setup if not)
- OQ6: Which Fidelity account types are in scope? (Placeholder: single account CSV)
