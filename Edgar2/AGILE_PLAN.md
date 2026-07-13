# AGILE_PLAN: Edgar2
spec:       Edgar2
target:     /mnt/c/Users/barlo/projects/Edgar2
plan_hash:  73f6b149b9c7
spec_commit: 726fce16536e7d3c4ce9c9acb1c0f50682f4dd4c
updated:    2026-05-26T21:12:34


## spike 1: Library discovery
summary:     Library discovery
description: Confirm and document the resolution of: Library discovery.
inputs:      SPECIFICATION.md
evidence:    STEP_1_LIBRARY_DISCOVERY.md
question:    Library discovery
finding:     Use direct EDGAR REST API via `edgar_client.py` (no edgartools).
state:    approved
decided_at: 2026-05-26T19:24:08

## spike 2: Connectivity and processing validity
summary:     Connectivity and processing validity
description: Confirm and document the resolution of: Connectivity and processing validity.
inputs:      SPECIFICATION.md
evidence:    STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md
question:    Connectivity and processing validity
finding:     Yes.
state:    approved
decided_at: 2026-05-26T19:24:16

## spike 3: EDGAR client class
summary:     EDGAR client class
description: Confirm and document the resolution of: EDGAR client class.
inputs:      SPECIFICATION.md
evidence:    STEP_3_EDGAR_CLIENT_CLASS.md
question:    EDGAR client class
finding:     `edgar_client.py` in build workspace.
state:    approved
decided_at: 2026-05-26T19:24:28

## spike 4: Data quality and coverage
summary:     Data quality and coverage
description: Confirm and document the resolution of: Data quality and coverage.
inputs:      SPECIFICATION.md
evidence:    STEP_4_DATA_QUALITY_AND_COVERAGE.md
question:    Data quality and coverage
finding:     XBRL is the primary extraction path for NAV per share, PIK income, and unrealized gain/loss.
state:    approved
decided_at: 2026-05-26T19:24:33

## spike 5: Database feasibility
summary:     Database feasibility
description: Confirm and document the resolution of: Database feasibility.
inputs:      SPECIFICATION.md
evidence:    STEP_5_DATABASE_FEASIBILITY.md
question:    Database feasibility
finding:     Six tables: `filings`, `metrics`, `positions`, `filing_flags`, `scores`, `eightk_events`.
state:    approved
decided_at: 2026-05-26T19:24:37

## spike 6: Signal feasibility and scale direction
summary:     Signal feasibility and scale direction
description: Confirm and document the resolution of: Signal feasibility and scale direction.
inputs:      SPECIFICATION.md
evidence:    STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md
question:    Signal feasibility and scale direction
finding:     pending PO confirmation of 7 open questions (thresholds, score direction, top-15 scope).
state:    approved
decided_at: 2026-05-26T19:24:43

## spike 7: Business thesis
summary:     Business thesis
description: Confirm and document the resolution of: Business thesis.
inputs:      SPECIFICATION.md
evidence:    STEP_7_BUSINESS_THESIS.md
question:    Business thesis
finding:     GO.
state:    approved
decided_at: 2026-05-26T19:24:50

## ac 1: evidence records edgartools rejection as dependency hygiene, not import failure
parent:    spike 1
origin:    dev
kind:      assertion
state:    verified

## ac 2: evidence confirms 0.12 s inter-request gap is safe against data.sec.gov rate limits
parent:    spike 1
origin:    dev
kind:      assertion
state:    verified

## ac 3: evidence confirms FSCO has zero 10-Q and 10-K filings on record
parent:    spike 1
origin:    dev
kind:      guardrail
state:    verified

## ac 4: evidence confirms NAV per share is present via XBRL for ARCC, MFIC, and TCPC
parent:    spike 2
origin:    dev
kind:      assertion
state:    verified

## ac 5: evidence documents that asset coverage XBRL is absent for TCPC and requires HTML fallback
parent:    spike 2
origin:    dev
kind:      guardrail
state:    verified

## ac 6: evidence records primary iXBRL document size as 17–37 MB per 10-Q (not ~0.9 MB)
parent:    spike 2
origin:    dev
kind:      assertion
state:    verified

## ac 7: edgar_client.py exposes get_cik, get_filings, get_document, get_xbrl_facts with only requests as a dependency
parent:    spike 3
origin:    dev
kind:      assertion
state:    verified

## ac 8: client enforces a minimum 0.12 s gap between all outbound requests
parent:    spike 3
origin:    dev
kind:      guardrail
state:    verified

## ac 9: non-accrual is absent from XBRL companyfacts for all three Phase 1 tickers
parent:    spike 4
origin:    dev
kind:      guardrail
state:    verified

