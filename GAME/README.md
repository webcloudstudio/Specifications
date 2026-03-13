# GAME — Generic AI Management Environment

A web dashboard for managing AI-assisted development projects. Discovers local projects by reading their METADATA.md and bin/ script headers, then provides a unified interface for running operations, viewing logs, publishing portfolios, managing AI configurations, and tracking usage costs.

## Intent

A solo practitioner or small team managing multiple AI-built projects needs one place to see what's running, launch operations, and track costs. GAME is that place. It does not modify project code — it reads filesystem contracts (METADATA.md, AGENTS.md, bin/ headers) and surfaces them as a dashboard with buttons.

## Stack

- **Language:** Python
- **Framework:** Flask (app factory, blueprints, HTMX for partial updates)
- **Database:** SQLite (WAL mode, single file at `data/game.db`)
- **Frontend:** Bootstrap 5 (dark theme, CDN)
- **Port:** 5001

Each stack component maps to a prescriptive reference file in `../stack/` (python.md, flask.md, sqlite.md, bootstrap5.md). These files define exactly how to implement with concrete code examples.

## Specifications

All project integration standards (script headers, METADATA.md format, secrets, documentation) are defined in `../CLAUDE_RULES.md` — that file should be appended to your CLAUDE.md before building this project.

The specs in this directory describe GAME specifically:

- **ARCHITECTURE.md** — App factory, blueprints, backend modules (scanner, engine, publisher, config, usage), routes, directory layout
- **DATABASE.md** — SQLite schema for projects, operations, runs, tags, config, usage
- **SCREEN-*.md** — What each UI screen shows and how users interact with it

## Building From This Specification

```bash
# 1. Validate that all stack files exist
bash ../validate.sh GAME

# 2. Generate a complete build prompt for an AI agent
bash ../generate-prompt.sh GAME > build-prompt.md

# 3. Feed build-prompt.md to the agent along with CLAUDE_RULES.md
```

The generated prompt includes all stack reference files (common.md, python.md, flask.md, sqlite.md, bootstrap5.md) followed by all specification files in this directory. An AI agent reading this prompt has everything needed to build GAME from scratch.
