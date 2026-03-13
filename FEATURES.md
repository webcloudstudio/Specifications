# FEATURES — Common Services & GAME Dashboard

---

## Section 1: Common Services Layer

What ANY project gets by following the rules in `CLAUDE_RULES.md`:

| Service | How It Works | Status |
|---------|-------------|--------|
| **Unified Logging** | Scripts log to `logs/{Op}_{timestamp}.log`; `[GAME]` protocol lines parsed for live status | Built |
| **Process Management** | `bin/start.sh` / `bin/stop.sh` discovered automatically; launch, stop, and monitor from dashboard | Built |
| **Service Discovery** | Filesystem scan reads bin/ headers, CLAUDE.md, git_homepage.md, Links.md, STACK.yaml — no registration needed | Built |
| **Portfolio Publishing** | `git_homepage.md` with `Show on Homepage: true` generates a card on the GitHub Pages portfolio site | Built |
| **Observability** | Declaring `# Port:` in a bin/ header enables health polling; status shown as UP/DOWN/UNKNOWN | Roadmap |
| **Configuration Management** | AI assistant config profiles stored as YAML; versioned deployment with git-based rollback | Built |
| **Usage Analytics** | Reads AI session JSONL logs; shows token counts and estimated costs per project | Built |
| **Ticketing** | Feature tickets with IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE lifecycle | Roadmap |

### Gap Analysis

| Service | What Exists | What's Missing |
|---------|------------|----------------|
| Logging | Log file convention + `[GAME]` protocol defined | Log rotation / cleanup is manual (`bin/clean-logs.sh`) |
| Process Management | Start/stop/status works end-to-end | No auto-restart on failure |
| Service Discovery | Full contract chain working | No file-watch trigger — requires manual rescan or startup scan |
| Portfolio Publishing | Card generation + GitHub Pages push working | No incremental builds; full rebuild each time |
| Observability | Port declaration in headers defined | Health polling daemon not yet implemented |
| Configuration Management | Profile deploy + rollback working | No diff preview UI yet |
| Usage Analytics | Session log reading + cost estimation | Per-ticket cost attribution not connected |
| Ticketing | State machine and data model defined | Feature not yet implemented |

---

## Section 2: GAME Dashboard Features

What the GAME platform UI provides:

| Feature | Description | Status |
|---------|------------|--------|
| **Control Panel** | Project list with status badges, inline workflow state editing, operation buttons, quick links | Built |
| **Project Discovery** | Filesystem scanner auto-detects projects and parses all contract files | Built |
| **Operations Engine** | Executes bin/ scripts on demand, captures stdout/stderr, tracks run state (IDLE → RUNNING → DONE/ERROR) | Built |
| **Process Monitor** | Live log viewer with auto-scroll, process list, stop button, past run history | Built |
| **GitHub Publisher** | Generates static portfolio from git_homepage.md cards, preview server, one-click publish | Built |
| **Project Documentation** | Detects `docs/index.html` and includes it in portfolio build at `/project-docs/{name}/` | Built |
| **Tag Management** | Colored tags with inline assignment, filtering, tag CRUD in settings | Built |
| **Git Integration** | Per-project branch, dirty state, unpushed commits, governance checklist (read-only) | Built |
| **Configuration Management** | Profile library, deploy preview, deployment history with rollback | Built |
| **Usage Analytics** | Daily/weekly/monthly token + cost dashboard, by-project breakdown, session log | Built |
| **Monitoring & Heartbeats** | Health polling for services with declared ports, UP/DOWN alerts, uptime history | Roadmap |
| **Workflow States** | Feature ticket lifecycle, Kanban view, AI transaction logs, acceptance criteria tracking | Roadmap |

### Feature Dependencies

```
Contracts (bin/ headers, CLAUDE.md, git_homepage.md, Links.md, STACK.yaml)
  └→ Project Discovery
       ├→ Control Panel ──→ Operations Engine ──→ Process Monitor
       │                                              └→ Monitoring & Heartbeats [ROADMAP]
       ├→ GitHub Publisher
       ├→ Git Integration
       └→ Tag Management

Usage Analytics (reads AI session logs independently)
  └→ Workflow States [ROADMAP] (uses cost data for scheduling)

Configuration Management (reads profiles independently)
```
