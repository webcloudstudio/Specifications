# Screen: Alerts

**Route:** `/alerts`
**Purpose:** Chronological log of triggered signals

## Layout

- Filter bar: by alert type (sell, buy, phase change), by asset class, by date range
- Alert cards: bucket name, signal type, score, date, brief description

## Alert Triggers

| Trigger | Condition |
|---------|-----------|
| Sell threshold | Composite sell score > configurable threshold |
| Buy threshold | Composite buy score > configurable threshold |
| Phase change | W001 transitions to any new phase |
| Volume spike | V004 (rel_volume_20d) > 2.0 |
| Flow shift | R007 changes by >20 percentile points in 5 days |

## Open Questions

- OQ2: Browser-only alerts sufficient for Phase 1? (Yes — email/SMS deferred to Phase 2)
