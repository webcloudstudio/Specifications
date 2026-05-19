# FEATURE: Data Validation

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Validate downloaded filings for completeness and consistency before metric extraction begins. |
| Phase       | 1 |

## Trigger

`bin/analyze.sh --validate [--ticker ARCC]`

Run automatically before extraction begins; also available as a standalone command.

## Validation Checks

### File-Level Checks
- Raw HTML file exists at the expected path in `data/raw/`.
- File size > 10KB (suspiciously small files likely incomplete downloads).
- File is valid HTML (BeautifulSoup parses without error).

### Metadata Checks
- Accession number format matches EDGAR standard (e.g. `0001278752-26-000012`).
- `period_end` falls within an expected fiscal quarter range.
- `filed_date` is within 75 days of `period_end` (regulatory requirement for 10-Q/10-K).

### Cross-Validation (run during extraction, reported here)
- `total_fair_value` from Schedule of Investments matches balance sheet total.
- Computed `nav_per_share` matches the value stated in the filing.
- PIK income appears in both the income statement and Schedule footnotes.

Confidence levels: **high** (all 3 pass), **medium** (2 of 3 pass), **low** (1 or 0 pass). Stored in `metrics.extraction_confidence`.

## Output

- `data/prereq/validation_report.md` — per-filing pass/fail table.
- Rows with validation failures are marked `processed = false` and logged.

## Success Criteria

- All 8 quarters of TCPC 10-Q pass file-level and metadata checks.
- Cross-validation correctly flags at least one fabricated test case with a known mismatch.

## Open Questions

- Should the validation report include a severity level (error vs. warning) for each check?
- What is the minimum acceptable file size? 10KB is a guess — calibrate against real filings.
