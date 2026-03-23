# Project Setup Instructions

**Version:** 20260320 V1  
**Description:** Guide to specification directory structure, files, and naming conventions

A spec directory is a self-contained project description — concise enough to fit in a single build prompt, structured enough for an AI agent to implement from. Run `bin/setup.sh <ProjectName>` to scaffold the directory. Edit the four required files first, then add conditional files as the design takes shape. Delete anything that doesn't apply.

## Required Files

| File | Purpose |
|------|---------|
| `METADATA.md` | Identity: name, display_name, short_description, status (IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED) |
| `README.md` | One-line project description |
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

- All spec files except README and METADATA end with `## Open Questions`
- File names use uppercase with hyphens: `SCREEN-Dashboard.md`, `FEATURE-Scan.md`
- Write concise specs (tables, bullets). CONVERT.md rules expand them during conversion.
- Stack-specific patterns come from `RulesEngine/stack/` files — don't repeat them in specs.

## Global Rules

```
RulesEngine/
  CONVERT.md           How concise specs expand into detailed specs
  CLAUDE_RULES.md      Agent behavior contract (injected into projects)
  stack/               Technology patterns (flask.md, sqlite.md, ...)
  spec_template/       Template files used by setup.sh
```
