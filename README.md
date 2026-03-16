# Specifications

Project integration standards and specifications for AI-orchestrated development. Defines how projects participate in the platform, what the platform does, and how GAME implements it.

## Structure

```
Specifications/
  CLAUDE_RULES.md          Integration standard (baseline CLAUDE.md for every project)
  FEATURES.md              Platform capabilities with status and completeness
  TODO.md                  Prioritized backlog
  verify.py                Compliance scanner
  rebuild_index.sh         Generate browsable documentation
  GAME/                    GAME dashboard specification (by screen)
  AlexaPrototypeOne/       Alexa prototype specification
  stack/                   Technology reference files (for generate-prompt.sh)
  archive/                 Superseded documents
```

## How It Works

```
CLAUDE_RULES.md    Rules every project follows (scripts, metadata, secrets, docs)
       |
       |           "Conform project X to CLAUDE_RULES.md" → agent builds it
       |
FEATURES.md        What the platform does (24 features, 10 built)
       |
GAME/              How the dashboard implements those features (7 screens)
```

**CLAUDE_RULES.md** is the baseline. It defines bin/ script standards, METADATA.md format, AGENTS.md context files, secrets convention, documentation generation, and governance rules. Any AI agent reading this file can build, operate, and maintain a conforming project.

**FEATURES.md** lists all 24 platform capabilities with status and completeness scores.

**GAME/** contains one spec per UI screen: Dashboard, Processes, Publisher, Configuration, Usage, Monitoring, Workflow.

## Quick Start

```bash
# Browse documentation
bash rebuild_index.sh && open index.html

# Validate project compliance
python3 verify.py --projects ~/projects

# Generate a build prompt for an AI agent
bash generate-prompt.sh GAME > build-prompt.md

# Conform a new project to standards
# → Give the agent CLAUDE_RULES.md and let it go
```

## Key Conventions

- **METADATA.md** — Line-based `key: value` format (not YAML). Single source of project identity.
- **AGENTS.md** — AI context file. CLAUDE.md is a pointer to it (`@AGENTS.md`).
- **bin/common.sh** — Shared functions. Reads PORT, PROJECT_NAME from METADATA.md.
- **$PROJECTS_DIR/.secrets** — Global API keys. Per-project overrides in `.env`.
- **doc/** — Generated documentation. Built by `bin/build_documentation.sh`.
- **Version format** — `YYYY-MM-DD.N` (e.g., `2026-03-13.2`).
- **Date format** — Always `yyyymmdd` or `yyyymmdd_hhmmss` for sorting.

## WORKFLOW FOR UPDATING

# Validate project compliance
 python3 verify.py --project GAME --projects ../