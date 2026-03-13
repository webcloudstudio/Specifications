# FEATURES — Platform Capabilities for AI-Orchestrated Projects

These are the 15 features the orchestration platform must implement to support AI-assisted development by non-specialist users. Features are listed in implementation priority order. Each feature includes its current status and the gap between what exists and what is needed.

---

## Feature 1: Control Panel

**What it is:** The unified dashboard. Shows every project in one view with its status, workflow state, operations, and links. All day-to-day actions happen here.

**Key capabilities:** Project list with status badges, inline workflow state editing, operation buttons, quick links, running process count in nav bar, filter by tag/state/type.

**Status:** Built

---

## Feature 2: Project Discovery & Compliance Reporting

**What it is:** Scans the filesystem for projects, reads their `METADATA.md` and `bin/` headers, and registers their capabilities. Reports which rules each project satisfies and which are missing based on the project's declared status.

**Key capabilities:** Auto-registration via METADATA.md, bin/ header parsing, compliance score per project, maturity-aware rule enforcement (IDEA projects are not penalized for missing bin/ scripts; PRODUCTION projects must pass all rules).

**Status:** Discovery built; compliance reporting is a gap — see Feature 13.

---

## Feature 3: Operations Engine

**What it is:** Runs a project's registered bin/ scripts on demand. Captures stdout/stderr, tracks run state, and reports status via the `[GAME]` line protocol.

**Key capabilities:** One-click script execution from the dashboard, IDLE → STARTING → RUNNING → DONE/ERROR/STOPPED state machine, run history per project, stop button.

**Status:** Built

---

## Feature 4: Process Monitor

**What it is:** Live log viewer and process control panel. Shows everything the platform has run, is running, or has completed.

**Key capabilities:** Live log output with auto-scroll, process list sorted by recency, stop button for running processes, log viewer for completed runs.

**Status:** Built

---

## Feature 5: Workflow States (Ticket Lifecycle)

**What it is:** A structured lifecycle for feature work. Each ticket moves from idea to done with the platform guiding what happens at each step and preserving an audit trail of AI decisions.

**Key capabilities:** States: IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE. Kanban view across all projects. AI Transaction Log (acceptance criteria, features built, intent). Rework paths back to READY or PROPOSED.

**Status:** Roadmap — data model defined, UI not built

---

## Feature 6: Documentation Generation

**What it is:** Generates human-readable documentation from project specs, code, and CLAUDE.md. The output is a self-contained `docs/index.html` that is committed to git and published with the portfolio.

**Key capabilities:** `bin/build_documentation.sh` CommandCenter operation per project. Generated HTML embeds all spec markdown files. Published automatically when portfolio is rebuilt. Documentation link appears on portfolio card.

**Status:** Partially built — the viewer template exists; per-project `build_documentation.sh` generation is a gap for non-GAME projects.

---

## Feature 7: Portfolio Publishing

**What it is:** Generates and publishes a static GitHub Pages portfolio from every project's `METADATA.md`. One-click rebuild and publish.

**Key capabilities:** Card grid from `METADATA.md` fields, site-wide branding config, local preview server, one-click push to GitHub Pages, documentation links per project when `docs/index.html` exists.

**Status:** Built — previously read from `git_homepage.md`; needs update to read from `METADATA.md`

---

## Feature 8: Git Integration

**What it is:** Surfaces each project's git state in the dashboard. Read-only — the platform never modifies git state.

**Key capabilities:** Branch, uncommitted changes, unpushed commits, last commit message, governance checklist (initialized / remote configured / not persistently dirty).

**Status:** Built

---

## Feature 9: Configuration Management

**What it is:** Manages the AI assistant's working configuration. Users select a config profile; the platform deploys it to the AI's config directory. Past deployments are versioned in git.

**Key capabilities:** Profile library (YAML files), deploy with diff preview, deployment history, one-click rollback to any prior deployment.

**Status:** Built

---

## Feature 10: Usage Analytics

**What it is:** Reads AI session log files and shows how many tokens were consumed and what it cost, by project and over time.

