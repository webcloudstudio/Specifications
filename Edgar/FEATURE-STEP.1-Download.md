# FEATURE: EDGAR Downloader

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | CLI-driven downloader for 10-Q, 10-K, and 8-K filings from SEC EDGAR for the target BDC universe. |
| Phase       | 1 |

## Trigger

`bin/download.sh [--ticker ARCC] [--type 10-Q] [--quarters 8]`

Without arguments: download all pending filings for all tickers in `config.yaml`.

## Sequence

1. Load target ticker list and CIK map from `config.yaml`.
2. For each ticker:
   a. GET `https://data.sec.gov/submissions/CIK{cik}.json` — returns filing index.
   b. Extract accession numbers for the requested filing type and date range.
   c. For each accession number not already in `filings` table:
      - GET filing index page to identify the primary document.
      - Download raw HTML to `data/raw/{ticker}/{filing_type}/{accession}/`.
      - Insert row into `filings` table with `processed = false`.
3. Respect rate limits: max 10 requests/second to EDGAR (recommended by SEC).
4. Log progress: filings downloaded, skipped (already present), and errors.

## Idempotency

- Already-downloaded filings (matching accession number in DB) are skipped.
- `--force` flag re-downloads and overwrites.

## 8-K Daily Monitor

When called with `--type 8-K --mode monitor`, polls EDGAR for new 8-K filings for all tickers since the last run. Designed to be called by cron/APScheduler daily.

8-K keyword flagging: any 8-K containing: "distribution", "redemption", "waiver", "investigation", "non-accrual", "asset coverage", "maturity extension", "amendment" → set `flagged = true` in `eightk_events`.

## Success Criteria

- Downloads last 8 quarters of 10-Q for all Tier 1 tickers without rate-limit errors.
- All downloaded filings are tracked in the `filings` table.
- 8-K monitor correctly flags at least one test filing containing a keyword.
- `bin/test.sh` includes a unit test that mocks the EDGAR API and verifies the download logic.

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| EDGAR rate limit (429) | Exponential backoff; retry up to 3 times |
| Network timeout | Log error; mark filing as failed; continue with next |
| Invalid CIK | Log warning; skip ticker; add to `data/prereq/library_discovery.md` |
| Disk full | Log CRITICAL; stop download; alert via heartbeat |

## Open Questions

- Should raw HTML be stored in the filesystem or in the DB as a blob? (Filesystem preferred — filings can be large.)
- Should we download 10-K separately or treat it as a higher-priority alternative to 10-Q when 10-Q is unavailable?
