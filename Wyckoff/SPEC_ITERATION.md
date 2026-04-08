# Specification Iteration Prompt: Wyckoff Accumulator

**Target gaps:** [P0] Signal computation formulas, [P0] Asset universe definition
**Run from:** /mnt/c/Users/barlo/projects/Specifications
**Command:** claude -p "$(cat Wyckoff/SPEC_ITERATION.md)"

## What This Prompt Does

Addresses the two P0 gaps blocking the Wyckoff Accumulator build: (1) the signal engine lists 50 signal IDs across five families but defines no formulas, lookback windows, or inputs — making `signals/volume.py`, `signals/momentum.py`, `signals/wyckoff.py`, `signals/relative.py`, and `signals/macro.py` unwritable; (2) the asset universe lists Phase 1 as "11 SPDR sector ETFs" and Phase 2 as "~40 buckets" but never enumerates the actual tickers — making `config/universe.yaml` and the `asset_config` table uninitialisable. This prompt creates `FEATURE-SignalDefinitions.md` (full per-signal specification) and `FEATURE-Universe.md` (full ticker/bucket enumeration).

## Context

### Project Description

Personal portfolio intelligence system. Detects institutional accumulation and distribution across ~40 asset class buckets using Wyckoff volume-price methodology. Generates rebalancing guidance with sell-signal emphasis. Flask/SQLite, localhost only. No authentication.

### Signal Engine Summary (from FEATURE-SignalEngine.md)

Signals are computed per bucket per date and stored in the `signals` table with columns `(bucket, date, signal_id, value)`. Five families:

| Family | IDs | Key outputs |
|--------|-----|-------------|
| Volume (V) | V001–V013 | rel_volume_20d, buying/selling pressure, climax, dry-up, divergence |
| Momentum (P) | P001–P015 | roc_5/20/60/120d, SMA crossovers, ATR, range position |
| Wyckoff (W) | W001–W008 | phase enum, confidence, spring/upthrust/test/SOS/SOW detection |
| Relative Strength (R) | R001–R007 | rs_vs_spy, rs_rank, dollar_vol_share, flow_rank |
| Macro (M) | M001–M007 | yield_curve, VIX_percentile, gold/TLT ratios, dollar trend, credit spread |

Inputs available per bucket per date: `open`, `high`, `low`, `close`, `adj_close`, `volume`, `dollar_volume` (adj_close × volume) from `market_data`. FRED macro series available in `macro_data`: DGS10, DGS2, T10Y2Y, CPIAUCSL, ICSA, M2SL, FEDFUNDS. For Relative Strength family, SPY is the benchmark ticker computed first before other buckets.

Composite sell score formula skeleton (weights are placeholders — do NOT specify weights in these files; leave as TBD):
```
sell_score = w1*(V009 > threshold) + w2*(W001=='distribution') + w3*(W005==True)
           + w4*(R006 < -threshold) + w5*(V011==True and P002>0)
           + w6*(P008 < 0 and V003 > 2.0)
```

Wyckoff phase state machine must classify each bucket as one of: `accumulation`, `markup`, `distribution`, `markdown`, `undetermined`. Phase stored as W001.

### Architecture (from ARCHITECTURE.md)

```
signals/
  volume.py      — Family 1 (V)
  momentum.py    — Family 2 (P)
  wyckoff.py     — Family 3 (W)
  relative.py    — Family 4 (R)
  macro.py       — Family 5 (M)
  composite.py   — composite score
```

Family 3 requires Families 1–2 computed first (rolling 40–60d windows). Family 4 requires SPY benchmark computed first.

### Database Schema (signals table)

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    bucket TEXT NOT NULL,
    date DATE NOT NULL,
    signal_id TEXT NOT NULL,  -- e.g. 'V004', 'W001'
    value REAL,               -- phase enum stored as integer mapping
    created_at TEXT,
    UNIQUE(bucket, date, signal_id)
);
```

Phase enum integer mapping for W001 (must be stored as REAL): `accumulation=1, markup=2, distribution=3, markdown=4, undetermined=0`.

### Asset Classes (from FUNCTIONALITY.md)

Phase 1 universe: 11 equity sector ETFs (SPDR XL* series). Phase 2 expands to full ~40-bucket universe covering: bonds (short/intermediate/long treasury, IG corp, HY corp, TIPS, munis), commodities (gold, silver, oil, nat gas, broad commodities, agriculture), forex (dollar index, yen, euro, emerging market currency), crypto (bitcoin, ethereum), real estate (REITs), and alternatives. All Phase 1 and Phase 2 data sourced via yfinance except FRED macro series (already in `macro_data`, not `asset_config`).

---

## Files to Create

### File 1: FEATURE-SignalDefinitions.md

Define every signal in all five families. For each signal provide: ID, name, formula/computation description, primary input columns, lookback window (in trading days), output type, and output range or enum.

Use this exact structure:

```markdown
# Feature: Signal Definitions

