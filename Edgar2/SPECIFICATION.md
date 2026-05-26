# Edgar2 — Private Credit Stress Signals

| Field       | Value |
|-------------|-------|
| Version     | 20260525 V4 |
| Description | A SEC-filing stress-signal pipeline for private-credit BDCs, built under uncertainty via the oneshot2 spike process. |
| Build Mode  | oneshot2 (decompose by unknown, demo each milestone, reconcile decisions back here) |

## Intent

Read public SEC filings (10-Q / 10-K / 8-K) for a small set of Business Development
Companies (BDCs) and alternative-asset managers, and surface early **stress signals**
— deterioration that shows up in the filings quarters before a fund cuts its
distribution, caps redemptions, or is investigated. The first cut is a private,
local pipeline producing a scoreboard over time. This is a personal build, not a
trading desk: the bar is "beats an investor who has no time to read filings," not
"beats Millennium."

Full background (target universe, metrics, EDGAR endpoints) lives in the imported
`../Initial_Spec.md` and is not duplicated here.

## Why this is a oneshot2 project

The scope is small (a CLI pipeline over a handful of tickers) but the **unknowns are
large**: I do not yet know the right library, the data quality, whether the documents
are parseable, whether a useful DB can be built, what signals are computable, or
whether the thesis is differentiated. A single one-shot build would force the agent to
guess on all of these — which is exactly how the predecessor (`Edgar` v1) drifted: it
guessed, the guesses were corrected mid-build, and the corrections never made it back
into the spec.

Each unknown below is a milestone. The engineer runs a spike, produces inspectable
evidence, and stops; I review it as product owner, supply the context an agent cannot
have, and approve or redirect; the decision is then written back into this file.

## Scope (Phase 1)

- Python, local, SQLite. No web server for the *pipeline itself*.
- A small target universe to start (ARCC, MFIC, TCPC — see FSCO note below) — expand only once the
  pipeline proves out on a few.
- Output: a terminal/markdown scoreboard of per-ticker stress scores over time.
- **EDGAR access: direct REST API via `edgar_client.py`.** No third-party library beyond `requests`.
  `edgartools` was rejected on **dependency hygiene grounds**: v5.31.5 pulls in 21 transitive
  dependencies (httpx, httpxthrottlecache, pyarrow, orjson, stamina, pyrate-limiter, rank-bm25,
  rapidfuzz, truststore, unidecode, and others) with opaque
  rate-limiting behaviour and internal APIs that change between minor versions. The library wraps
  the same REST endpoints with no data advantage. Note: `edgartools` 5.31.5 *does* import and run
  on Python 3.10.12 + pandas 2.2.3 — the `AttributeError` failure recorded in earlier notes was
  not reproduced in Step 1 testing; the rejection stands on dependency grounds, not import failure.
  The direct REST API is equally capable, has no fragile dependencies, and gives explicit
  rate-limit control (0.12 s gap ≈ 8 req/s). Use `EdgarClient.get_cik(ticker)` for
  CIK resolution — do not hardcode CIK numbers.
- **FSCO excluded from Phase 1.** FSCO does not file 10-Q or 10-K. It is a registered closed-end
  fund; confirmed filing types: NPORT-P (monthly portfolio, 27 filings), N-CSR (semi-annual
  shareholder report, 13), N-CSRS (12), N-CEN (8). Zero 10-Q or 10-K on record. Cannot be handled
  by the standard pipeline without a separate N-CSR parser. Scope deferred to PO decision.
- **BDC-specific XBRL concepts require per-ticker discovery.** Standard us-gaap concepts cover NAV
  per share and unrealized gain/loss; PIK income uses a concept that varies by ticker. Non-accrual
  has **no XBRL representation** for any Phase 1 ticker — ARCC, MFIC, and TCPC have no
  company-specific namespaces (`arcc:`, `mfic:`, `tcpc:` are all absent from their companyfacts
  payloads). Non-accrual is extracted via HTML regex as `% of portfolio at cost / fair value`.
  PIK income: discover per-ticker — try `InterestIncomeOperatingPaidInKind` first, fall back to
  `InterestAndDividendIncomeOperatingPaidInKind`. Unrealized: discover per-ticker — first of
  `UnrealizedGainLossInvestmentDerivativeAndForeignCurrencyTransactionPriceChangeOperatingAfterTax`,
  `UnrealizedGainLossOnInvestments`, `GainLossOnInvestments` with ≥3 recent quarterly obs wins.

Out of scope for Phase 1: live trading, real-time 8-K alerting, a hosted UI, the full
14-ticker universe.

## Confirmed CIK Numbers (all verified against EDGAR 2026-05-25)

