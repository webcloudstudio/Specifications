# Screen: Usage Analytics

**AI token and cost tracking.** Reads session logs, shows usage by project and over time.

---

## Layout

Summary bar at top, by-project table, session log below.

## Summary Bar

Today's tokens, today's cost, this month's tokens, this month's cost.

## By-Project Table

| Column | Description |
|--------|-------------|
| Project name | From session log context |
| Sessions today | Count |
| Tokens today | Sum |
| Tokens this month | Sum |
| Estimated cost | From rates table |

Sortable by any column.

## Session Log

Paginated, most recent first. Per row: timestamp (yyyymmdd_hhmmss), project, model, token count, cost.

## Nav Bar Indicator

Today's cost shown on all screens. Links to this page.

## How It Works

Reads AI session JSONL log files (not produced by this platform). Extracts: timestamp, project context, token counts, model name. Cost estimated from a user-editable rates table (model → cost per million tokens). Estimates labeled as estimates.

## Data Flow

| Reads | Writes |
|-------|--------|
| AI session JSONL logs (external) | Usage summary → nav bar |
| Rates config file | |
