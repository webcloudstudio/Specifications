# Screen: Settings

**Route:** `/settings`
**Purpose:** Configure the system without editing files directly — universe management, thresholds, and data operations

## Layout

Four sections rendered as stacked cards:

### 1. Universe Management

Table with one row per ticker in asset_config:

| Column | Control |
|--------|---------|
| Ticker | Read-only |
| Display Name | Editable text field |
| Bucket | Editable text field |
| Asset Class | Dropdown |
| Phase | Read-only (1 or 2) |
| Active | Toggle switch |
| Actions | Remove button |

- "Add Ticker" button opens inline form: ticker, display name, bucket, asset class, source
- Changes persist to universe.yaml and asset_config table on Save

### 2. Alert Thresholds

| Alert Type | Control | Default |
|------------|---------|---------|
| Sell score trigger | Numeric input (0.0–1.0) | 0.65 |
| Buy score trigger | Numeric input (0.0–1.0) | 0.65 |
| Relative volume spike | Numeric input | 2.0 |
| Flow rank shift (percentile points / 5d) | Numeric input | 20 |

"Save Thresholds" button — persists to config table in SQLite.

### 3. Data Operations

- "Run Backfill (Full)" button — triggers `scripts/backfill.py --full` as background task
- "Run Incremental Update" button — triggers `scripts/backfill.py --incremental`
- "Compute Signals" button — triggers `scripts/compute_signals.py --backfill`
- Status indicator: shows running / last run timestamp / result (ok / error)

### 4. Data Health

Table: one row per ticker showing last_success, last_failure, row_count, status from download_log. Rows with status = 'error' or 'warning' highlighted in red/yellow.

## Open Questions

-
