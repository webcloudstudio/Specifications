# Feature: Usage Analytics

**spec_v4 · 2026-03-11**

---

## Purpose

Shows the user how much AI work has been done, what it cost, and which projects
consumed the most. Enables cost-aware scheduling of AI development (a key input to
the WORKFLOW-STATES READY state).

---

## What the User Can Do

- View token usage and estimated cost for today, this week, this month
- See usage broken down by project
- View individual session records
- See a usage summary in the nav bar on every page

---

## Screens

### Usage Dashboard

Summary bar: today's tokens, today's cost, this month's tokens, this month's cost.

By-project table: project name, sessions today, tokens today, tokens this month,
estimated cost. Sortable.

Session log: timestamp, project, model, token count, cost. Paginated, most recent first.

### Nav Bar Indicator (all pages)

Today's token count and/or cost. Links to Usage Dashboard.

---

## How It Works

The platform reads AI session log files written by the AI assistant. It does not
produce these files — it reads them.

Log files are JSONL format, one record per line. The platform extracts: timestamp,
project context, token counts, model name.

Cost is estimated using a rates table (user-editable, not hardcoded). Estimates are
labeled as estimates in the UI.

---

## Persistence

Session log files are not written by this platform — they are read from the AI
assistant's own log directory.

The rates table (model name → cost per million tokens) is stored as a user-editable
configuration file in the platform's data directory.

---

## Out of Scope

- Billing integration or real-time cost queries from the AI provider → not planned
- Per-ticket cost attribution → possible future integration with WORKFLOW-STATES
