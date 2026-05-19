# FEATURE: Library Discovery

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Evaluate existing Python libraries for EDGAR data access before building anything. |
| Phase       | PreReq |

## Purpose

This is a research task, not a coding task. Before writing any downloader code, determine what is freely available so we do not reinvent what already works.

## Scope of Research

Candidate libraries and APIs to evaluate:
- `edgar` (pypi: edgar) — CIK lookup, filing index, document parsing
- `edgartools` — SEC EDGAR API wrapper
- `sec-api` — commercial but has a free tier
- `python-edgar` — older library
- Direct EDGAR REST API (`data.sec.gov/submissions/`) — no library, raw HTTP
- `full-text-search` endpoint at `efts.sec.gov`

## Evaluation Criteria

For each candidate, test and document:
1. **Connectivity**: Does it connect to EDGAR without authentication?
2. **Rate limits**: What limits apply? How does the library handle them?
3. **Data available for free**: CIK lookup? Filing index? Raw HTML download? Parsed text? Tables?
4. **10-Q / 10-K / 8-K support**: Can it fetch all three filing types?
5. **Schedule of Investments**: Can it extract structured table data from exhibits?
6. **Sample data**: Run against TCPC (CIK 0001452936) for the 4 most recent 10-Q filings and document what you get.

## Output

A short discovery report (Markdown) committed to `data/prereq/library_discovery.md` covering:
- Recommended library(ies) with rationale
- Known gaps (what must be handled with raw HTTP fallback)
- Rate limit strategy
- Any CIK data errors found (e.g. MFIC/OBDC conflict noted in DATABASE.md)

## Success Criteria

- At least one free path to downloading a 10-Q HTML filing for TCPC is confirmed working.
- Rate limit behavior is documented with a safe request-per-second recommendation.
- The architecture decision (which library to use) is made and approved before STEP.1 begins.

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| All libraries are commercial / rate-limited | Fall back to direct EDGAR REST API with manual rate limiting |
| CIK lookup returns wrong entity | Flag in report; resolve by manual lookup at sec.gov |

## Open Questions

- Does `edgartools` parse Schedule of Investments tables, or only document metadata?
- Is the EDGAR full-text search API stable and suitable for production polling?
