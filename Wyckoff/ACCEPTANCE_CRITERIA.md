# Acceptance Criteria: Wyckoff

Testable MUST / MUST NOT statements. Each line is a verifiable requirement.

## Requirements

### Data Pipeline
- [ ] `python scripts/backfill.py --full` MUST download 5 years of data for all configured tickers and populate the SQLite database.
- [ ] `python scripts/backfill.py --incremental` MUST add only new dates since last download.
- [ ] The database MUST NOT contain null `close` or `volume` values.
- [ ] Each ticker MUST have at least 1,200 trading days of data (5y × ~252 days).
- [ ] `config/universe.yaml` MUST be editable to add/remove tickers without code changes.
- [ ] Total backfill MUST complete in under 5 minutes on a reasonable internet connection.
- [ ] A validation report MUST print after each download showing row counts, date ranges, and any warnings.

### Signal Engine
- [ ] All signals in Families 1–5 for a single bucket and single date MUST compute in under 1 second.
- [ ] Full signal backfill for all ~40 buckets over 5 years MUST complete in under 10 minutes.
- [ ] The Wyckoff phase state machine MUST correctly identify at least 3 historical accumulation and 3 distribution phases in SPY against known market events (COVID-19 selloff/recovery, 2022 bear market).
- [ ] The backtesting framework MUST produce a report showing hit rates and information coefficients for sell and buy scores.
- [ ] Each signal family MUST be independently testable with unit tests covering edge cases (insufficient history, zero volume, missing data).

### Flask UI
- [ ] `python scripts/run_server.py` MUST launch the Flask app on localhost:5000.
- [ ] Dashboard MUST load in under 2 seconds with all ~40 buckets displayed.
- [ ] Bucket detail page MUST render a price/volume chart with at least one Wyckoff annotation visible on a known historical distribution period.
- [ ] Portfolio view MUST parse a Fidelity positions CSV and map at least 80% of holdings to asset class buckets automatically.
- [ ] Alerts page MUST show at least 3 different alert types from historical data.
- [ ] All pages MUST be functional without JavaScript enabled (HTMX degrades to full page loads).

## Build-ref
Last updated: 2026-04-08
