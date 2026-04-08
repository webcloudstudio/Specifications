# Functionality

**Version:** 20260408 V2
**Description:** What the Wyckoff Accumulator does

## Features

### Data Pipeline
Downloads and caches end-of-day price/volume data for asset class buckets plus FRED macro indicators. Phase 1 universe: 11 equity sector ETFs (SPDR XL*). Phase 2 expands to full ~40-bucket universe (bonds, commodities, forex, crypto, alternatives). Backfills 5 years on first run; incremental updates run daily on a schedule. All data stored in local SQLite. Validation report after each run. FRED API key read from `.api` file (`FRED_API_KEY`).

### Signal Engine
Computes ~200–300 signals per bucket per day across five families:
- **Volume analytics (V)** — relative volume, buying/selling pressure, volume divergence, climax, dry-up
- **Price momentum (P)** — rate of change (5/20/60/120d), SMA crossovers (20/50/200), ATR, range position
- **Wyckoff phase detection (W)** — state machine classifying each bucket: accumulation, markup, distribution, or markdown; plus event detection (spring, upthrust, test, SOS, SOW)
- **Cross-asset relative strength (R)** — performance vs SPY, dollar flow share, percentile rankings across all buckets
- **Macro/regime context (M)** — yield curve slope, VIX percentile, gold/TLT ratios, dollar trend, credit spread

### Composite Scoring
Weighted composite sell score and buy score derived from signal families. Sell signals weighted higher and thresholds tuned more sensitive — detecting distribution before it's obvious is the operator's stated priority.

### Portfolio Integration
Parses Fidelity positions CSV (`Portfolio_Positions_Apr-08-2026.csv` format), maps holdings to asset class buckets (config file + yfinance fallback), and computes current weight per bucket as a percentage of total portfolio value.

### Target Weight Management
Operator sets and adjusts target allocations per asset class bucket via the Portfolio web interface — reviewing charts and KPIs before committing changes. Target weights stored in the database (not YAML). Weight edits generate a proposed trade list showing dollar amounts to buy/sell per bucket to reach target.

### Alert Generation
Triggers when composite scores cross configurable thresholds, Wyckoff phase changes, relative volume spikes (V004 > 2.0), or flow rank shifts sharply (>20 percentile points in 5 days). Stored chronologically, filterable by type and asset class.

### Backtesting
Validates composite scores against historical forward returns (5/10/20/60d horizons). Outputs hit rates and information coefficients. Used to tune signal weights. Walk-forward only — no look-ahead.

## Open Questions

-
