# FEATURE: Metric Extraction and Analysis

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Extract all 12 metrics from the filing universe using regex, table parsing, and LLM-assisted narrative scoring. Update the JSONL signal rules file with LLM-discovered patterns. |
| Phase       | 2 |

## Trigger

`bin/analyze.sh [--ticker ARCC] [--filing-id 42] [--reprocess]`

Processes all filings where `processed = false` unless a specific ticker or filing is specified.

## Extraction Pipeline

### Stage 1: Document Structure
1. Load raw HTML from `data/raw/`.
2. Parse with BeautifulSoup + lxml.
3. Identify section boundaries: Part I Item 1 (financials), Part I Item 2 (MD&A), Notes to FS.
4. Extract all tables using `pandas.read_html()`.

### Stage 2: Regex + Table Extraction (Metrics 1-9, 11-12)
Apply patterns from `src/metrics/extractor.py`. Key regex groups:

```python
pik_patterns      = [r'payment.{0,5}in.{0,5}kind', r'\bPIK\b', r'PIK interest income']
non_accrual       = [r'non.accrual', r'nonaccrual', r'placed on non-accrual']
fee_waiver        = [r'waiv(ed|er|ing).{0,30}fee', r'voluntarily waived']
coverage_ratio    = [r'asset coverage ratio.{0,30}\d+\.?\d*\s*%']
extension         = [r'extend(ed|ing).{0,30}maturit', r'amend and extend', r'forbearance']
redemption_limits = [r'redemption.{0,30}limit', r'cap(ped|ping).{0,30}redemption']
```

### Stage 3: Schedule of Investments Parser (Metric 10)
1. Locate the Schedule of Investments exhibit.
2. Extract all positions: company name, investment type, cost, fair value.
3. Compute individual marks (fair_value / cost * 100).
4. Flag positions below 85% mark, on non-accrual, or with PIK notation.
5. Extract maturity dates where available.
6. Rank positions by fair value; store top 15 as `position_rank 1-15`.

### Stage 4: LLM-Assisted Narrative Scoring
For text sections that do not yield a clean numeric extraction:
1. Extract the relevant paragraph(s).
2. Send to LLM with the metric definition and scoring rubric.
3. LLM returns: numeric score + reasoning + candidate signal phrase.
4. If the signal phrase is novel and useful → append to `rules/signals.jsonl`.
5. Re-run extraction for the filing using updated JSONL rules.

## JSONL Signal Rule Format

```json
{"metric": "fee_waiver", "pattern": "voluntarily waived its management fee", "score_delta": 3, "confidence": "high", "source": "TCPC_2026Q1", "added": "2026-05-19"}
```

## Cross-Validation (writes to metrics.extraction_confidence)

After extraction:
- Compare computed `nav_per_share` to stated NAV.
- Compare Schedule totals to balance sheet.
- Compare PIK income in income statement to PIK notation in Schedule.

## Success Criteria

- All 12 metrics populated (or `null` with a note) for each processed filing.
- `extraction_confidence` is `high` or `medium` for at least 70% of Tier 1 filings.
- LLM scoring applied to at least one hard-to-parse filing (TCPC Q4 2025) and produces a non-zero score delta.
- Updated `rules/signals.jsonl` has at least 3 entries after processing the MVP dataset.

## Open Questions

- What is the right LLM for the scoring step — claude API call, or local model (ollama)? Depends on PreReq 2 discussion on on-machine feasibility.
- How many JSONL rule updates per filing run is too many? Should there be a review gate before JSONL changes are committed?
