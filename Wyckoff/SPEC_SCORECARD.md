# Specification Scorecard: Wyckoff Accumulator

**Generated:** 2026-04-08
**Status:** IDEA

## Dimension Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Completeness | 6/10 | All 6 screens and 3 feature pipelines are specified, but the signal engine — the core computational layer — lacks any per-signal formulas, and the asset universe is never enumerated |
| Buildability | 4/10 | Flask app shell, database schema, and UI screens are buildable, but the signal engine (50 signals) and composite score weights are placeholders that require guessing |
| Internal Consistency | 7/10 | Files are mostly consistent; one structural conflict — ARCHITECTURE.md defines a `scripts/` directory while PROJECT_LAYOUT rules require `bin/` |
| Architecture Clarity | 7/10 | Module responsibilities, data flow sequence, and database schema are clearly described with explicit reads/writes per feature |
| Screen Coverage | 7/10 | All 6 routes have spec files with layouts and column definitions; Settings screen is notably sparse with only a feature list and no layout, form fields, or interaction patterns |
| Rules Alignment | 6/10 | IDEA conformity requirements are met; AGENTS.md is missing for PROTOTYPE promotion; `scripts/` vs `bin/` violates PROJECT_LAYOUT; no `bin/daily.sh` spec despite daily scheduler being a stated feature |
| Open Questions Hygiene | 4/10 | Most OQ sections contain only a `-` placeholder rather than real questions or being omitted; only DATABASE.md, FEATURE-SignalEngine.md, and SCREEN-Alerts.md have substantive OQ entries |
| **Overall** | **6/10** | Solid foundation for screens and data flow; signal computation and universe definition are the two blocking gaps before a build attempt |

## Gap Summary

| Priority | Open | Closed | Total |
|----------|------|--------|-------|
| P0 | 2 | 0 | 2 |
| P1 | 4 | 0 | 4 |
| P2-P3 | 4 | 0 | 4 |
| P4+ | 0 | 0 | 0 |

## Priority Actions

1. **[P0] Signal computation formulas** — Write `FEATURE-SignalDefinitions.md` defining every signal ID (V001–V013, P001–P015, W001–W008, R001–R007, M001–M007) with formula, inputs, lookback window, and output type; without this, `signals/volume.py`, `signals/momentum.py`, and `signals/wyckoff.py` cannot be written
2. **[P0] Asset universe definition** — Write `FEATURE-Universe.md` enumerating all Phase 1 and Phase 2 tickers with their bucket and asset class; without this, `config/universe.yaml` and `asset_config` table population are undefined
3. **[P1] Composite score weights** — Specify `w1`–`w6` and threshold values in FEATURE-SignalEngine.md (or a companion file) so the composite scoring formula is implementable without tuning guesses
4. **[P1] Backtest feature specification** — Write `FEATURE-Backtest.md` covering walk-forward mechanics, forward-return horizons, IC calculation method, and output format to satisfy the acceptance criterion requiring hit-rate reports
5. **[P2] SCREEN-Settings.md depth** — Expand Settings screen spec with a layout table, form field definitions, and interaction patterns for threshold editing and universe management

## What This Specification Does Well

- Database schema is complete, typed, and includes all tables needed for the full feature set including the `target_weights` design decision to use the database rather than YAML
- Feature pipeline files (DataPipeline, SignalEngine, PortfolioIntegration) give explicit step-by-step sequences with named reads and writes — a builder can follow the flow without interpretation
- Acceptance criteria are concrete and testable: each item is a falsifiable MUST/MUST NOT with a measurable threshold (e.g., "1,200 trading days", "under 2 seconds", "80% mapping")
- All UI screens share a coherent component system (phase badge, score cell, rel-volume indicator) defined in UI.md and referenced consistently across screen specs

## Regenerate

```bash
bash bin/spec_iterate.sh Wyckoff
```
