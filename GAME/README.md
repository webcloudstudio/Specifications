# GAME — Generic AI Management Environment

A project framework for managing your projects.

Common built in standards provide enterprise features out of the box for users projects.  Projects can be easily conformed to a simple set of developement best practices which your agent can implement for you.  

Each AI project has a minimal configured set of instructions placed in their rules which will expose project operations, endpoints, capabilities, documentation, command and control in a standard way that can be leveraged to make the easy to run and work with.  They will all work similarly. 

## Intent

Purpose 1: Provide the user interface and central agent for the Project Owner to see their various Projects

        * Manage projects you want to keep around and update (software, book, or project)

Purpose 2: To Conform all projects to standards enabling thier management

    Standard workflow benefits any Tecnical Product Owner
        This framework provides one shot project creation
        This framework ensures project conformity

    Conformed projects expose Start/Stop commands, Routine Operations, Performance, Maintenace, Scheduled Tasks, Event Logging, Documentation, Heartbeats/Health Checks, Unit Testing.
    Exposed information can be seen in a user interface and managed

    This project workflow ensures we can add agents.md guidance such that your project builds correctly

Purpose 3: To Provide Workflow with value

    For value add i would ideally like the end of each claude session to be done with a custom skill that remembers next steps and questions 

The GAME project consists of
    The Flask user Interface with Configrable Snap In Screens
        A set of best practice screens that expose all the nice features we have for our projects so i can easily manage them
        I want to see by project but to easily filter to the project i want probably by last date
        Enables the project owner to manage their projects
    The Workflow engine
        I envision submitting feature tickets to claude for automated processing
        I envision being able to build the project from idea
        I envision being able to iterate the specification to make changes.  That iterateion could be a change to a specification file or a new markdown file.

The interface should use simple elegant design with form follows function 

Less is more... Reduce it to its fundamentals and produce the elegant simple solution.

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
