# Reference Gaps: Wyckoff

Features or behaviors not yet fully specified. Resolve before promotion.

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Blocks other work — fix immediately |
| P1 | Core feature missing |
| P2-P3 | Should have |
| P4+ | Backlog |

## Open Gaps

| Priority | Gap | Notes |
|----------|-----|-------|
| P0 | Signal computation formulas | V001–V013, P001–P015, W001–W008, R001–R007, M001–M007 are listed by ID only — no formulas, lookback windows, or input columns defined; signal engine cannot be built |
| P0 | Asset universe definition | Phase 1 (11 SPDR sector ETFs) and Phase 2 (~40 buckets) tickers not enumerated; data pipeline and asset_config table cannot be populated |
| P1 | Composite score weights | `w1`–`w6` and threshold values in FEATURE-SignalEngine.md are placeholders; scoring is unimplementable |
| P1 | AGENTS.md missing | Required at PROTOTYPE; project will need it before promotion |
| P1 | Backtest feature specification | ACCEPTANCE_CRITERIA.md requires hit-rate and IC reports; no FEATURE-Backtest.md defines the walk-forward logic, horizons, or output format |
| P1 | Directory naming inconsistency | ARCHITECTURE.md defines a `scripts/` entry point directory; PROJECT_LAYOUT rule requires `bin/`; reconciliation needed before code generation |
| P2 | SCREEN-Settings.md depth | Settings screen has feature list only — no layout table, no form fields, no interaction spec for threshold editors or universe management |
| P2 | portfolio_mapping.yaml format | Referenced in FEATURE-PortfolioIntegration.md but YAML structure (keys, value types, fallback behavior) never defined |
| P2 | Daily scheduler specification | FEATURE-DataPipeline.md says "runs daily on a schedule" but no `bin/daily.sh` spec, no cron expression, no entry point defined |
| P3 | config/universe.yaml YAML format | ARCHITECTURE.md references this file but its key schema (ticker, bucket, asset_class, source fields) is not specified |

## Closed Gaps

| Priority | Gap | Closed | Notes |
|----------|-----|--------|-------|
