# ARCHITECTURE: myEdgar

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Directory layout, module responsibilities, and technology stack for the Edgar stress intelligence system. |

## Implementation Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | Python 3.11+ | Primary |
| Storage | SQLite (dev) → PostgreSQL (production) | Phase 1 uses SQLite |
| HTTP | httpx or requests | For EDGAR API calls |
| HTML parsing | BeautifulSoup4 + lxml | Primary document parser |
| Table parsing | pandas read_html() | Schedule of Investments extraction |
| Scheduling | APScheduler or cron | 8-K daily monitor |
| Terminal UI | Rich | Colorized scoreboard |
| HTML reports | Jinja2 | Phase 2 report generation |
| Signal rules | JSONL file | Language-based signal patterns (LLM-discovered) |

## Directory Layout

```
edgar/
  bin/
    common.py              Shared OperationContext (from Prototyper template)
    download.sh / .py      CLI: download filings for target tickers
    analyze.sh / .py       CLI: run metric extraction on downloaded filings
    score.sh / .py         CLI: compute Red Flag Index scores
    monitor.sh / .py       CLI: daily 8-K monitor (scheduled)
    report.sh / .py        CLI: generate scoreboard output
    test.sh                Test runner
  src/
    edgar/
      downloader.py        EDGAR API calls, filing index, raw HTML storage
      parser.py            Document structure, section extraction
      schedule_parser.py   Schedule of Investments position-level parsing
    metrics/
      extractor.py         12-metric extraction logic (regex + pandas)
      scorer.py            Red Flag Index computation
      llm_scorer.py        LLM-assisted narrative scoring → JSONL rule updates
      divergence.py        Public vs. private mark comparison (Phase 3)
    db/
      schema.sql           Table definitions
      models.py            ORM or lightweight DB helpers
    reports/
      scoreboard.py        Terminal scoreboard (Rich)
      deep_dive.py         Per-ticker detailed report
      alerts.py            Alert dispatch
    main.py                Entry point
  data/
    raw/                   Downloaded HTML filings (gitignored)
    db/                    SQLite database file (gitignored)
  reports/                 Generated report output
  rules/
    signals.jsonl          LLM-discovered language signal patterns (committed)
  config.yaml              Target tickers, thresholds, API settings
  requirements.txt
  METADATA.md
  AGENTS.md
```

## EDGAR API Endpoints

| Purpose | Endpoint Pattern |
|---------|----------------|
| Company submissions | `https://data.sec.gov/submissions/CIK{10-digit-CIK}.json` |
| Filing search | `https://efts.sec.gov/LATEST/search-index?q=...&forms=10-Q` |
| Full-text search | `https://efts.sec.gov/LATEST/search-index?q=...&forms=10-Q&dateRange=...` |
| Filing index | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=...` |
| Filing content | `https://www.sec.gov/Archives/edgar/data/{CIK}/{accession}/{doc}.htm` |

## Target Universe

### Tier 1 — Publicly Traded BDCs (Primary)
ARCC, MFIC, TCPC, FSCO, OBDC, BXSL, CGBD, TPVG

### Tier 2 — Management Company Stocks (Potential Shorts)
APO, ARES, BX, BLK, OWL, KKR

### Tier 3 — Non-Traded / Interval Funds (8-K monitoring only)
BCRED, Ares Direct Lending, Apollo Direct Lending

## Open Questions

- Should `config.yaml` include the full CIK mapping table, or should CIKs be looked up dynamically from EDGAR on first run?
- Is SQLite sufficient for Phase 1 given the filing volume (8 quarters × ~14 tickers × multiple filing types)?
- Where do the JSONL signal rules live in relation to git? They evolve over time — should they be a separate file tracked carefully or embedded in the DB?
