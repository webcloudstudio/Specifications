# Edgar2 — Private Credit Stress Signals

| Field       | Value |
|-------------|-------|
| Version     | 20260525 V3 |
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
  `edgartools` was rejected — it fails to import on Python 3.11.0rc1 (invalid version string in
  `core.py`) and on Python 3.10 with pandas 2.x (`AttributeError: module 'pandas' has no attribute
  'DataFrame'`). The direct REST API is equally capable, has no fragile dependencies, and gives
  explicit rate-limit control (0.12 s gap ≈ 8 req/s). Use `EdgarClient.get_cik(ticker)` for
  CIK resolution — do not hardcode CIK numbers.
- **FSCO excluded from Phase 1 pending PO decision.** FSCO does not file 10-Q or 10-K. It is a
  registered closed-end fund filing N-CEN and N-2 only. It cannot be handled by the standard
  pipeline without a separate handler.
- **BDC-specific XBRL concepts are not standardized.** Non-accrual and PIK concepts use company-
  specific namespaces (e.g. `arcc:`, `tcpc:`, `bxsl:`). Step 4 (data quality) will resolve
  whether per-ticker concept maps or HTML fallback is the right approach.

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
tickers). The above are authoritative. The pipeline uses `Company(ticker)` for resolution so
hardcoded CIKs are reference only.

## Open Questions

These are the milestones. Each bullet becomes one spike step
(`bash bin/build_plan.sh Edgar2 spikes`). Resolved answers get written back into the
Scope / Intent sections above and the bullet annotated `RESOLVED:`.

- **Library discovery** — RESOLVED: Use edgartools v5.31.5+. It handles rate limiting (8 req/s), XBRL parsing, and all required form types. `Company(ticker)` resolves CIK automatically — no manual CIK management. All 14 target-ticker CIKs verified and recorded above (8 of 11 spec CIKs were wrong). FSCO does not file 10-Q/10-K; excluded from Phase 1 pending PO decision on whether to build a separate N-CEN handler.
- **Connectivity and processing validity** — RESOLVED: Yes. `edgartools` fetches 10-Q, 10-K, and 8-K for ARCC, MFIC, TCPC without 429 errors or blocks. XBRL parsed successfully: `get_total_assets()`, `get_total_liabilities()`, `get_net_income()` return correct values for all three tickers. `get_stockholders_equity()` returns `None` for some BDC filers (MFIC); workaround is `financials.xb.facts.get_facts_by_concept("us-gaap:StockholdersEquity")` filtered to `period_type == 'instant'`. `us-gaap:NetAssetValuePerShare` is available in XBRL for BDC filers. Local disk cache at `~/.edgar/` means subsequent runs skip network. First-fetch timing: 4–20s per filing; repeat <30s per ticker. FSCO has 0 × 10-Q, 0 × 10-K — excluded from this path (see library discovery note). Text content accessible via `filing.doc.get_sec_section("part_i_item_2")` (MD&A as plain string) for future LLM-based extraction.
- **EDGAR client class** — Build a small, reusable client wrapper (fetch filings by ticker/form/date, return raw documents) with a worked usage demo, so later steps share one access path.
- **Data quality and coverage** — RESOLVED: XBRL is the primary extraction path; HTML regex is the fallback for non-accrual only. Coverage across 3 BDCs × 4 quarters: NAV per share 4/4 (standard `us-gaap:NetAssetValuePerShare`); PIK interest income 4/4 (`us-gaap:InterestIncomeOperatingPaidInKind`); unrealized gain/loss 4/4 (various); non-accrual 4/4 for ARCC and MFIC via company-specific XBRL concepts, HTML regex fallback for TCPC (no XBRL concept present). Non-accrual and PIK balance concept names are company-specific — discover per-ticker at first-fetch time, do not hardcode. MFIC also exposes `mfic:PaidInKindBalance` (cumulative PIK capitalized balance) — treat as a first-class signal. FSCO files NPORT-P XML + N-CSR only, no 10-Q — quarterly NAV per share and non-accrual unavailable — FSCO scope deferred to PO. All four original spec CIKs were wrong; corrected table is above.
- **Database feasibility** — RESOLVED: Six tables: `filings`, `metrics`, `positions`, `filing_flags`, `scores`, `eightk_events`. Six v1 bugs fixed: (1) position dedup key — XBRL SoI produces 3–5 duplicate rows per investee, now blocked by `UNIQUE(filing_id, dedup_key)`; (2) `positions.company_name_raw` preserves the raw concatenated XBRL label; parsed fields (`issuer_name`, `sector`, `instrument_type`) are NULL until a name-parsing pass; (3) `asset_coverage_pct` renamed from `asset_coverage_ratio` — v1 regex returned nonsense values (3.0, 8.0 instead of ~165%); (4) `scores` table separated from `metrics`; (5) `filing_flags` table replaces packed `extraction_notes` strings; (6) `realized_gain_loss` separated from `unrealized_depreciation` — v1 stored same value for both due to a shared XBRL concept. 9 of 19 metric fields reliably populated from XBRL for TCPC; NAV per share, non-accrual, distributions per share, asset coverage, and realized gain/loss are consistently NULL and require extractor fixes. Schema: `evidence/edgar2_spike.db`; load script: `build_schema.py` in build workspace.
- **Signal feasibility and scale direction** — Which stress signals can actually be computed from the available data, and for each, which direction is "bad"? (e.g. is a higher number worse?) The product owner must confirm scale direction — the agent cannot infer it.
- **Business thesis** — RESOLVED: GO. Bloomberg/Calcbench/Sentieo deliver raw data or analyst workflow tools; none compute a longitudinal, BDC-specific stress-signal scoreboard. The edge is zero ongoing cost, BDC-calibrated signals (NAV compression, PIK %, non-accrual creep, distribution coverage), and automated quarterly monitoring that beats a retail investor who does not read filings. The bar is "beats not reading filings at all," not "beats Millennium." Phase 1 scope confirmed as written — no changes required.
