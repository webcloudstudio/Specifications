# Wyckoff Accumulator — Project Plan

**Author:** Claude Opus (project analysis) for Ed Barlow
**Date:** 2026-04-08
**Version:** 1.0
**Target Location:** `/mnt/c/Users/barlo/projects/WyckoffAccumulator/`

---

## Executive Summary

The Wyckoff Accumulator is a personal portfolio intelligence system that detects institutional money flows across asset classes using volume-price analysis rooted in Wyckoff methodology. The system pairs quantitative signals with the operator's own macro/political judgment to generate rebalancing guidance — with an emphasis on **sell signals**, which are behaviorally harder to act on.

Phase 1 delivers a working system on free data covering ~40 asset class buckets (sector ETFs, bond proxies, commodities futures, forex, crypto). Phase 2 expands to paid data feeds, options flow, and sub-industry granularity.

The system is designed to be built incrementally in Claude Code using a Python/Flask stack.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [SPEC-001: Data Download & Pipeline](#2-spec-001-data-download--pipeline)
3. [SPEC-002: Signal Generation & Analysis Engine](#3-spec-002-signal-generation--analysis-engine)
4. [SPEC-003: Flask User Interface](#4-spec-003-flask-user-interface)
5. [SPEC-004: Portfolio Integration](#5-spec-004-portfolio-integration)
6. [Phase 1 Build Sequence](#6-phase-1-build-sequence)
7. [Phase 2 Roadmap](#7-phase-2-roadmap)
8. [Technology Requirements](#8-technology-requirements)
9. [Open Questions & Risks](#9-open-questions--risks)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    WYCKOFF ACCUMULATOR                   │
├─────────────┬──────────────┬──────────────┬─────────────┤
│  DATA LAYER │ SIGNAL LAYER │   UI LAYER   │  PORTFOLIO  │
│             │              │              │   LAYER     │
│ yfinance    │ Wyckoff      │ Flask app    │ Fidelity    │
│ FRED API    │ phase detect │ Dashboards   │ CSV import  │
│ CSV cache   │ Volume       │ Signal table │ Holdings    │
│ SQLite DB   │ analytics    │ Charts       │ mapping     │
│             │ Regression   │ Alerts       │ Drift calc  │
│             │ engine       │              │             │
└─────────────┴──────────────┴──────────────┴─────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    Nightly ETL    Feature store   localhost:5000   Rebalance
    (cron/manual)  (SQLite)        (browser)        report
```

### Design Principles

1. **Offline-first.** All data is downloaded and cached locally. The system works without a live connection after initial data pull.
2. **Batch not streaming.** End-of-day data only. No intraday, no websockets, no real-time complexity.
3. **Opinionated defaults.** Ship with sensible Wyckoff parameters. Tuning comes later.
4. **Sell-signal priority.** Every scoring and alerting mechanism weights distribution/markdown detection higher than accumulation/markup detection.
5. **Human-in-the-loop.** The system advises. Ed decides. No auto-trading, no broker integration.

---

## 2. SPEC-001: Data Download & Pipeline

### 2.1 Purpose

Download, normalize, and store end-of-day price/volume data for ~40 asset class buckets plus historical backfill. All data lands in a local SQLite database with a consistent schema regardless of source.

### 2.2 Asset Class Universe (Phase 1)

The following instruments serve as **proxies** for asset class buckets. Each maps to exactly one asset class. The operator can add/remove instruments via a configuration file.

#### 2.2.1 Equity Sectors (11 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| Technology | XLK | Technology Select Sector SPDR | yfinance |
| Healthcare | XLV | Health Care Select Sector SPDR | yfinance |
| Financials | XLF | Financial Select Sector SPDR | yfinance |
| Consumer Discretionary | XLY | Consumer Discretionary Select Sector SPDR | yfinance |
| Consumer Staples | XLP | Consumer Staples Select Sector SPDR | yfinance |
| Energy | XLE | Energy Select Sector SPDR | yfinance |
| Industrials | XLI | Industrial Select Sector SPDR | yfinance |
| Materials | XLB | Materials Select Sector SPDR | yfinance |
| Utilities | XLU | Utilities Select Sector SPDR | yfinance |
| Real Estate | XLRE | Real Estate Select Sector SPDR | yfinance |
| Communication Services | XLC | Communication Services Select Sector SPDR | yfinance |

#### 2.2.2 Fixed Income (6 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| Long Treasury | TLT | iShares 20+ Year Treasury Bond | yfinance |
| Mid Treasury | IEF | iShares 7-10 Year Treasury Bond | yfinance |
| Short Treasury | SHY | iShares 1-3 Year Treasury Bond | yfinance |
| Investment Grade Corporate | LQD | iShares Investment Grade Corporate Bond | yfinance |
| High Yield Corporate | HYG | iShares High Yield Corporate Bond | yfinance |
| TIPS (Inflation Protected) | TIP | iShares TIPS Bond | yfinance |

#### 2.2.3 Commodities (8 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| Gold | GC=F | Gold Futures | yfinance |
| Silver | SI=F | Silver Futures | yfinance |
| Crude Oil (WTI) | CL=F | Crude Oil Futures | yfinance |
| Natural Gas | NG=F | Natural Gas Futures | yfinance |
| Copper | HG=F | Copper Futures | yfinance |
| Corn | ZC=F | Corn Futures | yfinance |
| Soybeans | ZS=F | Soybean Futures | yfinance |
| Broad Commodities | DJP | iPath Bloomberg Commodity ETN | yfinance |

#### 2.2.4 Forex (5 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| US Dollar Index | DX-Y.NYB | US Dollar Index | yfinance |
| Euro/USD | EURUSD=X | EUR/USD | yfinance |
| Yen/USD | JPY=X | USD/JPY | yfinance |
| Gold/USD (spot) | GLD | SPDR Gold Shares | yfinance |
| Emerging Markets FX | CEW | WisdomTree Emerging Currency Strategy | yfinance |

#### 2.2.5 Crypto (3 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| Bitcoin | BTC-USD | Bitcoin USD | yfinance |
| Ethereum | ETH-USD | Ethereum USD | yfinance |
| Broad Crypto | BITW | Bitwise 10 Crypto Index Fund | yfinance |

#### 2.2.6 Benchmarks (not tradeable — used as reference)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| Broad US Equity | SPY | SPDR S&P 500 ETF | yfinance |

**Note:** SPY is required by Family 4 (Relative Strength) signals. It is not an asset class bucket for trading purposes.

#### 2.2.7 Alternatives (3 buckets)

| Bucket | Proxy Ticker | Name | Source |
|--------|-------------|------|--------|
| REITs | VNQ | Vanguard Real Estate ETF | yfinance |
| Volatility | ^VIX | CBOE Volatility Index | yfinance |
| Private Equity proxy | PSP | Invesco Global Listed Private Equity | yfinance |

#### 2.2.8 Macro Indicators (from FRED — supplementary, not tradeable)

| Indicator | FRED Series ID | Frequency |
|-----------|---------------|-----------|
| Fed Funds Rate | FEDFUNDS | Monthly |
| 10Y Treasury Yield | DGS10 | Daily |
| 2Y Treasury Yield | DGS2 | Daily |
| 10Y-2Y Spread | T10Y2Y | Daily |
| CPI (Urban) | CPIAUCSL | Monthly |
| Initial Jobless Claims | ICSA | Weekly |
| M2 Money Supply | M2SL | Monthly |

### 2.3 Data Schema

All market data normalizes to a single table:

```sql
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    asset_class TEXT NOT NULL,       -- e.g. 'equity_sector'
    bucket TEXT NOT NULL,            -- e.g. 'Technology'
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL NOT NULL,
    adj_close REAL NOT NULL,
    volume BIGINT NOT NULL,
    dollar_volume REAL,             -- computed: adj_close * volume
    source TEXT NOT NULL,            -- 'yfinance' or 'fred'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

CREATE INDEX idx_market_data_bucket_date ON market_data(bucket, date);
CREATE INDEX idx_market_data_ticker_date ON market_data(ticker, date);
CREATE INDEX idx_market_data_date ON market_data(date);
```

FRED macro data goes to a separate table:

```sql
CREATE TABLE macro_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id TEXT NOT NULL,
    indicator_name TEXT NOT NULL,
    date DATE NOT NULL,
    value REAL NOT NULL,
    source TEXT DEFAULT 'fred',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id, date)
);
```

Asset class configuration is stored as:

```sql
CREATE TABLE asset_config (
    ticker TEXT PRIMARY KEY,
    asset_class TEXT NOT NULL,
    bucket TEXT NOT NULL,
    display_name TEXT NOT NULL,
    source TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    added_date DATE DEFAULT CURRENT_DATE
);
```

### 2.4 Download Behavior

#### 2.4.1 Initial Backfill

On first run, download **5 years** of daily history for all configured tickers. yfinance supports this in a single call per ticker with `period="5y"`. For ~40 tickers this completes in under 2 minutes.

**Critical implementation detail:** Use `yf.download(tickers_list, period="5y", group_by="ticker", threads=True)` to batch-download all tickers in a single API call. This is dramatically faster than per-ticker calls and avoids rate limiting.

#### 2.4.2 Daily Incremental Update

On subsequent runs, download only the delta since the last stored date. Use `start=last_date + 1 day`.

#### 2.4.3 FRED Data

Use the `fredapi` Python package. Requires a free API key from https://fred.stlouisfed.org/docs/api/api_key.html (free, instant registration). Backfill 5 years, then incremental.

#### 2.4.4 Error Handling

- If a ticker fails to download, log the error and continue with remaining tickers. Do not abort the batch.
- Store download metadata (last success, last failure, row count) in a `download_log` table.
- yfinance occasionally returns partial data or NaN rows. Drop rows where `close` or `volume` is null/NaN.
- If a ticker returns zero rows on a non-holiday weekday, flag it for manual review.

#### 2.4.5 Configuration File

`config/universe.yaml`:

```yaml
version: 1
asset_classes:
  equity_sector:
    source: yfinance
    instruments:
      - ticker: XLK
        bucket: Technology
        display_name: "Technology Select Sector SPDR"
      - ticker: XLV
        bucket: Healthcare
        display_name: "Health Care Select Sector SPDR"
      # ... etc
  fixed_income:
    source: yfinance
    instruments:
      - ticker: TLT
        bucket: "Long Treasury"
        display_name: "iShares 20+ Year Treasury Bond"
      # ... etc
  macro:
    source: fred
    indicators:
      - series_id: DGS10
        indicator_name: "10Y Treasury Yield"
        frequency: daily
      # ... etc

download:
  backfill_years: 5
  batch_size: 40
  retry_count: 3
  retry_delay_seconds: 5
```

### 2.5 Deliverables (SPEC-001)

| Artifact | Description |
|----------|-------------|
| `data/downloader.py` | Main download orchestrator. Handles backfill and incremental. |
| `data/yfinance_client.py` | yfinance wrapper with retry logic and batch support. |
| `data/fred_client.py` | FRED API wrapper. |
| `data/db.py` | SQLite connection manager, schema creation, upsert helpers. |
| `config/universe.yaml` | Asset class universe configuration. |
| `data/validate.py` | Post-download validation: check for gaps, NaNs, stale tickers. |
| `scripts/backfill.py` | CLI entry point: `python scripts/backfill.py --full` or `--incremental`. |

### 2.6 Acceptance Criteria

1. Running `python scripts/backfill.py --full` downloads 5 years of data for all configured tickers and populates the SQLite database.
2. Running `python scripts/backfill.py --incremental` adds only new dates since last download.
3. The database contains no null `close` or `volume` values.
4. Each ticker has at least 1,200 trading days of data (5y × ~252 days).
5. The `universe.yaml` file can be edited to add/remove tickers without code changes.
6. Total backfill completes in under 5 minutes on a reasonable internet connection.
7. A validation report prints after each download showing row counts, date ranges, and any warnings.

---

## 3. SPEC-002: Signal Generation & Analysis Engine

### 3.1 Purpose

Transform raw price/volume data into a feature matrix of ~200-300 signals per asset class per day. These signals encode Wyckoff phase detection, volume anomalies, momentum, and cross-asset-class relative strength. The engine then applies pattern recognition and statistical methods to flag buy/sell conditions with an emphasis on **sell signal reliability**.

### 3.2 Signal Taxonomy

Signals are organized into five families. Each signal is computed per asset class bucket per trading day.

#### 3.2.1 Family 1: Volume Analytics (core Wyckoff)

| Signal ID | Name | Formula | Interpretation |
|-----------|------|---------|----------------|
| V001 | raw_volume | volume | Raw daily volume |
| V002 | dollar_volume | close × volume | Dollar-denominated flow |
| V003 | rel_volume_5d | volume / SMA(volume, 5) | Short-term volume anomaly |
| V004 | rel_volume_20d | volume / SMA(volume, 20) | Medium-term volume anomaly |
| V005 | rel_volume_60d | volume / SMA(volume, 60) | Long-term volume anomaly |
| V006 | vol_trend_20d | slope of linear regression of volume over 20d | Volume trend direction |
| V007 | up_volume_ratio_10d | sum(volume where close > prev_close, 10d) / sum(volume, 10d) | Buying pressure |
| V008 | up_volume_ratio_20d | same, 20d window | Buying pressure (slower) |
| V009 | down_volume_ratio_10d | 1 - V007 | Selling pressure |
| V010 | down_volume_ratio_20d | 1 - V008 | Selling pressure (slower) |
| V011 | volume_price_divergence | sign(ROC(close, 20)) ≠ sign(ROC(volume, 20)) | Classic divergence flag |
| V012 | climax_volume | volume > 2.5 × SMA(volume, 50) | Potential climax detection |
| V013 | dry_up | volume < 0.4 × SMA(volume, 50) | Low volume test / absorption |

#### 3.2.2 Family 2: Price Momentum & Trend

| Signal ID | Name | Formula | Interpretation |
|-----------|------|---------|----------------|
| P001 | roc_5d | (close - close[5]) / close[5] | 1-week momentum |
| P002 | roc_20d | (close - close[20]) / close[20] | 1-month momentum |
| P003 | roc_60d | (close - close[60]) / close[60] | 3-month momentum |
| P004 | roc_120d | (close - close[120]) / close[120] | 6-month momentum |
| P005 | sma_20 | SMA(close, 20) | 1-month trend |
| P006 | sma_50 | SMA(close, 50) | ~quarter trend |
| P007 | sma_200 | SMA(close, 200) | Long-term trend |
| P008 | price_vs_sma20 | close / SMA(close, 20) - 1 | Distance from short trend |
| P009 | price_vs_sma200 | close / SMA(close, 200) - 1 | Distance from long trend |
| P010 | sma20_vs_sma200 | SMA(close, 20) / SMA(close, 200) - 1 | Trend alignment |
| P011 | atr_14 | ATR(14) | Volatility |
| P012 | atr_pct | ATR(14) / close | Normalized volatility |
| P013 | high_20d | max(high, 20) | 20-day high watermark |
| P014 | low_20d | min(low, 20) | 20-day low watermark |
| P015 | range_position_20d | (close - P014) / (P013 - P014) | Where in range |

#### 3.2.3 Family 3: Wyckoff Phase Detection

These are composite signals that attempt to classify the current Wyckoff phase for each asset class.

| Signal ID | Name | Logic | Output |
|-----------|------|-------|--------|
| W001 | wyckoff_phase | State machine (see below) | Enum: accumulation, markup, distribution, markdown, undetermined |
| W002 | phase_confidence | Weighted score of supporting evidence | 0.0 to 1.0 |
| W003 | phase_duration_days | Days in current phase | Integer |
| W004 | spring_detected | Price briefly breaks below support on low volume, then recovers | Boolean |
| W005 | upthrust_detected | Price briefly breaks above resistance on high volume, then fails | Boolean |
| W006 | test_detected | Price approaches prior extreme on declining volume | Boolean |
| W007 | sign_of_strength | Strong up move on high volume after range | Boolean |
| W008 | sign_of_weakness | Strong down move on high volume after range | Boolean |

**Wyckoff Phase State Machine (W001):**

```
ACCUMULATION criteria (all must be true over rolling 40-60d window):
  - Price in defined range (P013 - P014 < 2 × ATR on entry)
  - Volume declining on down moves (V009 trending down)
  - At least one spring (W004) or test (W006) detected
  - No new lows in last 10 days

MARKUP criteria:
  - Price breaks above prior range high
  - Volume expanding on up days (V007 > 0.6)
  - Close > SMA20 > SMA50

DISTRIBUTION criteria (all must be true over rolling 40-60d window):
  - Price in defined range at elevated level
  - Volume declining on up moves (V007 trending down)
  - At least one upthrust (W005) detected
  - No new highs in last 10 days

MARKDOWN criteria:
  - Price breaks below prior range low
  - Volume expanding on down days (V009 > 0.6)
  - Close < SMA20 < SMA50
```

**Sell-signal emphasis:** Distribution and markdown detection parameters should be tuned to be **more sensitive** (lower thresholds) than accumulation and markup. False positive sells are less costly than missed sells for an operator who admits they don't sell well.

#### 3.2.4 Family 4: Cross-Asset Relative Strength

| Signal ID | Name | Formula | Interpretation |
|-----------|------|---------|----------------|
| R001 | rs_vs_spy_20d | ROC(bucket, 20) - ROC(SPY, 20) | Relative strength vs. broad market |
| R002 | rs_vs_spy_60d | ROC(bucket, 60) - ROC(SPY, 60) | Longer-term relative strength |
| R003 | rs_rank_20d | Percentile rank of R001 across all buckets | Sector rank |
| R004 | rs_rank_60d | Percentile rank of R002 across all buckets | Longer-term sector rank |
| R005 | dollar_vol_share | bucket dollar_volume / sum(all bucket dollar_volumes) | Market share of flow |
| R006 | dollar_vol_share_delta_20d | R005 - R005[20] | Flow share change |
| R007 | flow_rank | Percentile rank of R006 across all buckets | Who's gaining flow |

**Note:** SPY must be added to the universe as a benchmark (non-tradeable bucket).

#### 3.2.5 Family 5: Regime & Macro Context

| Signal ID | Name | Formula | Interpretation |
|-----------|------|---------|----------------|
| M001 | yield_curve_slope | DGS10 - DGS2 (from FRED) | Recession indicator |
| M002 | vix_level | ^VIX close | Fear gauge |
| M003 | vix_percentile_1y | Percentile rank of VIX over 252 days | Relative fear |
| M004 | gold_to_spy_ratio | GLD close / SPY close | Risk-off preference |
| M005 | tlt_to_spy_ratio | TLT close / SPY close | Flight-to-safety |
| M006 | dollar_trend | ROC(DX-Y.NYB, 20) | Dollar momentum |
| M007 | high_yield_spread | HYG close / LQD close | Credit stress proxy |

### 3.3 Feature Matrix

The signal engine produces a **feature matrix** stored as:

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bucket TEXT NOT NULL,
    date DATE NOT NULL,
    signal_id TEXT NOT NULL,
    value REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bucket, date, signal_id)
);

CREATE INDEX idx_signals_bucket_date ON signals(bucket, date);
CREATE INDEX idx_signals_date ON signals(date);
```

Alternatively, for performance, store as a wide table with one column per signal. Decision deferred to implementation — either works for Phase 1 volumes.

### 3.4 Pattern Detection & Scoring

#### 3.4.1 Composite Sell Score

A weighted composite of signals most predictive of distribution/markdown:

```
sell_score = w1 * (V009 > threshold) +
             w2 * (W001 == 'distribution') +
             w3 * (W005 == True) +
             w4 * (R006 < -threshold) +
             w5 * (V011 == True and P002 > 0) +   # volume divergence at top
             w6 * (P008 < 0 and V003 > 2.0)       # high volume breakdown
```

Initial weights set heuristically; refined via backtesting in Phase 1.

#### 3.4.2 Composite Buy Score

Same structure but using accumulation/markup signals. Lower priority for initial tuning.

#### 3.4.3 Backtesting Framework

The system must support backtesting any composite score against forward returns:

- For each historical date, compute the composite score.
- Measure forward returns at 5d, 10d, 20d, 60d horizons.
- Compute hit rate: % of times a score above threshold preceded a negative return (for sell) or positive return (for buy).
- Compute information coefficient: rank correlation of score vs. forward return.
- Output: a report per asset class showing optimal thresholds and expected hit rates.

### 3.5 Regression & Weight Discovery (Phase 1 Stretch Goal)

Once the feature matrix exists with sufficient history:

1. **Logistic regression:** Predict binary outcome (down >5% in 20d = 1, else 0) from signal features. Output: feature importance ranking and fitted weights for the sell score.
2. **Random forest:** Same target, non-linear. Use feature importance to identify which signals matter most per asset class.
3. **Walk-forward validation:** Train on 3 years, validate on 1 year, test on 1 year. Never look ahead.

This is a stretch goal because it requires the feature matrix to be populated and validated first.

### 3.6 Deliverables (SPEC-002)

| Artifact | Description |
|----------|-------------|
| `signals/calculator.py` | Main signal computation engine. Takes raw data, outputs feature matrix. |
| `signals/volume.py` | Family 1: Volume analytics. |
| `signals/momentum.py` | Family 2: Price momentum. |
| `signals/wyckoff.py` | Family 3: Wyckoff phase state machine. |
| `signals/relative.py` | Family 4: Cross-asset relative strength. |
| `signals/macro.py` | Family 5: Regime/macro context. |
| `signals/composite.py` | Sell/buy composite score computation. |
| `signals/backtest.py` | Backtesting framework for score validation. |
| `scripts/compute_signals.py` | CLI entry point: `python scripts/compute_signals.py --date 2026-04-08` or `--backfill`. |

### 3.7 Acceptance Criteria

1. For a single bucket and single date, the system produces all signals in Families 1-5 (excluding regression) in under 1 second.
2. Full backfill of signals for all ~40 buckets over 5 years completes in under 10 minutes.
3. The Wyckoff phase state machine correctly identifies at least 3 historical accumulation and 3 distribution phases in SPY when manually verified against known market events (e.g., COVID-19 selloff/recovery, 2022 bear market).
4. The backtesting framework produces a report showing hit rates and information coefficients for sell and buy scores.
5. Each signal family is independently testable with unit tests covering edge cases (e.g., insufficient history, zero volume, missing data).

---

## 4. SPEC-003: Flask User Interface

### 4.1 Purpose

A locally-hosted web application for viewing signals, monitoring portfolio drift, and reviewing Wyckoff phase status across all asset class buckets. Runs on `localhost:5000`. No authentication needed (local only).

### 4.2 Technology Requirements

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | Python 3.11+, Flask | Lightweight, Ed to provide stack details |
| Frontend | HTML + Jinja2 templates, HTMX | Minimal JS. HTMX for dynamic updates without React complexity. |
| Charts | Plotly.js (via CDN) | Interactive volume/price charts with Wyckoff annotations |
| Tables | DataTables.js (via CDN) | Sortable, filterable signal tables |
| CSS | Tailwind CSS (via CDN) | Utility-first, minimal custom CSS |
| Database | SQLite (same as data layer) | Single file, no server process |

### 4.3 Page Specifications

#### 4.3.1 Dashboard (Home) — `/`

**Purpose:** At-a-glance view of all asset class buckets with current Wyckoff phase and composite scores.

**Layout:**
- Header: "Wyckoff Accumulator" + last data update timestamp
- Summary bar: Count of buckets in each Wyckoff phase (e.g., "3 Accumulation | 12 Markup | 2 Distribution | 1 Markdown | 22 Undetermined")
- Main table: One row per asset class bucket

**Table columns:**
| Column | Content |
|--------|---------|
| Bucket | Asset class name (e.g., "Technology") |
| Asset Class | Category (e.g., "Equity Sector") |
| Close | Latest adjusted close |
| Chg 1D | 1-day return % |
| Chg 20D | 20-day return % |
| Rel Volume | V004 (rel_volume_20d) |
| Buy Pressure | V007 (up_volume_ratio_10d) |
| Wyckoff Phase | W001 with color coding (green=accumulation, blue=markup, orange=distribution, red=markdown, gray=undetermined) |
| Phase Conf. | W002 (confidence) |
| Sell Score | Composite sell score with heat coloring |
| Buy Score | Composite buy score with heat coloring |
| Flow Rank | R007 (percentile, higher = more inflow) |

**Sorting default:** Sell Score descending (highest sell signals at top — matches operator's stated priority).

**Row click:** Navigate to bucket detail page.

#### 4.3.2 Bucket Detail — `/bucket/<bucket_name>`

**Purpose:** Deep dive into a single asset class bucket showing price/volume chart with Wyckoff annotations and full signal history.

**Layout:**
- Header: Bucket name, current phase badge, phase duration
- Chart area (Plotly):
  - Top panel: Candlestick or line chart of price with SMA20, SMA50, SMA200 overlays
  - Bottom panel: Volume bars colored by up/down day
  - Annotations: Wyckoff event markers (springs, upthrusts, tests, signs of strength/weakness) as arrows/icons on chart
  - Shaded regions: Wyckoff phase periods color-coded
- Signal table: All current signal values for this bucket, grouped by family
- History table: Last 60 days of composite sell/buy scores, sortable

**Interactive features:**
- Date range selector (HTMX driven, re-renders chart)
- Toggle overlays on/off (SMAs, Wyckoff annotations)

#### 4.3.3 Cross-Asset Flow Map — `/flows`

**Purpose:** Visualize money moving between asset classes over time.

**Layout:**
- Heatmap (Plotly): X-axis = dates (last 60 trading days), Y-axis = all buckets, color = dollar volume share change (R006). Red = outflow, green = inflow.
- Flow ranking table: Current R007 values sorted descending with sparklines showing 20-day trend.

#### 4.3.4 Portfolio View — `/portfolio`

**Purpose:** Map the operator's actual Fidelity holdings to asset class buckets and show drift from target weights.

**Layout:**
- Upload area: Drag-and-drop Fidelity CSV or paste path
- Mapping table: Each holding → mapped bucket → current weight → target weight → drift
- Unmapped holdings flagged for manual mapping
- Summary: Aggregate weight by asset class vs. target, with traffic-light coloring

#### 4.3.5 Alerts View — `/alerts`

**Purpose:** Chronological log of triggered signals.

**Layout:**
- Filter bar: By alert type (sell, buy, phase change), by asset class, by date range
- Alert cards: Each showing bucket, signal type, score, date, brief description
- Alerts generated when:
  - Sell score crosses above configurable threshold
  - Buy score crosses above configurable threshold
  - Wyckoff phase changes
  - Relative volume (V004) exceeds 2.0
  - Flow rank (R007) changes by more than 20 percentile points in 5 days

#### 4.3.6 Settings — `/settings`

**Purpose:** Configure the system without editing YAML files.

**Features:**
- Add/remove/deactivate tickers in universe
- Adjust composite score weights
- Set alert thresholds
- Trigger manual data download
- View download log and data health

### 4.4 Deliverables (SPEC-003)

| Artifact | Description |
|----------|-------------|
| `app/__init__.py` | Flask app factory. |
| `app/routes/dashboard.py` | Dashboard route and data assembly. |
| `app/routes/bucket.py` | Bucket detail route. |
| `app/routes/flows.py` | Cross-asset flow map route. |
| `app/routes/portfolio.py` | Portfolio import and drift calculation. |
| `app/routes/alerts.py` | Alerts view route. |
| `app/routes/settings.py` | Settings management route. |
| `app/templates/` | Jinja2 templates for all pages. |
| `app/static/` | Any static assets (minimal — mostly CDN). |
| `scripts/run_server.py` | CLI entry point: `python scripts/run_server.py` → localhost:5000. |

### 4.5 Acceptance Criteria

1. `python scripts/run_server.py` launches the Flask app on localhost:5000.
2. Dashboard loads in under 2 seconds with all ~40 buckets displayed.
3. Bucket detail page renders a price/volume chart with at least one Wyckoff annotation visible on a known historical distribution period.
4. Portfolio view successfully parses a Fidelity positions CSV export and maps at least 80% of holdings to asset class buckets automatically.
5. Alerts page shows at least 3 different alert types from historical data.
6. All pages are functional without JavaScript disabled (HTMX degrades to full page loads).

---

## 5. SPEC-004: Portfolio Integration

### 5.1 Fidelity CSV Format

Fidelity's "Positions" CSV export typically contains:

```
Account Number, Account Name, Symbol, Description, Quantity, Last Price,
Last Price Change, Current Value, Today's Gain/Loss Dollar,
Today's Gain/Loss Percent, Total Gain/Loss Dollar, Total Gain/Loss Percent,
Cost Basis Per Share, Cost Basis Total, Type
```

### 5.2 Ticker-to-Bucket Mapping

Each security in the portfolio must map to an asset class bucket. This mapping is maintained in:

```yaml
# config/portfolio_mapping.yaml
mappings:
  # Direct ticker mappings
  AAPL: Technology
  MSFT: Technology
  JPM: Financials
  XOM: Energy

  # Fallback: use yfinance sector lookup for unmapped tickers
  fallback: yfinance_sector

  # Manual overrides for edge cases
  overrides:
    BRK.B: Financials    # yfinance sometimes misclassifies
    GOOG: Technology      # Communication Services in GICS, but operator prefers Tech
```

### 5.3 Rebalance Report

Given current holdings mapped to buckets and operator-defined target weights, produce:

| Column | Content |
|--------|---------|
| Bucket | Asset class bucket name |
| Current $ | Sum of holdings mapped to this bucket |
| Current % | Current weight |
| Target % | Operator-defined target |
| Drift | Current % - Target % |
| Wyckoff Phase | Current phase for this bucket |
| Sell Score | Current composite sell score |
| Suggested Action | "Trim" if drift > +2% AND sell score elevated; "Add" if drift < -2% AND buy score elevated; "Hold" otherwise |

### 5.4 Deliverables (SPEC-004)

| Artifact | Description |
|----------|-------------|
| `portfolio/parser.py` | Fidelity CSV parser. |
| `portfolio/mapper.py` | Ticker-to-bucket mapping with yfinance fallback. |
| `portfolio/rebalance.py` | Drift calculation and rebalance suggestion engine. |
| `config/portfolio_mapping.yaml` | Manual ticker-to-bucket mappings. |
| `config/target_weights.yaml` | Operator-defined target weights per bucket. |

---

## 6. Phase 1 Build Sequence

Ordered for incremental delivery. Each step produces a working increment.

| Step | Description | Depends On | Estimated Effort |
|------|-------------|------------|-----------------|
| 1 | Project scaffolding: directories, `pyproject.toml`, virtual env, SQLite setup | Nothing | 1 hour |
| 2 | `config/universe.yaml` with all ~40 tickers defined | Nothing | 30 min |
| 3 | SPEC-001: Data downloader (yfinance only, no FRED yet) | Steps 1-2 | 4 hours |
| 4 | SPEC-001: Backfill validation and data health report | Step 3 | 2 hours |
| 5 | SPEC-002: Volume analytics (Family 1) | Step 3 | 3 hours |
| 6 | SPEC-002: Momentum signals (Family 2) | Step 3 | 2 hours |
| 7 | SPEC-002: Wyckoff phase state machine (Family 3) | Steps 5-6 | 6 hours |
| 8 | SPEC-003: Flask scaffolding + Dashboard (table only, no charts) | Step 5 | 3 hours |
| 9 | SPEC-002: Cross-asset relative strength (Family 4) | Step 5 | 2 hours |
| 10 | SPEC-003: Bucket detail page with Plotly charts | Steps 7-8 | 4 hours |
| 11 | SPEC-002: Composite sell/buy scores | Steps 5-7, 9 | 3 hours |
| 12 | SPEC-003: Flow map page | Step 9 | 3 hours |
| 13 | SPEC-001: FRED data integration | Step 3 | 2 hours |
| 14 | SPEC-002: Macro/regime signals (Family 5) | Step 13 | 2 hours |
| 15 | SPEC-004: Fidelity CSV parser + portfolio mapping | Step 2 | 3 hours |
| 16 | SPEC-003: Portfolio view page | Steps 11, 15 | 3 hours |
| 17 | SPEC-003: Alerts view + alert generation logic | Step 11 | 3 hours |
| 18 | SPEC-002: Backtesting framework | Step 11 | 4 hours |
| 19 | SPEC-003: Settings page | Steps 2, 3 | 2 hours |
| 20 | Integration testing + signal validation against known events | All above | 4 hours |

**Total estimated Phase 1 effort: ~56 hours of Claude Code implementation time.**

### Minimum Viable Product (Steps 1-8)

After Step 8 you have: data downloading, volume signals, and a dashboard table. This is usable — you can see relative volume anomalies across all asset classes in a browser.

### First Sell Signal (Steps 1-11)

After Step 11 you have: composite sell scores. This is the core value proposition.

---

## 7. Phase 2 Roadmap

Phase 2 is **not built now**. This section documents the planned evolution for future Claude Code sessions.

### 7.1 Paid Data Integration (Polygon.io)

- **Trigger:** Operator subscribes to Polygon.io Starter tier (~$29/month).
- **Adds:** More reliable EOD data, options flow data, extended market hours data.
- **Key feature:** Options unusual activity scanner. Large options bets by institutional players are a stronger leading indicator than equity volume alone. Polygon's options endpoints provide open interest and volume by strike/expiry.
- **Implementation:** New `data/polygon_client.py` replacing yfinance for equities. yfinance remains for crypto/forex where Polygon free tier may not cover.

### 7.2 Sub-Industry Granularity

- **Trigger:** Phase 1 signals are validated and operator wants to go deeper than 11 equity sectors.
- **Adds:** Expand from 11 equity sector ETFs to ~74 industry-level ETFs (iShares, SPDR, VanEck industry ETFs).
- **Key challenge:** Many industry ETFs are illiquid. Need minimum volume thresholds to filter usable proxies.
- **Implementation:** Expand `universe.yaml` with industry-level tickers. Signal engine already works — just more rows.

### 7.3 Individual Security Signals

- **Trigger:** Operator wants Wyckoff signals on specific holdings, not just sector proxies.
- **Adds:** Pull EOD data for all portfolio holdings. Run signal engine per-holding.
- **Key challenge:** Need Finviz or similar for sector/industry mapping of portfolio constituents. yfinance sector lookup works but is slow for >100 tickers.
- **Implementation:** New `portfolio/security_signals.py`. UI adds a "Holdings" tab showing per-security Wyckoff phase.

### 7.4 Machine Learning Signal Refinement

- **Trigger:** Feature matrix has >1 year of computed signals with forward return labels.
- **Adds:** Walk-forward logistic regression and random forest models to optimize composite score weights per asset class.
- **Key technologies:** scikit-learn for models, optuna for hyperparameter tuning.
- **Important constraint:** Training data is small (~250 rows/year × 40 buckets = 10,000 rows). Risk of overfitting is high. Regularization and cross-validation are mandatory. Simple models will likely beat complex ones.

### 7.5 Automated Report Generation

- **Trigger:** Operator wants a weekly PDF/email summary.
- **Adds:** Scheduled (cron) report generation. "This week's Wyckoff Accumulator" with top sell signals, phase changes, flow shifts.
- **Implementation:** Jinja2 → HTML → PDF via weasyprint. Email via SMTP.

### 7.6 Multi-Timeframe Analysis

- **Trigger:** Operator wants weekly and monthly signal aggregation in addition to daily.
- **Adds:** Resample daily data to weekly/monthly. Compute all signals at each timeframe. Higher-timeframe signals tend to be more reliable for position-level decisions.
- **Implementation:** New resampling step in signal pipeline. UI adds timeframe toggle.

### 7.7 Sector Constituent Aggregation (The "Security Master" Approach)

- **Trigger:** Operator decides ETF proxies are insufficient and wants to build true industry-level aggregations from constituent data.
- **Adds:** Nightly download of all US equities in operator's target industries (~500-2,000 stocks). Aggregate volume and price by industry.
- **Key challenge:** Rate limits. Requires careful scheduling (overnight batch) or paid Polygon tier with higher rate limits.
- **Implementation:** New `data/constituent_downloader.py`, `data/aggregator.py`. This is the heaviest lift in the roadmap.

---

## 8. Technology Requirements

### 8.1 Python Packages (Phase 1)

```
# Core
python >= 3.11
flask >= 3.0
jinja2 >= 3.1

# Data
yfinance >= 0.2.30
fredapi >= 0.5
pandas >= 2.0
numpy >= 1.24

# Database
sqlite3 (stdlib — no install needed)

# Charts (server-side rendering optional, primarily CDN)
plotly >= 5.18

# Signal computation
scipy >= 1.11          # for linear regression slopes
statsmodels >= 0.14    # optional, for more sophisticated regression

# Testing
pytest >= 7.4
pytest-cov >= 4.1

# Utilities
pyyaml >= 6.0
click >= 8.1           # CLI argument parsing
rich >= 13.0           # terminal output formatting
```

### 8.2 Frontend (CDN, no npm/build step)

```
Plotly.js            — https://cdn.plot.ly/plotly-latest.min.js
HTMX                 — https://unpkg.com/htmx.org
DataTables           — https://cdn.datatables.net/
Tailwind CSS         — https://cdn.tailwindcss.com
```

### 8.3 External Services (Free Tier)

| Service | Purpose | Cost | Key Limit |
|---------|---------|------|-----------|
| yfinance | Market data | Free | Unofficial API, no SLA, occasional rate limits |
| FRED | Macro indicators | Free (API key required) | 120 requests/minute |

### 8.4 System Requirements

- Python 3.11+ on WSL (Ubuntu)
- ~500MB disk for 5-year SQLite database with signals
- No GPU, no Docker, no cloud services required

---

## 9. Open Questions & Risks

### 9.1 Open Questions (Require Operator Decision)

| # | Question | Default if No Answer |
|---|----------|---------------------|
| OQ1 | What are the 6-7 specific industries the operator is concentrated in? This affects which sub-industry ETFs to prioritize in Phase 2. | Start with 11 sector-level only |
| OQ2 | Does the operator want alerts via email/SMS or is browser-only sufficient for Phase 1? | Browser only |
| OQ3 | What target weights does the operator want per asset class? | Equal weight as placeholder |
| OQ4 | How frequently will the operator run the data update? Daily? Weekly? | Daily, manual trigger |
| OQ5 | Does the operator have a FRED API key already? | Will register during setup |
| OQ6 | What Fidelity account types are in scope? (Taxable, IRA, 401k all export differently) | Single account CSV |

### 9.2 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| yfinance breaks or rate-limits | Data pipeline stops | Design for source abstraction. Polygon.io is the fallback. Data layer uses a client interface pattern so swapping sources requires only a new client class. |
| Wyckoff phases too noisy on daily data | False sell signals erode operator trust | Start with conservative thresholds. Require phase confidence > 0.7 before alerting. Add weekly timeframe as confirmation. |
| Backtest overfitting | Regression weights look great historically but fail forward | Walk-forward validation only. Maximum 5-10 features in any regression model. Prefer simple heuristic scores over fitted models initially. |
| Fidelity CSV format changes | Portfolio import breaks | Parser should be tolerant of column order changes. Match on column name, not position. Log unrecognized columns. |
| SQLite performance at scale | Queries slow as data grows | Not a real risk at Phase 1 volumes (~40 tickers × 1,300 days × 50 signals = ~2.6M rows). If it matters in Phase 2, migrate to DuckDB (drop-in for analytical queries). |
| Operator doesn't use the system | Entire project wasted | Ship the MVP (Steps 1-8) fast. Get the dashboard in front of the operator within the first build session. Iterate based on actual usage. |

---

## Appendix A: Directory Structure

```
WyckoffAccumulator/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── bucket.py
│   │   ├── flows.py
│   │   ├── portfolio.py
│   │   ├── alerts.py
│   │   └── settings.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── bucket_detail.html
│   │   ├── flows.html
│   │   ├── portfolio.html
│   │   ├── alerts.html
│   │   └── settings.html
│   └── static/
│       └── css/
│           └── custom.css       # Minimal overrides only
├── config/
│   ├── universe.yaml            # Asset class universe definition
│   ├── portfolio_mapping.yaml   # Ticker-to-bucket mappings
│   └── target_weights.yaml      # Operator's target allocations
├── data/
│   ├── __init__.py
│   ├── db.py                    # SQLite manager
│   ├── downloader.py            # Download orchestrator
│   ├── yfinance_client.py       # yfinance wrapper
│   ├── fred_client.py           # FRED API wrapper
│   └── validate.py              # Data validation
├── signals/
│   ├── __init__.py
│   ├── calculator.py            # Signal computation orchestrator
│   ├── volume.py                # Family 1
│   ├── momentum.py              # Family 2
│   ├── wyckoff.py               # Family 3
│   ├── relative.py              # Family 4
│   ├── macro.py                 # Family 5
│   ├── composite.py             # Sell/buy scores
│   └── backtest.py              # Backtesting framework
├── portfolio/
│   ├── __init__.py
│   ├── parser.py                # Fidelity CSV parser
│   ├── mapper.py                # Ticker-to-bucket mapping
│   └── rebalance.py             # Drift and rebalance logic
├── scripts/
│   ├── backfill.py              # Data download CLI
│   ├── compute_signals.py       # Signal computation CLI
│   └── run_server.py            # Flask server launcher
├── tests/
│   ├── test_data/
│   ├── test_signals/
│   ├── test_portfolio/
│   └── conftest.py
├── db/
│   └── wyckoff.db               # SQLite database (gitignored)
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Appendix B: Fidelity CSV Export Instructions

For the operator's reference:

1. Log in to Fidelity.com
2. Navigate to **Accounts & Trade → Portfolio**
3. Select the account
4. Click **Positions** tab
5. Click the **Download** icon (small arrow/spreadsheet icon, usually top-right of positions table)
6. Select **CSV** format
7. Save to `WyckoffAccumulator/data/imports/` and rename to `fidelity_positions_YYYYMMDD.csv`

---

*End of project plan. This document is intended as input to a Claude Code build session. Each SPEC section is self-contained and can be implemented independently following the build sequence in Section 6.*
