# FEATURE: Red Flag Scoring System

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Compute the Red Flag Index from extracted metrics, generate per-ticker score histories, and produce actionable buy/sell/hold signals. |
| Phase       | 2 |

## Trigger

`bin/score.sh [--ticker ARCC] [--period 2026-Q1]`

Called automatically after `analyze.sh` completes for a set of filings.

## Scoring Logic

Scores are additive. Each metric's contribution is defined in `config.yaml` (thresholds and points):

| Metric | Threshold | Points |
|--------|-----------|--------|
| PIK income | > 10% | +1 |
| PIK income | > 15% | +2 cumulative |
| PIK income QoQ increase | > 3pp | +2 |
| Non-accrual at cost | > 2% | +1 |
| Non-accrual at cost | > 3% | +2 cumulative |
| Non-accrual QoQ increase | > 1.5pp | +2 |
| Weighted avg mark | < 95% | +1 |
| Weighted avg mark | < 90% | +2 cumulative |
| NAV decline QoQ | > 2% | +1 |
| NAV decline QoQ | > 4% | +2 cumulative |
| Asset coverage | < 185% | +1 |
| Asset coverage | < 170% | +2 cumulative |
| NII coverage | < 1.05x | +1 |
| NII coverage | < 1.0x | +2 cumulative |
| Unrealized depreciation | 2 consecutive quarters | +2 |
| Unrealized depreciation | 3+ consecutive quarters | +3 cumulative |
| Any top-15 position mark | < 70% | +2 |
| Fee waiver | Any | +3 |
| Distribution cut | Any | +4 |
| Redemption cap | Any | +4 |
| 8-K investigation notice | Any | +5 |

## Score Interpretation

| Score | Signal | Action |
|-------|--------|--------|
| 0–3 | Watch | Monitor quarterly |
| 4–6 | Elevated Risk | Underweight |
| 7–9 | High Stress | Short management company stock |
| 10+ | Distress | Strong short; consider puts |

## Trading Signal Generation

**Long signal (FSCO model)**: Score 0–3, trading at discount to NAV > 15%, > 75% senior secured, closed-end exchange-listed.

**Short signal — management company (primary)**: Underlying BDC score > 7 AND management company stock has not declined proportionally AND one or more: distribution cut, redemption cap, investigation.

**Short signal — BDC (secondary)**: Any BDC trading at premium to NAV with score > 6.

**Pairs trade**: Long FSCO / Short ARCC or OBDC.

## Score History

`metrics.red_flag_score` is populated per filing. The scorer also writes a `score_history` view or query that shows quarter-by-quarter score trend per ticker.

## Backtesting

Phase 3 feature. Validate test cases:

| Event | Ticker | Quarter | Expected |
|-------|--------|---------|----------|
| 19% NAV cut | TCPC | Q4 2025 / Q1 2026 | Score ≥ 10 |
| Non-accrual 0.6%→2.4% | BCRED | Q1 2026 | Non-accrual flag |
| Redemption cap 5% | Ares funds | Q1 2026 | Redemption cap critical |
| $3B fund sale | APO | Q1 2026 | Material event flag |
| DOJ investigation | BLK/TCPC | May 2026 | +5 investigation points |

## Success Criteria

- `score.sh` correctly scores TCPC at ≥ 10 and FSCO at ≤ 3 when fed the Q1 2026 10-Q data.
- Score history shows the correct trend direction for TCPC (rising score over trailing 4 quarters).
- All trading signals (long, short, pairs) are derivable from the score alone — no external data needed for Phase 1.

## Open Questions

- Should thresholds be configurable per-ticker (some BDCs have structurally higher PIK) or global?
- Should the scoring system emit alerts into the `alerts` table automatically, or should alerts be a separate step?
