# Database

**Version:** 20260408 V1
**Description:** SQLite schema — market data, signals, configuration, and portfolio support

## market_data

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| ticker | TEXT | NOT NULL |
| asset_class | TEXT | e.g. 'equity_sector', 'fixed_income' |
| bucket | TEXT | e.g. 'Technology', 'Long Treasury' |
| date | DATE | NOT NULL |
| open | REAL | |
| high | REAL | |
| low | REAL | |
| close | REAL | NOT NULL |
| adj_close | REAL | NOT NULL |
| volume | INTEGER | NOT NULL |
| dollar_volume | REAL | computed: adj_close × volume |
| source | TEXT | 'yfinance' or 'fred' |
| created_at | TEXT | timestamp |

UNIQUE(ticker, date)

## macro_data

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| series_id | TEXT | FRED series ID, NOT NULL |
| indicator_name | TEXT | e.g. '10Y Treasury Yield' |
| date | DATE | NOT NULL |
| value | REAL | NOT NULL |
| source | TEXT | default 'fred' |
| created_at | TEXT | timestamp |

UNIQUE(series_id, date)

## asset_config

| Column | Type | Notes |
|--------|------|-------|
| ticker | TEXT PK | |
| asset_class | TEXT | NOT NULL |
| bucket | TEXT | NOT NULL |
| display_name | TEXT | NOT NULL |
| source | TEXT | 'yfinance' or 'fred' |
| is_active | INTEGER | boolean, default 1 |
| added_date | DATE | |

## signals

Stores only the top-ranked features after regression — not the full feature matrix. Used by the UI dashboard and alert engine.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| bucket | TEXT | NOT NULL |
| date | DATE | NOT NULL |
| feature_name | TEXT | e.g. 'close_roc_20', 'volume_ratio_10' |
| value | REAL | |
| created_at | TEXT | timestamp |

UNIQUE(bucket, date, feature_name)

## feature_importance

Results from the regression layer — updated after each regression run.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| feature_name | TEXT | transformation name |
| bucket | TEXT | asset class bucket; 'ALL' for cross-sectional |
| forward_horizon_days | INTEGER | 5, 10, 20, or 60 |
| coefficient | REAL | regression coefficient or RF importance score |
| hit_rate | REAL | fraction of times signal preceded correct direction |
| information_coefficient | REAL | rank correlation of signal vs forward return |
| rank | INTEGER | rank among all features for this bucket/horizon |
| computed_at | TEXT | timestamp |

UNIQUE(feature_name, bucket, forward_horizon_days)

## download_log

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| ticker | TEXT | NOT NULL |
| last_success | TEXT | timestamp |
| last_failure | TEXT | timestamp |
| row_count | INTEGER | rows in market_data for this ticker |
| status | TEXT | 'ok', 'warning', 'error' |

## target_weights

Managed via Portfolio web interface. Replaces static YAML for target allocations.

| Column | Type | Notes |
|--------|------|-------|
| bucket | TEXT PK | Asset class bucket name |
| target_pct | REAL | Target allocation 0.0–100.0; all rows must sum to 100 |
| notes | TEXT | Optional operator annotation |
| updated_at | TEXT | timestamp of last edit |

## Open Questions

- signals table storage: narrow (one row per signal_id) chosen for Phase 1 flexibility; may switch to wide table if query performance becomes an issue