**Key capabilities:** Daily/weekly/monthly summaries, by-project breakdown, session log, nav bar cost indicator, user-editable rates table.

**Status:** Built

---

## Feature 11: Monitoring & Alerting

**What it is:** Polls running services for health and notifies the user when something goes down. Closes the loop between "I started the server" and "the server is actually responding."

**Key capabilities:** Health polling via declared `Port:` in bin/ headers and `health:` in METADATA.md, UP/DOWN/UNKNOWN/SNOOZED states, in-UI alerts on state transitions, uptime history, incident log. Future: webhook/email/OS notifications.

**Status:** Roadmap

---

## Feature 12: Environment Management

**What it is:** Tracks `.env` files across projects, identifies missing variables, and alerts when a project's actual environment diverges from `.env.example`.

**Key capabilities:** Per-project .env.example detection, diff between .env.example and actual .env (variables present/missing, not values), secrets scanner (warns if .env is committed to git), environment comparison across deployments.

**Status:** Not built — `.env.example` convention defined in CLAUDE_RULES.md; tooling is a gap

---

## Feature 13: Compliance Verification

**What it is:** A standalone script (and dashboard view) that scans all projects and reports which CLAUDE_RULES standards each project satisfies, calibrated to the project's declared status.

**Key capabilities:** Per-project pass/fail for every applicable rule, maturity-aware enforcement (IDEA projects only checked for basic metadata; PRODUCTION projects checked for all rules), aggregate summary table, JSON output for CI integration.

**Implementation:** `bin/verify.py` at the Specifications root. Run with `python3 verify.py --projects /path/to/projects`.

**Status:** Built — see `verify.py` in this repository

---

## Feature 14: Tag Management

**What it is:** Lightweight visual grouping for projects. Tags are defined in `METADATA.md` and can be assigned colors in the platform. The project list is filterable by tag.

**Key capabilities:** Tags read from `METADATA.md` `tags:` field, user-assigned colors stored in platform config, inline tag assignment from dashboard, filter by one or more tags, tag CRUD in settings.

**Status:** Built

---

## Feature 15: Project Scaffolding

**What it is:** Generates a new project directory pre-wired to all CLAUDE_RULES standards. A user picks a template (web service, CLI tool, data pipeline, etc.) and gets a project with correct METADATA.md, CLAUDE.md, bin/ scripts with proper headers and preamble, .env.example, and a passing compliance score from day one.

**Key capabilities:** Template library, parameter prompts (project name, port, stack), generated METADATA.md with all required fields, generated bin/start.sh / bin/stop.sh / bin/test.sh with CommandCenter headers and preamble, generated CLAUDE.md skeleton, generated .env.example.

**Status:** Not built — highest leverage gap for onboarding new AI-developed projects

---

## Implementation Priority

| Priority | Feature | Why |
|----------|---------|-----|
| 1 | Project Discovery & Compliance | Everything else depends on knowing what projects exist and how compliant they are |
| 2 | Compliance Verification (verify.py) | Needed immediately; can run standalone before the full platform is built |
| 3 | Project Scaffolding | Prevents new projects from starting non-compliant |
| 4 | Workflow States | Needed to track AI work; currently all ticket tracking is manual |
| 5 | Environment Management | .env problems are common failure mode for AI-built projects |
| 6 | Monitoring & Alerting | Currently no automatic detection when a service goes down |
| 7 | Documentation Generation | AI sessions leave no readable trail without this |
| 8 | Portfolio Publishing → METADATA.md | Existing publisher needs to read from METADATA.md instead of git_homepage.md |

---

## What Changed from Previous Version

- `git_homepage.md` portfolio fields are now part of `METADATA.md` — no separate file
- `Links.md` link table is now part of `METADATA.md` — no separate file
- `STACK.yaml` is superseded by the `stack:` field in `METADATA.md`
- Tag Management promoted to first-class feature (was listed as a dependency)
- Added: Documentation Generation, Environment Management, Compliance Verification, Project Scaffolding
