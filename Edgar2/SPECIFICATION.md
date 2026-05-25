# Edgar2 — Private Credit Stress Signals

| Field       | Value |
|-------------|-------|
| Version     | 20260521 V1 |
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
- A small target universe to start (e.g. ARCC, MFIC, TCPC, FSCO) — expand only once the
  pipeline proves out on a few.
- Output: a terminal/markdown scoreboard of per-ticker stress scores over time.

Out of scope for Phase 1: live trading, real-time 8-K alerting, a hosted UI, the full
14-ticker universe.

## Open Questions

These are the milestones. Each bullet becomes one spike step
(`bash bin/build_plan.sh Edgar2 spikes`). Resolved answers get written back into the
Scope / Intent sections above and the bullet annotated `RESOLVED:`.

- **Library discovery** — Which Python EDGAR libraries exist (edgartools, sec-edgar, direct HTTP), what are their capabilities and the SEC rate limits, and which should Edgar2 standardize on? Verify the target tickers' CIK numbers against EDGAR (the v1 spec had 10 of 14 wrong).
- **Connectivity and processing validity** — Can we actually fetch real 10-Q/10-K/8-K filings for the starter tickers, respecting rate limits, and store them? Prove it on a few real filings end to end.
- **EDGAR client class** — Build a small, reusable client wrapper (fetch filings by ticker/form/date, return raw documents) with a worked usage demo, so later steps share one access path.
- **Data quality and coverage** — For the fetched filings, what is actually parseable? Which target fields (NAV, non-accruals, PIK income, portfolio marks) can be reliably extracted, from XBRL vs HTML, and what is the coverage across tickers and quarters?
- **Database feasibility** — Given the real extracted data, what schema actually holds it? Build and load a minimal SQLite schema from real samples; identify what does not fit cleanly.
- **Signal feasibility and scale direction** — Which stress signals can actually be computed from the available data, and for each, which direction is "bad"? (e.g. is a higher number worse?) The product owner must confirm scale direction — the agent cannot infer it.
- **Business thesis** — RESOLVED: GO. Bloomberg/Calcbench/Sentieo deliver raw data or analyst workflow tools; none compute a longitudinal, BDC-specific stress-signal scoreboard. The edge is zero ongoing cost, BDC-calibrated signals (NAV compression, PIK %, non-accrual creep, distribution coverage), and automated quarterly monitoring that beats a retail investor who does not read filings. The bar is "beats not reading filings at all," not "beats Millennium." Phase 1 scope confirmed as written — no changes required.
