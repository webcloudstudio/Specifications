# Project Setup

Every spec directory needs these four files. `bin/create_spec.sh` generates them from templates.

## Required Files

| File | Purpose |
|------|---------|
| `METADATA.md` | Identity: name, display_name, short_description, status (IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED) |
| `README.md` | One-line project description |
| `INTENT.md` | Why this project exists, who it's for, scope boundaries |
| `ARCHITECTURE.md` | Modules, routes, directory layout |

## Conditional Files

Add what applies. Delete the rest.

| File | When |
|------|------|
| `DATABASE.md` | Project has a database — tables and columns only |
| `UI.md` | Project has a UI — shared patterns across screens |
| `SCREEN-{Name}.md` | One per screen: route, layout, columns, interactions |
| `FEATURE-{Name}.md` | Cross-cutting behavior: trigger, sequence, reads, writes |

## Conventions

- All spec files except README, METADATA, and INTENT end with `## Open Questions`
- File names use uppercase with hyphens: `SCREEN-Dashboard.md`, `FEATURE-Scan.md`
- Write concise specs (tables, bullets). CONVERT.md rules expand them during conversion.
- Stack-specific patterns come from `GLOBAL_RULES/stack/` files — don't repeat them in specs.

## Global Rules

```
GLOBAL_RULES/
  CONVERT.md           How concise specs expand into detailed specs
  CLAUDE_RULES.md      Agent behavior contract (injected into projects)
  stack/               Technology patterns (flask.md, sqlite.md, ...)
  spec_template/       Template files used by create_spec.sh
```
