# Project Setup Guide

How to create the required files for a new project specification. This is the technical reference for setting up each file.

---

## Required Files

Every project specification directory needs at minimum:

| File | Required | Purpose |
|------|----------|---------|
| `METADATA.md` | Yes | Project identity — name, stack, port, status |
| `README.md` | Yes | Intent, stack summary, build instructions |
| `ARCHITECTURE.md` | Yes | Modules, directory layout, routes |
| `DATABASE.md` | If has DB | Tables, columns, types |
| `UI.md` | If has UI | Shared visual patterns |
| `SCREEN-*.md` | If has UI | One per screen |
| `FEATURE-*.md` | As needed | One per cross-cutting behavior |

---

## METADATA.md

Key-value format (not YAML). Parsed with grep/cut.

```markdown
# ProjectName

One-line description.

name: my-project
display_name: My Project
git_repo: my-project
short_description: One sentence describing the project.
port: 8080
status: PROTOTYPE
version: 2026-03-19.1
updated: 20260319
stack: Python/Flask/SQLite/Bootstrap5
health: /health
tags: tool, dashboard
desired_state: on-demand
namespace: development
```

**Required fields:** `name`, `display_name`, `short_description`, `stack`, `status`.

**Optional fields:** `port` (services only), `health` (services only), `git_repo`, `version`, `tags`, `desired_state`, `namespace`, `show_on_homepage`, `card_*` overrides.

The `stack:` field is slash-separated and maps to `GLOBAL_RULES/stack/*.md` files. Available: python, flask, django, sqlite, postgres, bootstrap5, alexa-skills-kit, aws-lambda, aws-api-gateway, aws-sqs.

---

## README.md

Short. Three sections:

```markdown
# Project Name — Subtitle

What this project does in 1-2 sentences.

## Intent

Why this project exists. Who it's for. What problem it solves.

## Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** SQLite
- **Frontend:** Bootstrap 5, HTMX
- **Port:** 8080

## Building From This Specification

\```bash
bash bin/build.sh ProjectName > build-prompt.md
\```
```

---

## DATABASE.md

Tables and columns only. Stack conventions are applied during conversion — don't repeat them.

```markdown
# Database

SQLite at `data/app.db`. Stack conventions per `stack/sqlite.md`.

## table_name

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | unique, machine slug |
| status | TEXT | active / archived |
| extra | JSON | |
| created_at | TEXT | timestamp |
| updated_at | TEXT | timestamp |

## Open Questions

- Should X be its own table or a JSON field in extra?
```

**Types:** `INTEGER`, `TEXT`, `INTEGER PK`, `FK` (references another table), `JSON` (stored as TEXT).

**Notes column:** constraints (unique, nullable), allowed values, defaults, or brief description.

---

## SCREEN-*.md

One file per screen. Name matches the nav bar label.

```markdown
# Screen: ScreenName

One-line description.

## Route

\```
GET /path
\```

## Layout

Description of major sections/areas.

## Columns

| Column | Content |
|--------|---------|
| Name | What's in this column |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Do thing | Click button | POST /path → result |

## Open Questions

- Unresolved design decisions
```

**Reference UI.md** for shared components (e.g., "Uses Standard Row Header — see UI.md"). Don't redefine shared patterns.

---

## FEATURE-*.md

One file per cross-cutting behavior that isn't tied to a single screen.

```markdown
# Feature: FeatureName

One-line description.

## Trigger

What starts this feature (user action, timer, startup).

## Sequence

1. Step one
2. Step two
3. Step three

## Reads

What data sources are consumed.

## Writes

What data stores are modified.

## Key Behaviors

- Important behavior that isn't obvious from the sequence

## Open Questions

- Unresolved decisions
```

Mark roadmap features: `# Feature: FeatureName [ROADMAP]`

---

## UI.md

Shared visual patterns referenced by SCREEN-* files.

```markdown
# UI Standards

Shared patterns. Screen specs reference this for shared components.

## Theme

Framework, theme, CSS approach.

## Navigation Bar

What's in the nav, left to right.

## Shared Components

Table of reusable components (row headers, buttons, filters, modals).

## Conventions

HTMX patterns, typography, responsive behavior.
```

---

## ARCHITECTURE.md

Code organization. Modules, routes, directory layout.

```markdown
# Architecture

One-line summary of the pattern (e.g., "Flask app factory with blueprints").

## App Factory / Entry Point

How the app starts.

## Modules

| Module | Responsibility |
|--------|---------------|
| module.py | What it does |

## Routes

| Method | Path | Returns |
|--------|------|---------|
| GET | / | Full page |
| POST | /api/action | HTML fragment |

## Directory Layout

\```
Project/
  app.py
  routes.py
  ...
\```

## Open Questions

- Architectural decisions not yet made
```

---

## Validation

After creating files, validate:

```bash
# Check that all stack files referenced in METADATA.md exist
bash bin/validate_project.sh ProjectName

# Generate the build prompt to verify everything assembles correctly
bash bin/build.sh ProjectName --no-tag > /dev/null && echo "OK"
```
