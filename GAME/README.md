# GAME — Generic AI Management Environment

A dashboard for project owners managing AI-assisted prototypes.

Common built-in standards provide enterprise features out of the box. Projects conform to a simple set of development best practices which your agent implements for you. Each project has a minimal configured set of instructions in its rules which expose operations, endpoints, capabilities, documentation, and command-and-control in a standard way.

## Intent

**Purpose 1: Dashboard for the Project Owner**

Manage projects you want to keep around and update — software, books, or any project type. See everything in one place: status, health, operations, logs, documentation.

**Purpose 2: Conform projects to standards**

Standard workflow benefits any Technical Product Owner:
- One-shot project creation from templates
- Project conformity via CLAUDE_RULES injection
- Conformed projects expose: Start/Stop, Operations, Health, Logging, Documentation, Testing
- Exposed capabilities appear automatically in the dashboard

**Purpose 3: Prototype workflow**

- Feature tickets tracked from idea to done
- AI transaction logs capture decisions and rationale
- Specification management links specs to running code

## The Prototyper Application

- Flask UI with configurable snap-in screens
- Best-practice screens for managing all project features
- Filter and sort by project, status, tags, namespace
- Simple elegant design — form follows function, less is more

## Stack

- **Language:** Python
- **Framework:** Flask (app factory, blueprints, HTMX for partial updates)
- **Database:** SQLite (WAL mode, single file at `data/prototyper.db`)
- **Frontend:** Bootstrap 5 (dark theme, CDN)
- **Port:** 5001

Each stack component maps to a prescriptive reference file in `../RulesEngine/stack/`.

## Specifications

All project integration standards are defined in `../RulesEngine/CLAUDE_RULES.md`.

| Document | Answers |
|----------|---------|
| **FEATURE_MAP.md** | What attributes exist? What features? What can the platform detect? |
| **FUNCTIONALITY.md** | End-to-end flows: trigger → sequence → result |
| **ARCHITECTURE.md** | How is code organized? Modules, routes, data flow |
| **DATABASE.md** | Tables, columns, constraints |
| **UI-GENERAL.md** | Shared UI patterns: nav bar, headers, dark theme, HTMX |
| **SCREEN-*.md** | Per-screen: route, layout, interactions |

**Flow:** FEATURE_MAP defines features → ARCHITECTURE describes modules → DATABASE defines storage → UI-GENERAL defines shared patterns → SCREEN-* defines per-screen layout.

## Building From This Specification

```bash
bash ../bin/validate.sh GAME
bash ../bin/build.sh GAME > build-prompt.md
```

The generated prompt includes all stack reference files followed by all specification files. An AI agent reading this prompt has everything needed to build GAME from scratch.
