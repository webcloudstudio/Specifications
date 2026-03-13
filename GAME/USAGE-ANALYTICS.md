# Usage Analytics

**AI token and cost tracking.** Reads session logs, shows usage by project and over time.

---

## Capabilities

- Daily/weekly/monthly token summaries
- By-project breakdown
- Session log (timestamp, project, model, tokens, cost)
- Nav bar cost indicator
- User-editable rates table (model → cost per million tokens)

## How It Works

Reads AI session JSONL log files (not produced by this platform). Extracts timestamp, project context, token counts, model name. Cost estimated from rates table.

## Screens

**Usage Dashboard:** Summary bar (today/month tokens and cost). By-project table. Session log (paginated).

**Nav Bar:** Today's cost indicator.

## Persistence

- Session logs: read from AI assistant's log directory (external)
- Rates table: user-editable config file in platform data directory