**Version:** 20260408 V1
**Description:** Per-signal formulas for all five signal families

## Signal Table Format

| ID | Name | Formula | Inputs | Lookback | Output |
|----|------|---------|--------|----------|--------|

## Family 1: Volume Analytics (V001–V013)

[table]

## Family 2: Price Momentum (P001–P015)

[table]

## Family 3: Wyckoff Phase Detection (W001–W008)

[table plus prose for state machine logic]

## Family 4: Relative Strength (R001–R007)

[table]

## Family 5: Macro Context (M001–M007)

[table plus FRED series mapping]

## Open Questions

- Composite score weights (w1–w6) and thresholds are TBD — specified separately
```

**Required signal content:**

**Family 1 — Volume Analytics (V001–V013):**
- V001: Average daily volume (20d rolling mean of volume)
- V002: Average dollar volume (20d rolling mean of dollar_volume)
- V003: Relative volume 20d (volume / V001; today's volume as multiple of 20d average)
- V004: Relative volume 5d (volume / 5d rolling mean of volume)
- V005: Up-day volume (volume on days where close > prior close)
- V006: Down-day volume (volume on days where close < prior close)
- V007: Up/down volume ratio 10d (sum of V005 over 10d / sum of V006 over 10d; buying pressure)
- V008: Volume trend 20d (linear regression slope of volume over 20d, normalised by V001)
- V009: Volume divergence (price ROC 20d positive but V008 negative, or vice versa; boolean)
- V010: Climax volume (V003 > 3.0 AND abs(close - open) / close > 0.01; boolean — high volume wide spread)
- V011: Selling climax (V010 AND close < open; boolean)
- V012: Buying climax (V010 AND close > open; boolean)
- V013: Volume dry-up (V003 < 0.5 for 3 consecutive days; boolean — Wyckoff spring/test precursor)

**Family 2 — Price Momentum (P001–P015):**
- P001: ROC 5d (rate of change: (close / close[5] - 1) × 100)
- P002: ROC 20d
- P003: ROC 60d
- P004: ROC 120d
- P005: SMA 20d (20d simple moving average of adj_close)
- P006: SMA 50d
- P007: SMA 200d
- P008: Price vs SMA20 (adj_close / P005 - 1; positive = above, negative = below)
- P009: Price vs SMA50 (adj_close / P006 - 1)
- P010: Price vs SMA200 (adj_close / P007 - 1)
- P011: SMA20 vs SMA50 (P005 / P006 - 1; golden/death cross indicator)
- P012: ATR 14d (14d average true range: mean of max(high-low, abs(high-prev_close), abs(low-prev_close)) over 14d)
- P013: ATR % (P012 / adj_close × 100; normalised volatility)
- P014: Range position (how close today's close is to the 52-week high/low: (close - low_52w) / (high_52w - low_52w))
- P015: 52-week high distance ((adj_close / rolling_max_252d - 1) × 100; negative = below 52w high)

**Family 3 — Wyckoff Phase Detection (W001–W008):**
- W001: Phase (state machine output; enum: accumulation/markup/distribution/markdown/undetermined; stored as integer 0-4)
- W002: Phase confidence (0.0–1.0; fraction of sub-signals agreeing with current phase)
- W003: Spring detected (boolean; price breaks below prior 20d low AND closes back above it within 3 days AND V003 > 1.5)
- W004: Upthrust detected (boolean; price breaks above prior 20d high AND closes back below it within 3 days AND V003 > 1.5)
- W005: Test of supply (boolean; price approaches prior 20d low within 1% AND V013 is True; low-volume test)
- W006: Sign of strength (boolean; strong close >0.8% on above-average volume after accumulation phase)
- W007: Sign of weakness (boolean; weak close <-0.8% on above-average volume after distribution phase)
- W008: Phase duration (integer; number of consecutive trading days in the current W001 phase)

For the state machine prose, describe the phase transition rules:
- `undetermined` → `accumulation`: price range-bound (P015 < -15%) for ≥20d AND P010 < -0.05
- `accumulation` → `markup`: W006 fires AND P011 > 0 (SMA20 above SMA50)
- `markup` → `distribution`: price at or near 52w high (P015 > -5%) AND V011 fires within 20d AND V008 < 0
- `distribution` → `markdown`: W007 fires AND P011 < 0
- `markdown` → `accumulation`: price decline >20% from distribution start AND V013 fires

**Family 4 — Relative Strength (R001–R007):**
- R001: Return vs SPY 5d (bucket P001 - SPY P001)
- R002: Return vs SPY 20d (bucket P002 - SPY P002)
- R003: Return vs SPY 60d (bucket P003 - SPY P003)
- R004: RS rank 20d (percentile rank of R002 among all buckets on same date; 0–100)
- R005: Dollar volume share (bucket V002 / sum of V002 across all buckets; percent of total market dollar volume)
- R006: Dollar volume share delta 20d (R005 today - R005[20d ago]; positive = inflow, negative = outflow)
- R007: Flow rank (percentile rank of R006 among all buckets on same date; 0–100)

**Family 5 — Macro Context (M001–M007):**
- M001: Yield curve slope (DGS10 - DGS2; from macro_data; positive = normal, negative = inverted)
- M002: VIX level (VIX close from market_data; ticker ^VIX)
- M003: VIX percentile (percentile rank of M002 over trailing 252d; 0–100)
- M004: Gold trend (gold ETF GLD P002 — 20d momentum)
- M005: TLT trend (long treasury ETF TLT P002 — 20d momentum)
- M006: Dollar index trend (UUP P002 — USD ETF 20d momentum; positive = dollar strengthening)
- M007: Credit spread proxy (HYG P002 - IEF P002; high yield vs intermediate treasury momentum; negative = credit stress)

Note: VIX (^VIX), GLD, TLT, UUP, HYG, IEF must be included in the asset universe (Phase 1 or Phase 2) for macro signals to compute. If not in universe, macro signals for those series are null.

### File 2: FEATURE-Universe.md

Define the complete asset universe for Phase 1 and Phase 2. For each entry provide: ticker, display name, bucket (human-readable asset class bucket name), asset_class (category), source (`yfinance` or `fred`), and phase (1 or 2).

Use this exact structure:

```markdown
# Feature: Asset Universe