| Ticker | Name | CIK |
|--------|------|-----|
| ARCC | Ares Capital Corporation | 0001287750 |
| MFIC | MidCap Financial Investment Corp | 0001278752 |
| TCPC | BlackRock TCP Capital Corp | 0001370755 |
| FSCO | FS Credit Opportunities Corp | 0001568194 |
| OBDC | Blue Owl Capital Corporation | 0001655888 |
| BXSL | Blackstone Secured Lending Fund | 0001736035 |
| CGBD | Carlyle Secured Lending | 0001544206 |
| TPVG | TriplePoint Venture Growth | 0001580345 |
| APO | Apollo Global Management | 0001858681 |
| ARES | Ares Management Corp | 0001176948 |
| BX | Blackstone Inc | 0001393818 |
| BLK | BlackRock Inc | 0002012383 |
| OWL | Blue Owl Capital Inc | 0001823945 |
| KKR | KKR & Co | 0001404912 |

Note: The CIK table in `../Initial_Spec.md` had 8 of 11 entries wrong (cross-assigned between
tickers). The above are authoritative. The pipeline uses `EdgarClient.get_cik(ticker)` for
live resolution — hardcoded CIKs are reference only.

## Open Questions

These are the milestones. Each bullet becomes one spike step
(`bash bin/build_plan.sh Edgar2 spikes`). Resolved answers get written back into the
Scope / Intent sections above and the bullet annotated `RESOLVED:`.

