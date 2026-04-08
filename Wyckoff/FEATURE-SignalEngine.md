# Feature: Signal Engine

**Trigger:** Manual CLI (`python scripts/compute_signals.py --date <date>` or `--backfill`) or post-data-download

## Design Philosophy

The signal engine generates a **wide feature matrix** — hundreds of candidate metrics per (bucket, date) row — and then uses regression to discover which features actually predict asset class moves. Specific metrics are not pre-specified; the framework is generic and applies the same transformation set to any input data. Phase 1 goal is feature discovery and selection, not a pre-tuned model.

## Sequence

1. Load market_data and macro_data for the target date range
2. Per bucket, apply all transformation types over all configured windows (see below) → wide feature matrix
3. Compute cross-sectional features (rankings across all buckets on each date)
4. Store feature matrix (see Storage note below)
5. Run regression against forward-return targets to score each feature's predictive value
6. Write feature importance ranking to `feature_importance` table
7. Apply configurable alert thresholds against high-importance features; write alerts

## Feature Transformation Types

Applied systematically to each input field (close, volume, dollar_volume, high, low) over all configured windows:

| Transformation | Description | Example columns |
|---------------|-------------|-----------------|
| Simple moving average | SMA(field, n) | close_sma_5, close_sma_20 |
| Exponential moving average | EMA(field, n) | close_ema_10, close_ema_50 |
| Rolling std deviation | std(field, n) / mean(field, n) | close_cv_20 |
| Rolling min / max | min/max(field, n) | close_min_20, close_max_52w |
| Rate of change | (field[t] - field[t-n]) / field[t-n] | close_roc_5, close_roc_20 |
| Ratio to rolling avg | field[t] / SMA(field, n) | volume_ratio_20 |
| Up-day / down-day split | sum(field on up-days, n) / sum(field, n) | volume_upday_ratio_10 |
| Price range position | (close - min_n) / (max_n - min_n) | range_position_20 |
| Boolean threshold | close > SMA(n) ? 1 : 0 | above_sma_50 |

**Configured windows (default):** 3, 5, 10, 20, 50, 100, 200 days

## Cross-Sectional Features

Computed across all buckets on each date (require all buckets to be computed first):

- Percentile rank of each feature vs all other buckets on that date
- Dollar volume share: bucket dollar_volume / sum(all buckets)
- Return vs benchmark (SPY): bucket_roc_n - spy_roc_n

## Macro Overlay Features

Joined from macro_data (FRED) for each date — not transformed, used directly:

- Yield curve slope (10Y − 2Y)
- Fed Funds Rate
- CPI YoY change (computed)
- VIX level (from ^VIX market data)

## Regression Layer

Forward-return targets:
- `fwd_5d`, `fwd_10d`, `fwd_20d`, `fwd_60d` — percentage return n days forward

Methods (applied per asset class and cross-sectionally):
- OLS with LASSO regularization — linear predictors, sparse feature selection
- Logistic regression — binary target (up/down > 2% threshold)
- Random forest feature importance — non-linear, identifies interactions

Walk-forward validation only: train on oldest 3 years, validate on year 4, test on year 5. No look-ahead.

Output: feature importance ranking with coefficient, hit rate, and information coefficient per feature per forward horizon.

## Storage

**Feature matrix:** Parquet file per bucket (`features/<bucket>.parquet`) — columnar format, fast for pandas/sklearn. Not in SQLite — too wide for efficient row-based storage.

**Feature importance:** `feature_importance` table in SQLite (see DATABASE.md).

**Selected signals:** After regression, top-N features per bucket written back to `signals` table for use by the UI and alert engine.

## Reads

- market_data
- macro_data

## Writes

- features/<bucket>.parquet (feature matrix per bucket)
- feature_importance table
- signals table (top-N selected features per bucket/date)
- alerts (new triggers only)

## Open Questions

- Window list is configurable — default set (3,5,10,20,50,100,200) is the starting point; operator can extend
- Top-N features to promote to signals table: TBD after first regression run