## ac 10: evidence records per-ticker XBRL concept names for PIK income and unrealized gain/loss
parent:    spike 4
origin:    dev
kind:      assertion
state:    verified

## ac 11: evidence confirms iXBRL tags must be stripped from filing HTML before applying non-accrual regex
parent:    spike 4
origin:    dev
kind:      guardrail
state:    verified

## ac 12: all six tables load without FK integrity errors from build_schema.py
parent:    spike 5
origin:    dev
kind:      assertion
state:    verified

## ac 13: positions table carries UNIQUE(filing_id, dedup_key) to block duplicate XBRL SoI rows
parent:    spike 5
origin:    dev
kind:      guardrail
state:    verified

## ac 14: filing_flags table is used for extraction anomalies; no packed extraction_notes string column exists
parent:    spike 5
origin:    dev
kind:      guardrail
state:    verified

## ac 15: all 11 signals are extractable from XBRL or HTML sources for TCPC Q1 2026
parent:    spike 6
origin:    dev
kind:      assertion
state:    verified

## ac 16: asset coverage regex is exactly r"asset coverage ratio was (\d+\.?\d*)\s*%" (narrow — does not capture the BDC reform text)
parent:    spike 6
origin:    dev
kind:      guardrail
state:    verified

## ac 17: per-position top-15 marks are deferred to Phase 2 and not attempted in Phase 1
parent:    spike 6
origin:    dev
kind:      guardrail
state:    verified

## ac 18: evidence confirms no existing tool produces a longitudinal BDC-specific stress-signal scoreboard at zero cost
parent:    spike 7
origin:    dev
kind:      assertion
state:    verified

## story 1: EDGAR REST client
summary:     Implement edgar_client.py wrapping the four SEC REST endpoints needed by the pipeline.
description: Build edgar_client.py with four public methods: get_cik(ticker) resolves a ticker to a CIK string via the SEC company-search endpoint; get_filings(cik, form_types) returns a list of filing metadata dicts; get_document(accession_url) returns raw bytes; get_xbrl_facts(cik) returns the companyfacts JSON payload. Enforce a 0.12 s inter-request gap internally. Import only requests — no edgartools or other HTTP clients.
inputs:      SPECIFICATION.md, STEP_1_LIBRARY_DISCOVERY.md, STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md, STEP_3_EDGAR_CLIENT_CLASS.md
kind:        python
evidence:    STEP_S1_EDGAR_CLIENT.md
state:    accepted
finding:  `edgar_client.py` already existed from Step 3 (spike). This story:

## ac 19: client never hardcodes a CIK — all CIK lookups go through get_cik(ticker)
parent:    story 1
origin:    dev
kind:      guardrail
state:    verified

## ac 20: only the requests library is imported in edgar_client.py — no edgartools, httpx, or other HTTP clients
parent:    story 1
origin:    dev
kind:      guardrail
state:    verified