**Version:** 20260408 V1
**Description:** Complete ticker list for Phase 1 and Phase 2 data pipeline

## Phase 1 Universe

Phase 1 includes the 11 SPDR sector ETFs plus the macro/benchmark tickers required for signal computation.

| Ticker | Display Name | Bucket | Asset Class | Source | Phase |
|--------|-------------|--------|-------------|--------|-------|

## Phase 2 Universe

Phase 2 adds bonds, commodities, forex, real estate, and alternatives to the Phase 1 base.

| Ticker | Display Name | Bucket | Asset Class | Source | Phase |

## Universe Configuration (universe.yaml schema)

[YAML block showing the schema for one entry so config/universe.yaml is unambiguous]

## Open Questions

-
```

**Required ticker content:**

Phase 1 must include (at minimum):
- The 11 SPDR sector ETFs: XLK (Technology), XLV (Health Care), XLF (Financials), XLY (Consumer Discretionary), XLP (Consumer Staples), XLE (Energy), XLI (Industrials), XLB (Materials), XLC (Communication Services), XLRE (Real Estate), XLU (Utilities). Asset class: `equity_sector`.
- SPY (S&P 500 benchmark) — required for R001–R004. Asset class: `benchmark`.
- ^VIX (CBOE Volatility Index) — required for M002/M003. Asset class: `macro`.
- GLD (Gold ETF) — required for M004. Asset class: `commodity`.
- TLT (20+ Year Treasury ETF) — required for M005. Asset class: `fixed_income`.
- UUP (Invesco DB US Dollar Index) — required for M006. Asset class: `forex`.
- HYG (iShares High Yield Corporate Bond) — required for M007. Asset class: `fixed_income`.
- IEF (7-10 Year Treasury ETF) — required for M007. Asset class: `fixed_income`.

Phase 2 should expand to cover:
- Fixed income buckets: SHY (1-3yr Treasury), IEF (already Phase 1), TLT (already Phase 1), TIP (TIPS), LQD (IG Corp), HYG (already Phase 1), MUB (Munis)
- Commodities: GLD (already Phase 1), SLV (Silver), USO (Oil), UNG (Nat Gas), DJP or PDBC (Broad Commodities), DBA (Agriculture)
- Forex: UUP (already Phase 1), FXY (Yen), FXE (Euro), EEM (Emerging Market proxy — also equity)
- Real estate: VNQ (REIT ETF) — if not already included via XLRE
- Alternatives / Crypto: IBIT (Bitcoin ETF), ETHA (Ethereum ETF) or similar liquid ETFs
- International equity: EFA (Developed Markets), EEM (Emerging Markets), VGK (Europe)
- Small/mid cap: IWM (Russell 2000), MDY (S&P 400 Mid Cap)

Use the FRED series (DGS10, DGS2, T10Y2Y, CPIAUCSL, ICSA, M2SL, FEDFUNDS) in the `macro_data` table only — they do NOT appear in `asset_config` or the universe YAML.

**universe.yaml schema example to include in the file:**

```yaml
universe:
  - ticker: XLK
    display_name: Technology SPDR
    bucket: Technology
    asset_class: equity_sector
    source: yfinance
    phase: 1
    is_active: true
```

---

## Conventions

- Follow existing specification file format (see ARCHITECTURE.md, DATABASE.md, FEATURE-DataPipeline.md as reference)
- All specification files end with `## Open Questions`
- Use the same table styles and column layouts as neighboring feature files
- Signal ID column should be fixed-width code format: `V001`, `W003`, etc.
- Wyckoff phase state machine prose should describe transition conditions — not just list states
- Write to: /mnt/c/Users/barlo/projects/Specifications/Wyckoff/
