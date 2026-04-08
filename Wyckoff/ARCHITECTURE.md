# Architecture

**Version:** 20260408 V1
**Description:** Python/Flask local intelligence system with SQLite storage, signal computation pipeline, and browser UI

## Modules

| Module | Responsibility |
|--------|---------------|
| data/ | Download and cache end-of-day market data from yfinance and FRED into SQLite |
| signals/ | Compute feature matrix: volume analytics, momentum, Wyckoff phase, relative strength, macro |
| portfolio/ | Parse Fidelity CSV, map holdings to buckets, compute drift vs target weights |
| app/ | Flask web server — routes, Jinja2 templates, HTMX-driven interactions |
| scripts/ | CLI entry points: backfill.py, compute_signals.py, run_server.py |
| config/ | YAML configuration: universe.yaml, portfolio_mapping.yaml, target_weights.yaml |

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | / | Dashboard — all buckets with Wyckoff phase and composite scores |
| GET | /bucket/<bucket_name> | Bucket detail — price/volume chart with Wyckoff annotations, signal history |
| GET | /flows | Cross-asset flow heatmap and flow ranking table |
| GET | /portfolio | Holdings mapped to buckets, drift vs targets, rebalance suggestions |
| POST | /portfolio/upload | Upload Fidelity positions CSV |
| GET | /alerts | Chronological alert log — sell/buy/phase-change events |
| GET | /settings | System configuration — universe, thresholds, data management |
| POST | /settings | Save configuration changes |

## Directory Layout

```
WyckoffAccumulator/
├── app/
│   ├── __init__.py              Flask app factory
│   ├── routes/                  dashboard.py, bucket.py, flows.py, portfolio.py, alerts.py, settings.py
│   ├── templates/               base.html + one template per route
│   └── static/css/              custom.css (minimal overrides)
├── config/
│   ├── universe.yaml            Asset class universe (~40 tickers)
│   ├── portfolio_mapping.yaml   Ticker-to-bucket manual mappings
│   └── target_weights.yaml      Operator target allocations per bucket
├── data/
│   ├── db.py                    SQLite manager, schema creation, upsert helpers
│   ├── downloader.py            Download orchestrator (backfill + incremental)
│   ├── yfinance_client.py       yfinance wrapper with retry and batch support
│   ├── fred_client.py           FRED API wrapper
│   └── validate.py              Post-download validation (gaps, NaNs, stale tickers)
├── signals/
│   ├── calculator.py            Signal computation orchestrator
│   ├── volume.py                Family 1: volume analytics (V001–V013)
│   ├── momentum.py              Family 2: price momentum (P001–P015)
│   ├── wyckoff.py               Family 3: Wyckoff phase state machine (W001–W008)
│   ├── relative.py              Family 4: cross-asset relative strength (R001–R007)
│   ├── macro.py                 Family 5: regime/macro context (M001–M007)
│   ├── composite.py             Composite sell/buy score computation
│   └── backtest.py              Backtesting framework (hit rate, IC)
├── portfolio/
│   ├── parser.py                Fidelity CSV parser
│   ├── mapper.py                Ticker-to-bucket mapping with yfinance fallback
│   └── rebalance.py             Drift calculation and rebalance suggestion engine
├── scripts/
│   ├── backfill.py              CLI: python scripts/backfill.py --full | --incremental
│   ├── compute_signals.py       CLI: python scripts/compute_signals.py --date <date> | --backfill
│   └── run_server.py            CLI: python scripts/run_server.py → localhost:5000
├── tests/
│   ├── test_data/
│   ├── test_signals/
│   ├── test_portfolio/
│   └── conftest.py
└── db/
    └── wyckoff.db               SQLite database (gitignored)
```

## Open Questions

- Stack confirmed: Flask, SQLite, yfinance, fredapi, Plotly.js, HTMX, DataTables.js, Tailwind CSS — all CDN or stdlib; no npm/build step
