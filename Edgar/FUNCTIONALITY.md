# FUNCTIONALITY: myEdgar

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | High-level feature index — one paragraph per feature. All implementation detail is in individual FEATURE-STEP files. |

## Feature Index

**STEP.PreReq.1 — Library Discovery**
Before any code is written, evaluate existing Python libraries for EDGAR data access (edgar, edgartools, sec-api, etc.). Confirm connectivity, rate limits, and what is available for free. This research output directly informs all subsequent phases. **This step requires discussion with the author before proceeding.**

**STEP.PreReq.2 — Research and Plan Iteration**
Research comparable products (Calcbench, Sentieo, Visible Alpha, etc.) to understand the competitive landscape and avoid reinventing available free capabilities. Iterate the full project plan based on PreReq 1 findings. **All coding is gated on explicit author approval of the iterated plan.**

**STEP.1 — EDGAR Downloader**
CLI-driven downloader that fetches 10-Q, 10-K, and 8-K filings for all tickers in the target universe. Stores raw HTML locally with metadata, respects EDGAR rate limits, and tracks download state in the `filings` table.

**STEP.2 — Data Validation**
Validates downloaded filings for completeness and consistency. Checks that file sizes are reasonable, accession numbers are unique, and that the filing date/period_end match the EDGAR index. Builds a validation report with pass/fail per filing.

**STEP.3 — Algorithm: Signal Definition**
Defines the exact 12 metrics and their extraction logic. Builds the MVP database schema and populates it with a sample dataset. Produces a discovery report on how consistently the metrics appear in filings across tickers and quarters.

**STEP.4 — Metric Extraction and Analysis**
Extracts all 12 metrics from the MVP dataset using regex, pandas table parsing, and LLM-assisted narrative scoring. Benchmarks extraction accuracy. For hard-to-parse language, the LLM rates text into scores and updates the `rules/signals.jsonl` file with new patterns.

**STEP.5 — Red Flag Scoring System**
Implements the Red Flag Index: computes scores from extracted metrics against defined thresholds, generates per-ticker score histories, and produces buy/sell/hold signals. Designed for eventual backtesting against known stress events (TCPC, BCRED, etc.).

**STEP.6 — UI and Reporting**
Terminal scoreboard (Rich) as Phase 1 output. Phase 2 adds HTML report generation. Phase 3 target: UI with KPI trends, recent filing highlights, and automated signal reports.

## Open Questions

- See individual FEATURE-STEP files for per-feature open questions.
