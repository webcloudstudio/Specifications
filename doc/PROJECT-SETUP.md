# Project Setup Guide

Technical reference for the files in a specification directory. For the overall process, see `SPECIFICATION-PROCESS.md`.

---

## Required Files

| File | Purpose |
|------|---------|
| `METADATA.md` | Project identity: name, display_name, short_description, status, and optional fields |
| `README.md` | Project name and one-line description |
| `INTENT.md` | Why this project exists, who it's for, what problem it solves |
| `ARCHITECTURE.md` | Modules, routes, directory layout |

**METADATA.md required fields:** `name`, `display_name`, `short_description`, `status`.
All other METADATA fields are documented in `GLOBAL_RULES/CLAUDE_RULES.md` — not repeated here.

## Conditional Files

| File | Include when | Delete when |
|------|-------------|-------------|
| `DATABASE.md` | Project has a database | No database |
| `UI.md` | Project has a user interface | No UI (CLI, library, API-only) |
| `SCREEN-{Name}.md` | One per screen in the UI | No UI |
| `FEATURE-{Name}.md` | Cross-cutting behavior not tied to one screen | Not needed |

---

## INTENT.md

Why the project exists. Written by the author, not generated.

```markdown
# Intent

Who this is for and what problem it solves.

## Core Principle

The main design idea or philosophy.

## What This Is Not

Explicit scope boundaries.
```

No Open Questions section. This file is the author's declaration, not a spec to expand.

---

## ARCHITECTURE.md

Code organization. Keep it concise — conversion expands it.

```markdown
# Architecture

One-line pattern summary.

## Modules

| Module | Responsibility |
|--------|---------------|
| module.py | What it does |

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | / | Full page |

## Directory Layout

{tree}

## Open Questions

- Unresolved architectural decisions
```

---

## DATABASE.md

Tables and columns only. Stack conventions (WAL, migrations, etc.) are applied during conversion from `stack/*.md` files — do not repeat them here.

```markdown
# Database

SQLite at `data/app.db`. Stack conventions per `stack/sqlite.md`.

## table_name

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | unique |
| extra | JSON | |
| created_at | TEXT | timestamp |

## Open Questions

- Schema decisions not yet resolved
```

**Type shorthand:** `INTEGER PK`, `TEXT`, `FK` (→ references), `JSON` (stored as TEXT), `INTEGER` (booleans use 0/1).

---

## SCREEN-*.md

One per screen. File name matches the nav bar label.

```markdown
# Screen: ScreenName

One-line description.

## Route

GET /path

## Layout

Major sections/areas.

## Columns

| Column | Content |
|--------|---------|

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|

## Open Questions

-
```

Reference `UI.md` for shared components — don't redefine shared patterns in screen files.

---

## FEATURE-*.md

One per cross-cutting behavior that spans multiple screens or has no screen.

```markdown
# Feature: FeatureName

One-line description.

## Trigger

What starts this.

## Sequence

1. Step one
2. Step two

## Reads

Data sources consumed.

## Writes

Data stores modified.

## Open Questions

-
```

Mark roadmap features: `# Feature: Name [ROADMAP]`. Conversion preserves intent without expanding implementation detail.

---

## UI.md

Shared visual patterns. Screen files reference this instead of repeating.

```markdown
# UI Standards

## Theme

Framework, color scheme, CSS approach.

## Navigation

What's in the nav bar.

## Shared Components

Reusable pieces: row headers, buttons, filters, modals.

## Open Questions

-
```

---

## Open Questions Convention

All spec files except README.md, METADATA.md, and INTENT.md end with:

```markdown
## Open Questions

- Unresolved design decision
- Another question
```

These signal to the builder: "ask the human before deciding." Preserved through conversion and build. Agents add questions here rather than creating new files.

---

## Scaffolding

```bash
bash bin/create_spec.sh <project-name> ["Short description"]
```

Creates the directory with all template files. Edit, rename, and delete as needed. Then validate:

```bash
bash bin/validate.sh <project-name>
```