## story 2: database schema initializer
summary:     Create the SQLite schema with all six tables and the six v1 bug-fixes applied.
description: Write build_schema.py that creates (or migrates idempotently) the six tables: filings, metrics, positions, filing_flags, scores, eightk_events. Apply the six bug-fixes from spike 5: UNIQUE(filing_id, dedup_key) on positions; company_name_raw column with parsed fields NULL until a name-parsing pass; asset_coverage_pct naming (not asset_coverage_ratio); scores table separate from metrics; filing_flags table for anomalies; realized_gain_loss column separate from unrealized_depreciation. Running the script twice on the same database must succeed without error.
inputs:      SPECIFICATION.md, STEP_5_DATABASE_FEASIBILITY.md
kind:        python
evidence:    STEP_S2_DATABASE_SCHEMA.md
state:    accepted
finding:  ```

## ac 21: all six tables exist with correct column names and FK constraints after build_schema.py runs on a fresh database
parent:    story 2
origin:    dev
kind:      assertion
state:    verified

## ac 22: build_schema.py is idempotent — running it twice on the same database raises no error and creates no duplicate columns
parent:    story 2
origin:    dev
kind:      guardrail
state:    verified

## story 3: metric extractor
summary:     Extract all nine per-filing metrics from XBRL and HTML sources and persist to the metrics table.
description: Write metric_extractor.py that, given a filing record, extracts: NAV per share (us-gaap:NetAssetValuePerShare, filter by end==period-end date — not by filed date); PIK income (discover per-ticker: InterestIncomeOperatingPaidInKind → InterestAndDividendIncomeOperatingPaidInKind); unrealized G/L (discover per-ticker across three candidate concepts, pick first with ≥3 recent obs); NII per share (InvestmentCompanyInvestmentIncomeLossPerShare); distributions per share (CommonStockDividendsPerShareDeclared for ARCC/TCPC; InvestmentCompanyDistributionToShareholdersPerShare for MFIC); asset coverage pct (XBRL for ARCC/MFIC; narrow HTML regex for TCPC); non-accrual cost% and FV% via HTML regex (strip all iXBRL tags first; handle both cost-first and FV-first sentence orderings); portfolio mark (InvestmentOwnedAtFairValue ÷ InvestmentOwnedAtCost); fee waiver dollar amount from income statement line (em dash = $0, not a text-presence flag). Write values into metrics; write anomalies into filing_flags.
inputs:      SPECIFICATION.md, STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md, STEP_3_EDGAR_CLIENT_CLASS.md, STEP_4_DATA_QUALITY_AND_COVERAGE.md, STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md, STEP_S1_EDGAR_CLIENT.md
kind:        python
evidence:    STEP_S3_METRIC_EXTRACTOR.md
state:    accepted
finding:  `metric_extractor.py` — a pure Python module that extracts all filing metrics from

## ac 23: NAV per share extraction filters by end == period-end date, not by filed date
parent:    story 3
origin:    dev
kind:      guardrail
state:    verified

## ac 24: non-accrual HTML regex strips iXBRL tags before matching and handles both cost-first and FV-first sentence orderings
parent:    story 3
origin:    dev
kind:      guardrail
state:    verified

## ac 25: fee waiver extraction reads the dollar amount from the income statement line; an em dash records $0 and not a text-presence flag
parent:    story 3
origin:    dev
kind:      guardrail
state:    verified

## story 4: signal scorer
summary:     Compute 11 stress signals from extracted metrics and write a composite score per ticker per period.
description: Write signal_scorer.py that reads from the metrics table and computes all 11 signals: (1) PIK % of total investment income, (2) PIK % QoQ change, (3) NAV per share QoQ change, (4) asset coverage pct vs threshold, (5) non-accrual cost%, (6) non-accrual FV%, (7) unrealized G/L QoQ change, (8) unrealized depreciation consecutive-quarter streak, (9) NII coverage ratio (NII per share ÷ distributions per share), (10) portfolio weighted-average mark, (11) fee waiver amount. Sum to a composite 0–11 stress score and write to the scores table. Produce a data_gap flag for any signal that cannot be computed due to missing data.
inputs:      SPECIFICATION.md, STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md, STEP_S3_METRIC_EXTRACTOR.md
kind:        python
evidence:    STEP_S4_SIGNAL_SCORER.md
state:    accepted
finding:  `signal_scorer.py` — computes all 11 BDC stress signals from extracted metrics,

## ac 26: all 11 signals produce a numeric value or a data_gap flag for TCPC Q1 2026 — no signal is silently absent
parent:    story 4
origin:    dev
kind:      assertion
state:    verified

## ac 27: NII coverage ratio is NII per share ÷ distributions per share — not NII ÷ total dollar distributions
parent:    story 4
origin:    dev
kind:      guardrail
state:    verified

## story 5: pipeline CLI and scoreboard
summary:     Wire edgar_client → extractor → scorer into a CLI and render a terminal scoreboard.
description: Write run_pipeline.py as the CLI entrypoint accepting an optional --tickers argument (default: ARCC MFIC TCPC). For each ticker: resolve CIK via EdgarClient.get_cik(), fetch the last four quarters of 10-Q/10-K filings, run metric_extractor, run signal_scorer, persist results to SQLite. After processing all tickers, render a markdown table to stdout showing per-ticker stress scores over the last four periods sorted by most-recent score descending. Include a warning row beneath any ticker that has data_gap flags. If a ticker has no 10-Q or 10-K filings, print a warning and skip it without aborting the run.
inputs:      SPECIFICATION.md, STEP_S1_EDGAR_CLIENT.md, STEP_S3_METRIC_EXTRACTOR.md, STEP_S4_SIGNAL_SCORER.md
kind:        python
evidence:    STEP_S5_PIPELINE_CLI.md
state:    accepted
decided_at: 2026-05-26T21:12:26

## ac 28: run_pipeline.py prints a warning and skips a ticker cleanly when it has no 10-Q or 10-K filings — it does not abort the run
parent:    story 5
origin:    dev
kind:      guardrail
state:    verified

## ac 29: scoreboard table is sorted by most-recent stress score descending
parent:    story 5
origin:    dev
kind:      assertion
state:    verified

----------- REQUEST COMPLETED -----------
