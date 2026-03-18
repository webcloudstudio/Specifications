# GAME — Generic AI Management Environment

A project framework for managing your projects.

Common built in standards provide enterprise features out of the box for users projects.  Projects can be easily conformed to a simple set of developement best practices which your agent can implement for you.  

Each AI project has a minimal configured set of instructions placed in their rules which will expose project operations, endpoints, capabilities, documentation, command and control in a standard way that can be leveraged to make the easy to run and work with.  They will all work similarly. 

## Intent

A solo practitioner or small team managing multiple AI-built projects needs one methedology.  If your projects have custom capabilities then it is difficult to manage.  A users projects become easier to manage when they are standard in format.  Start/Stop Services, Logs, Documentation, Health Checks, Unit Testing and other features are all set the same way. 

Projects go through workflow.  They have several stages where we conform the project to standards and verify the metadata as we work through our workflow.  

## Stack

- **Language:** Python
- **Framework:** Flask (app factory, blueprints, HTMX for partial updates)
- **Database:** SQLite (WAL mode, single file at `data/game.db`)
- **Frontend:** Bootstrap 5 (dark theme, CDN)
- **Port:** 5001

Each stack component maps to a prescriptive reference file in `../GLOBAL_RULES/stack/` (python.md, flask.md, sqlite.md, bootstrap5.md). These files define exactly how to implement with concrete code examples.

## Specifications

All project integration standards (script headers, METADATA.md format, secrets, documentation) are defined in `../GLOBAL_RULES/CLAUDE_RULES.md` — that file is injected into each project's AGENTS.md.

The specs in this directory describe GAME specifically:

| Document | Answers |
|----------|---------|
| **FEATURE_MAP.md** | What attributes exist? What features does the platform offer? What can it detect? Primary reference. |
| **ARCHITECTURE.md** | How is the code organized? What are the modules? How does data flow? |
| **DATABASE.md** | What tables exist? What columns? What constraints? |
| **UI-GENERAL.md** | Shared UI patterns: nav bar, standard headers, dark theme, modals, HTMX conventions. |
| **SCREEN-*.md** | What does each screen show? What can the user do on it? |

**Flow:** FEATURE_MAP defines features --> ARCHITECTURE describes modules --> DATABASE defines storage --> UI-GENERAL defines shared patterns --> SCREEN-* defines per-screen layout.

## Building From This Specification

```bash
# 1. Validate that all stack files exist
bash ../validate.sh GAME

# 2. Generate a complete build prompt for an AI agent
bash ../generate-prompt.sh GAME > build-prompt.md

# 3. Feed build-prompt.md to the agent along with CLAUDE_RULES.md
```

The generated prompt includes all stack reference files (common.md, python.md, flask.md, sqlite.md, bootstrap5.md) followed by all specification files in this directory. An AI agent reading this prompt has everything needed to build GAME from scratch.
