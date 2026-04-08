# Functionality

**Version:** 20260408 V2
**Description:** What the Wyckoff Accumulator does

## Features

### Data Pipeline
Downloads and caches end-of-day price/volume data for asset class buckets plus FRED macro indicators. Phase 1 universe: 11 equity sector ETFs (SPDR XL*). Phase 2 expands to full ~40-bucket universe (bonds, commodities, forex, crypto, alternatives). Backfills 5 years on first run; incremental updates run daily on a schedule. All data stored in local SQLite. Validation report after each run. FRED API key read from `.api` file (`FRED_API_KEY`).

### Signal Engine
Generates a wide feature matrix — hundreds of candidate metrics per (bucket, date) row — by applying systematic transformations (rolling averages, rate-of-change, volume ratios, range position, boolean thresholds) over configurable window lengths (3, 5, 10, 20, 50, 100, 200 days) to raw OHLCV data. Cross-sectional features (percentile rankings across all buckets on each date) and FRED macro indicators are appended. The specific metrics that matter are determined empirically, not pre-specified.

### Feature Selection & Regression
Runs regression (LASSO, logistic, random forest) against forward-return targets (5, 10, 20, 60 days) to identify which features have genuine predictive signal. Walk-forward validation only — no look-ahead. Output is a feature importance ranking. Phase 1 goal is discovery: which transformations and windows actually predict asset class moves. Top-ranked features are promoted to the signals table and used for alerting and the dashboard.

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
