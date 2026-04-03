# Engineering Rules

A platform-wide agent behavior contract and technology stack. Every project
gets the same rules and patterns, enforced by AI agents automatically.

## How It Works

`BUSINESS_RULES.md` is the source of truth. An AI summarises it into `CLAUDE_RULES.md`,
which is injected into every project's `AGENTS.md`. The agent follows these rules
when building and maintaining code.

```bash
bash bin/summarize_rules.sh > rules-prompt.md
# Feed to AI → paste output over RulesEngine/CLAUDE_RULES.md
```

## What's in RulesEngine/

| File | Purpose |
|------|---------|
| `BUSINESS_RULES.md` | Full rules with rationale — edit here |
| `CLAUDE_RULES.md` | Generated agent contract — never edit directly |
| `ONESHOT_BUILD_RULES.md` | How concise specifications expand to detailed ones |
| `DOCUMENTATION_BRANDING.md` | Colour palette, typography, theme standards |
| `stack/*.md` | Prescriptive patterns per technology (Flask, SQLite, Bootstrap, etc.) |
| `spec_template/` | Template files scaffolded by `setup.sh` |
| `templates/` | Files propagated to every code project (common.sh, common.py) |

## Conformity Levels

Projects mature through levels. Each level adds requirements:

| Level | Requirements |
|-------|-------------|
| **IDEA** | `METADATA.md` exists |
| **PROTOTYPE** | + `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py` |
| **ACTIVE** | + git initialised, health endpoint configured |
| **PRODUCTION** | + health responding, all compliance checks pass |

Check status: `bash bin/ProjectValidate.sh MyProject`
Update rules: `bash bin/ProjectUpdate.sh MyProject`
