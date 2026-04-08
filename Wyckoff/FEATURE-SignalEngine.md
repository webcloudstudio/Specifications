# Feature: Signal Engine

**Trigger:** Manual CLI (`python scripts/compute_signals.py --date <date>` or `--backfill`) or post-data-download

## Sequence

1. Load market_data and macro_data for target date range
2. Per bucket per date, compute signal families in order:
   - Family 1 (V): volume analytics
   - Family 2 (P): price momentum
   - Family 3 (W): Wyckoff phase — requires Families 1–2; rolling 40–60d windows
   - Family 4 (R): relative strength — requires SPY benchmark computed first
   - Family 5 (M): macro context
3. Compute composite sell score and buy score from weighted signal combinations
4. Upsert all computed values into `signals`
5. Evaluate alert triggers against configurable thresholds; write new alerts

## Signal Families

| Family | IDs | Key outputs |
|--------|-----|-------------|
| Volume (V) | V001–V013 | rel_volume_20d, buying/selling pressure, climax, dry-up, divergence |
| Momentum (P) | P001–P015 | roc_5/20/60/120d, SMA crossovers, ATR, range position |
| Wyckoff (W) | W001–W008 | phase enum, confidence, spring/upthrust/test/SOS/SOW detection |
| Relative Strength (R) | R001–R007 | rs_vs_spy, rs_rank, dollar_vol_share, flow_rank |
| Macro (M) | M001–M007 | yield_curve, VIX_percentile, gold/TLT ratios, dollar trend, credit spread |

## Composite Score Logic

```
sell_score = w1*(V009 > threshold) + w2*(W001=='distribution') + w3*(W005==True)
           + w4*(R006 < -threshold) + w5*(V011==True and P002>0)
           + w6*(P008 < 0 and V003 > 2.0)
```

Sell signal thresholds set more sensitive than buy — false positive sells preferred over missed sells.

## Reads

- market_data
- macro_data

## Writes

- signals (upsert per bucket/date/signal_id)
- alerts (new triggers only)

## Open Questions

- Wide vs narrow signals table: narrow chosen for Phase 1; revisit if query performance degrades
