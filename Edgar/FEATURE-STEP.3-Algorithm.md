# FEATURE: Algorithm and Signal Definition

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Define the 12 extraction metrics, build the MVP database, populate sample data, and produce a discovery report on metric consistency across the filing universe. |
| Phase       | 2 |

## Trigger

Research phase — runs once after PreReq phases are complete and approved. Output informs STEP.4.

## The 12 Metrics

| # | Metric | Primary Source | Extraction Method |
|---|--------|---------------|-------------------|
| 1 | PIK income % of total investment income | Income Statement | Regex + table |
| 2 | Non-accrual rate at cost | MD&A non-accrual table | Table parse |
| 3 | Weighted average portfolio mark | MD&A / Schedule totals | Compute from table |
| 4 | NAV per share trend | Balance sheet | Table parse |
| 5 | Asset coverage ratio | Liquidity / debt tables | Regex |
| 6 | NII distribution coverage | Income statement | Compute |
| 7 | Net change in unrealized depreciation | Income statement | Table parse |
| 8 | Realized vs. unrealized loss ratio | Income statement | Compute |
| 9 | Maturity concentration in near term | Notes to financials | Table parse |
| 10 | Top 15 position individual marks | Schedule of Investments | Position parser |
| 11 | Fee waivers by manager | MD&A / Related Party notes | Regex |
| 12 | PIK % of new originations | MD&A / Investment Activity | Regex + table |

## MVP Dataset Build

1. Download and validate 8 quarters of 10-Q for all Tier 1 tickers (STEP.1 + STEP.2 complete).
2. Manually extract Metric 1 and Metric 2 for TCPC and ARCC for 2 quarters each — establish ground truth.
3. Run automated extraction for the same quarters and measure precision/recall against ground truth.
4. Produce a discovery report: which metrics extract cleanly vs. require LLM assistance.

## Discovery Report

Written to `data/prereq/algorithm_discovery.md`:
- Per-metric: extraction success rate across the MVP dataset.
- Which sections of 10-Q are structurally consistent vs. idiosyncratic by filer.
- Recommended regex patterns (confirmed against at least 3 different filers).
- Metrics that require LLM scoring (narrative language, non-standard tables).

## Red Flag Thresholds

Defined in `config.yaml` — all thresholds from the initial spec are the starting point. They must be confirmed/adjusted based on the MVP dataset discovery before STEP.5 scoring is built.

## Success Criteria

- At least 5 of 12 metrics extract correctly (confidence ≥ medium) across the MVP dataset.
- Ground truth comparison shows < 20% error rate for Metric 1 and Metric 2.
- Discovery report is reviewed and approved by the author before STEP.4 begins.

## Open Questions

- Should the discovery report include a comparison of BDC marks against a public index (Metric 3 divergence detection)? Or defer to Phase 3?
- Are all 12 metrics equally important for Phase 1, or should the MVP focus on the 5 most reliable extractors?
