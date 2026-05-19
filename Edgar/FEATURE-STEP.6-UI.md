# FEATURE: UI and Reporting

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Terminal scoreboard (Phase 1), HTML reports (Phase 2), and a KPI dashboard with automated signal reports (Phase 3). |
| Phase       | 3 |

## Phase 1: Terminal Scoreboard (Rich)

`bin/report.sh`

Output format (Rich table):
```
PRIVATE CREDIT STRESS SCOREBOARD  —  2026-Q1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ticker  Score  PIK%   Non-Acc%  Avg Mark  Coverage  NII Cov  Signal
TCPC      14   18.2%    4.8%     88.1%     164%      0.87x   🔴 CRITICAL SHORT
MFIC       9   14.1%    3.2%     92.4%     172%      0.94x   🟠 HIGH STRESS
OBDC       6    9.8%    2.1%     94.7%     181%      1.01x   🟡 ELEVATED
ARCC       4    8.2%    1.8%     95.2%     189%      1.08x   🟡 WATCH
FSCO       2    5.1%    0.9%     96.8%      N/A      1.12x   🟢 LONG (25% disc)
BXSL       3    7.4%    1.4%     95.9%     183%      1.03x   🟡 WATCH
```

Color coding: 10+ = red, 7-9 = orange, 4-6 = yellow, 0-3 = green.

## Phase 2: HTML Report Generation

`bin/report.sh --html --output reports/scoreboard_YYYY-MM-DD.html`

Per-ticker deep dive report (Jinja2 template) showing:
- Score history chart (8 quarters)
- Metric table with trend arrows
- Recent 8-K events flagged
- Top 15 positions (if available)

## Phase 3: KPI Dashboard and Automated Signal Reports

Full UI (Flask or static HTML) with:
- KPI trend charts per ticker per metric
- Recent filing highlights extracted from MD&A
- Automated buy/sell/hold signal report (email or file)
- Alert log with acknowledge capability

## 8-K Event Display

Recent flagged 8-K events appear in the scoreboard and deep dive. Format:
```
[TCPC] 2026-05-12  8-K Item 8.01  DOJ investigation announced  ⚠️ +5 pts
```

## Success Criteria

- Phase 1: `bin/report.sh` prints a Rich table with correct scores for all Tier 1 tickers.
- Phase 1: Color coding correctly reflects signal levels.
- Phase 1: Recent flagged 8-K events appear below the scoreboard.

## Open Questions

- Phase 3 UI: Flask + Bootstrap (consistent with other projects) or static HTML generation?
- Should the report email alerts directly, or only write to a file for manual review?