- **Library discovery** — RESOLVED: Use direct EDGAR REST API via `edgar_client.py` (no edgartools). `edgartools` 5.31.5 rejected on dependency hygiene grounds (21 transitive deps, opaque rate-limiting, no data advantage over direct REST). Note: the previously recorded import failure (`AttributeError` on Python 3.10 + pandas 2.x) did *not* reproduce in Step 1 testing (Python 3.10.12 + pandas 2.2.3) — the rejection reason is dependency hygiene, not import breakage. Direct REST to `data.sec.gov` is equivalent and stable. Rate limit: 0.12 s gap confirmed safe. All 4 Phase 1 CIKs confirmed live. FSCO: zero 10-Q/10-K filings (NPORT-P + N-CSR only) — excluded from standard pipeline.
- **Connectivity and processing validity** — RESOLVED: Yes. Direct REST fetches 10-Q, 10-K, 8-K for ARCC, MFIC, TCPC. XBRL via `companyfacts` endpoint: 185 / 165 / 155 us-gaap concepts for ARCC / MFIC / TCPC. `NetAssetValuePerShare` confirmed 20 / 20 / 22 distinct quarterly end-dates; `InvestmentCompanySeniorSecurityIndebtednessAssetCoverageRatio` confirmed 11 / 9 quarterly end-dates for ARCC / MFIC but **NOT FOUND for TCPC** (HTML fallback required); distributions per share — ARCC/TCPC use `CommonStockDividendsPerShareDeclared`, MFIC uses `InvestmentCompanyDistributionToShareholdersPerShare`. Asset coverage stored as pure decimal (1.88 = 188%) — needs ×100. Non-accrual: **NOT in XBRL for any ticker** — HTML-only. Documents: primary iXBRL HTML **17–37 MB per 10-Q** (not ~0.9 MB as earlier noted — inline XBRL embeds the full filing HTML plus all tags). FSCO: 0 × 10-Q. XBRL extraction nuance: NAV per share is an instantaneous concept — filter by `end` == target period-end date, not by `filed` date, to avoid returning comparatives. See `evidence/STEP_2_CONNECTIVITY_AND_PROCESSING_VALI.md`.
- **EDGAR client class** — RESOLVED: `edgar_client.py` in build workspace. `get_cik()`, `get_filings()`, `get_document()`, `get_xbrl_facts()`. Rate limit baked in. Only `requests` needed. See `evidence/STEP_3_EDGAR_CLIENT_CLASS.md`.
- **Data quality and coverage** — RESOLVED: XBRL is the primary extraction path for NAV per share, PIK income, and unrealized gain/loss. HTML regex is the fallback for non-accrual (all 3 tickers — no XBRL non-accrual concept exists in the `companyfacts` API for any of them; `mfic:PercentageOnInvestmentsOnNonAccrualAtAmortizedCost` appears in inline iXBRL tag attributes but is not surfaced by `get_xbrl_facts()`). Coverage 3 BDCs × 4 quarters: NAV per share 4/4 (`us-gaap:NetAssetValuePerShare`, same concept all tickers); PIK interest income 4/4 (ARCC/MFIC use `InterestIncomeOperatingPaidInKind`; TCPC uses `InterestAndDividendIncomeOperatingPaidInKind` — discover per-ticker, do not hardcode); unrealized gain/loss 4/4 (ARCC/MFIC use `UnrealizedGainLossInvestmentDerivativeAndForeignCurrencyTransactionPriceChangeOperatingAfterTax`; TCPC uses `UnrealizedGainLossOnInvestments` — discover per-ticker); non-accrual 4/4 for all 3 tickers via HTML regex. PIK balance: `us-gaap:PaidInKindInterest` present for ARCC and MFIC; absent for TCPC. No `mfic:PaidInKindBalance` concept exists; MFIC's `PaidInKindInterest` values are identical to its PIK income values (not a separate balance concept). Non-accrual HTML extraction notes: (1) strip all iXBRL tags before applying regex — MFIC embeds the numeric value inside `<ix:nonFraction>` closing tags, so raw-bytes pattern matching fails; (2) TCPC's MD&A sentence is FV-first ("X% at fair value and Y% at cost") — extractor needs both orderings; ARCC/MFIC are cost-first. Q1 2026 values: ARCC 2.1%/1.2%, MFIC 5.3%/3.5%, TCPC 7.6%/2.8% (at amortized cost / at fair value). See `evidence/STEP_4_DATA_QUALITY_AND_COVERAGE.md`.
- **Database feasibility** — RESOLVED: Six tables: `filings`, `metrics`, `positions`, `filing_flags`, `scores`, `eightk_events`. Six v1 bugs fixed: (1) position dedup key — XBRL SoI produces 3–5 duplicate rows per investee, now blocked by `UNIQUE(filing_id, dedup_key)`; (2) `positions.company_name_raw` preserves the raw concatenated XBRL label; parsed fields (`issuer_name`, `sector`, `instrument_type`) are NULL until a name-parsing pass; (3) `asset_coverage_pct` renamed from `asset_coverage_ratio` — v1 regex returned nonsense values (3.0, 8.0 instead of ~165%); (4) `scores` table separated from `metrics`; (5) `filing_flags` table replaces packed `extraction_notes` strings; (6) `realized_gain_loss` separated from `unrealized_depreciation` — v1 stored same value for both due to a shared XBRL concept. Schema loads and passes FK integrity. New findings from Step 5 spike: (a) ARCC unrealized gain/loss observations are absent from step4_raw.json — concept name confirmed in Step 4 but observations not saved; extractor step must re-fetch; (b) MFIC unrealized data is 2022-vintage only (2 rows) in step4_raw.json; same re-fetch needed; (c) XBRL companyfacts can have multiple observations for the same `(period, form_type)` pair — extractor must select latest `filed` date to avoid NAV value drift. Schema: `evidence/edgar2_spike.db`; load script: `build_schema.py` in build workspace. See `evidence/STEP_5_DATABASE_FEASIBILITY.md`.
- **Signal feasibility and scale direction** — RESOLVED pending PO confirmation of 7 open questions (thresholds, score direction, top-15 scope). Tested against TCPC (3 quarters v1 DB + live XBRL for Q1 2026). **All 11 signals are extractable** — prior "2 not computable" claim is corrected. **5 signals working:** PIK % of investment income (XBRL), PIK % QoQ change (derived), weighted avg portfolio mark (XBRL SOI totals), unrealized change (XBRL, Q1 2026 only — earlier quarters require v1 bug #6 fix), unrealized depreciation streak (derived). **4 broken but fixable:** (a) NAV per share — XBRL concept `NetAssetValuePerShare` confirmed present (TCPC: $6.72 Mar-26, $7.07 Dec-25), v1 extractor searched wrong label; (b) asset coverage ratio — v1 HTML regex captured "3" from "168.3%", real TCPC value confirmed as 168.3% in filing text, fix is updated regex; (c) top-15 position marks — per-position cost (638 XBRL rows) and FV (726 rows) both present in SOI, extractor does not pair them; (d) fee waiver — v1 detected text presence rather than current-period amount, causing false positives (TCPC Q1 2026 fee waiver amount = $0; Q1 2025 comparative = $1,827,948). **2 previously "not computable" — now confirmed extractable:** non-accrual % at cost — HTML prose regex confirmed working (Step 4 + Step 6 re-verified; TCPC Q1 2026: 7.6% at cost, 2.8% at FV); v1 extractor searched for table structure instead of prose; NII distribution coverage — XBRL concepts confirmed (`InvestmentCompanyInvestmentIncomeLossPerShare` + `CommonStockDividendsPerShareDeclared`; TCPC Q1 2026 coverage = 1.29x); v1 used `EarningsPerShareBasic` (wrong — includes unrealized). TCPC Q1 2026 theoretical score: 7 points (High band) on corrected data; 9 if unrealized streak; 14+ if DOJ 8-K flagged. Scale directions and thresholds pending PO confirmation — see `evidence/STEP_6_SIGNAL_FEASIBILITY_AND_SCALE_DIR.md`.
- **Business thesis** — RESOLVED: GO. Bloomberg/Calcbench/Sentieo deliver raw data or analyst workflow tools; none compute a longitudinal, BDC-specific stress-signal scoreboard. The edge is zero ongoing cost, BDC-calibrated signals (NAV compression, PIK %, non-accrual creep, distribution coverage), and automated quarterly monitoring that beats a retail investor who does not read filings. The bar is "beats not reading filings at all," not "beats Millennium." Phase 1 scope confirmed as written — no changes required.
