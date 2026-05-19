# Intent: myEdgar

## Goals

- Replicate the analytical process used by top fixed-income trading desks (Millennium, Citadel) to systematically read SEC filings across the private credit universe and identify stress signals before they are widely recognized.
- Generate actionable long/short trading signals by detecting deterioration in private credit fund books — specifically Business Development Companies (BDCs) and alternative asset managers — using publicly available EDGAR data that most investors do not systematically process.
- Build a scoring system (Red Flag Index) that quantifies stress across 12 defined metrics extracted from 10-Q, 10-K, and 8-K filings.
- Learn over time: use LLM scoring to recognize stress language that is hard to parse with rules alone, then update the rules engine (stored as JSONL) with discovered signal patterns.
- Provide a terminal scoreboard and eventually a UI with KPIs, trend charts, and automated buy/sell signal reports.

## Core Thesis

Private credit funds mark illiquid assets quarterly using internal models with every incentive to be optimistic. Stress signals appear in filings many quarters before a fund cuts its distribution, caps redemptions, or faces regulatory investigation. The BlackRock TCP Capital DOJ investigation (May 2026) is an example of the endpoint — this system is designed to find the beginning.

## Constraints

- **Discussion gate**: The PROJECT PLAN requires back-and-forth discussion with the author before any code is built. PreReqs 1 and 2 must be completed first (library discovery, research, and plan iteration).
- Data is sourced entirely from public SEC EDGAR APIs — no paid data feeds in Phase 1.
- The system must respect EDGAR rate limits and implement appropriate throttling.
- Language-based signals (narrative text in MD&A) are initially rated by an LLM into scores; the LLM output then trains/updates a rules file (JSONL) for deterministic re-scoring.
- SQLite for development; PostgreSQL path planned for production (Phase 3+).
- This system is for informational and research purposes. Not investment advice.

## Success Criteria

- Phase 1 MVP: EDGAR downloader, 5-metric parser, SQLite storage, terminal scoreboard, 8-K daily monitor.
- Validation: System correctly identifies TCPC (score spikes 10+), BCRED non-accrual flag, Ares redemption cap alert, and BlackRock DOJ investigation alert when fed the relevant filings.
- Scoring system produces clear buy/sell/hold signals matching the target universe tier structure.
- LLM-assisted parsing correctly identifies at least 80% of stress signals that resist regex-only extraction.

## Open Questions

- **PreReq 1**: What Python libraries exist for EDGAR data? (edgar, sec-api, edgartools, full-text-search?) Which provide free access without rate-limit risk?
- **PreReq 2**: Is this type of EDGAR analysis already a product? What do comparables (Calcbench, Sentieo, Visible Alpha) offer vs. what we can build for free?
- What is the best on-machine approach for LLM-assisted signal learning? (local model vs. API calls, on-laptop feasibility)
- Should the scoring JSONL rules file be versioned separately so signal updates are auditable?
- How should the system handle CIK mismatches (e.g. MFIC and OBDC share CIK 0001655888 in the spec — likely a data error)?
