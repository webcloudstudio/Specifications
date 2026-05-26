# AGILE_PLAN: Edgar2
spec:       Edgar2
target:     /mnt/c/Users/barlo/projects/Edgar2
plan_hash:  93217ea672dd
spec_commit: b90dcf1ecaf0165e414123329adba400b4ecddc6
updated:    2026-05-26T13:58:03

## spike 1: Library discovery
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_1_LIBRARY_DISCOVERY.md
finding:  Use direct EDGAR REST API via `edgar_client.py` (no edgartools).
state:    awaiting_review

## spike 2: Connectivity and processing validity
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md
finding:  Yes.
state:    awaiting_review

## spike 3: EDGAR client class
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_3_EDGAR_CLIENT_CLASS.md
finding:  `edgar_client.py` in build workspace.
state:    awaiting_review

## spike 4: Data quality and coverage
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_4_DATA_QUALITY_AND_COVERAGE.md
finding:  XBRL is the primary extraction path for NAV per share, PIK income, and unrealized gain/loss.
state:    awaiting_review

## spike 5: Database feasibility
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_5_DATABASE_FEASIBILITY.md
finding:  Six tables: `filings`, `metrics`, `positions`, `filing_flags`, `scores`, `eightk_events`.
state:    awaiting_review

## spike 6: Signal feasibility and scale direction
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md
finding:  pending PO confirmation of 7 open questions (thresholds, score direction, top-15 scope).
state:    awaiting_review

## spike 7: Business thesis
summary:  
inputs:   SPECIFICATION.md
evidence: STEP_7_BUSINESS_THESIS.md
finding:  GO.
state:    awaiting_review

## story 1: edgar_client module
summary:  Build edgar_client.py with get_cik(), get_filings(), get_document(), get_xbrl_facts(), 0.12 s rate-limit gap, and SEC-compliant User-Agent header.
inputs:   SPECIFICATION.md, STEP_3_EDGAR_CLIENT_CLASS.md
kind:     python
evidence: STEP_S1_EDGAR_CLIENT.md
state:    pending

## story 2: database schema
summary:  Create build_schema.py that initialises the SQLite database with all six tables (filings, metrics, positions, filing_flags, scores, eightk_events) including the positions UNIQUE(filing_id, dedup_key) constraint and asset_coverage_pct column naming.
inputs:   SPECIFICATION.md, STEP_5_DATABASE_FEASIBILITY.md
kind:     python
evidence: STEP_S2_DATABASE_SCHEMA.md
state:    pending

## story 3: metric extractor
summary:  Build extract_metrics.py that fetches XBRL companyfacts and iXBRL HTML for each filing, discovers per-ticker XBRL concepts at runtime for PIK income and unrealized G/L, extracts non-accrual via HTML prose regex, deduplicates XBRL observations by latest filed date, and writes rows to metrics, positions, and filing_flags.
inputs:   SPECIFICATION.md, STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md, STEP_4_DATA_QUALITY_AND_COVERAGE.md, STEP_S1_EDGAR_CLIENT.md, STEP_S2_DATABASE_SCHEMA.md
kind:     python
evidence: STEP_S3_METRIC_EXTRACTOR.md
state:    pending

## story 4: signal scorer
summary:  Build score.py that reads the metrics table, computes all 11 stress signals with confirmed scale directions and thresholds, and writes per-ticker per-quarter rows to the scores table.
inputs:   SPECIFICATION.md, STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md, STEP_S3_METRIC_EXTRACTOR.md
kind:     python
evidence: STEP_S4_SIGNAL_SCORER.md
state:    pending

## story 5: filing pipeline and scoreboard CLI
summary:  Build run_pipeline.py, a CLI entry point that fetches 10-Q and 10-K filings for ARCC, MFIC, and TCPC, orchestrates extraction and scoring, and prints a terminal/markdown scoreboard of per-ticker stress scores over time.
inputs:   SPECIFICATION.md, STEP_7_BUSINESS_THESIS.md, STEP_S1_EDGAR_CLIENT.md, STEP_S2_DATABASE_SCHEMA.md, STEP_S3_METRIC_EXTRACTOR.md, STEP_S4_SIGNAL_SCORER.md
kind:     python
evidence: STEP_S5_PIPELINE_SCOREBOARD.md
state:    pending

## ac 1: client never hardcodes CIK
parent:   story 1
origin:   dev
kind:     guardrail
state:    open

## ac 2: rate gap enforced between every request
parent:   story 1
origin:   dev
kind:     guardrail
state:    open

## ac 3: get_cik resolves all three phase-1 tickers live
parent:   story 1
origin:   dev
kind:     assertion
state:    open

## ac 4: all six tables present with correct column names
parent:   story 2
origin:   dev
kind:     assertion
state:    open

## ac 5: positions table rejects duplicate filing_id plus dedup_key pairs
parent:   story 2
origin:   dev
kind:     guardrail
state:    open

## ac 6: asset coverage column named asset_coverage_pct not ratio
parent:   story 2
origin:   dev
kind:     guardrail
state:    open

## ac 7: non-accrual extracted via HTML regex not XBRL for all three tickers
parent:   story 3
origin:   dev
kind:     guardrail
state:    open

## ac 8: PIK and unrealized XBRL concepts discovered per ticker at runtime
parent:   story 3
origin:   dev
kind:     guardrail
state:    open

## ac 9: duplicate XBRL observations resolved by latest filed date
parent:   story 3
origin:   dev
kind:     guardrail
state:    open

## ac 10: asset coverage value stored as percentage not pure decimal
parent:   story 3
origin:   dev
kind:     assertion
state:    open

## ac 11: fee waiver signal measures current-period dollar amount
parent:   story 4
origin:   dev
kind:     guardrail
state:    open

## ac 12: NII coverage uses InvestmentCompanyInvestmentIncomeLossPerShare not EarningsPerShareBasic
parent:   story 4
origin:   dev
kind:     guardrail
state:    open

## ac 13: all 11 signals produce a non-null value for TCPC Q1 2026
parent:   story 4
origin:   dev
kind:     assertion
state:    open

## ac 14: scoreboard shows per-ticker scores across multiple quarters
parent:   story 5
origin:   dev
kind:     assertion
state:    open

## ac 15: FSCO is excluded from the pipeline run
parent:   story 5
origin:   dev
kind:     guardrail
state:    open
