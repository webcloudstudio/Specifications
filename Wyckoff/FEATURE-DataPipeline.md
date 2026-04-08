# Feature: Data Pipeline

**Trigger:** Manual CLI (`python scripts/backfill.py --full` or `--incremental`) or Settings page button

## Sequence

1. Load asset universe from `config/universe.yaml`
2. Batch-download all active tickers via yfinance: `yf.download(tickers_list, period="5y", group_by="ticker", threads=True)`
3. For incremental: query last stored date per ticker; download only delta since that date
4. Drop rows with null `close` or `volume`
5. Upsert into `market_data`
6. Download FRED series (DGS10, DGS2, T10Y2Y, CPIAUCSL, ICSA, M2SL, FEDFUNDS) via fredapi; upsert into `macro_data`
7. Write download result (row count, date range, any errors) to `download_log`
8. Run post-download validation: flag gaps, stale tickers, NaN counts
9. Print validation report to terminal

## Reads

- config/universe.yaml
- market_data (last date per ticker, incremental only)

## Writes

- market_data
- macro_data
- download_log

## Error Handling

- Ticker download failure: log and continue — do not abort batch
- Zero rows on weekday: flag in download_log for manual review
- FRED API failure: log; macro data is supplementary, do not abort

## Open Questions

- OQ5: FRED API key — register at fred.stlouisfed.org during setup if not present
