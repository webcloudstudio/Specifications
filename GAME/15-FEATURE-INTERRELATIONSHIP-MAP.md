# Feature: Interrelationship Map

**spec_v3 · 2026-03-10**

---

## Purpose

This document summarizes the dependencies between all spec_v3 features — which features
produce data that other features consume, and which features trigger or are triggered by
other features. Use this as the entry point when adding a new feature or debugging an
unexpected interaction.

---

## Dependency Graph

```
PROJECT-METADATA-STANDARDS ──────────────────────┐
SERVICE-SCRIPT-STANDARDS   ──────────────────────┤
                                                   ↓
                                         PROJECT-DISCOVERY
                                                   │
                          ┌────────────────────────┤
                          │                        │
                          ↓                        ↓
                   CONTROL-PANEL           GITHUB-PUBLISHER
                          │                        ↑
                          │                        │
               ┌──────────┼──────────────┐   git_site_config.md
               │          │              │   git_homepage.md
               ↓          ↓              ↓
     OPERATIONS-ENGINE  WORKFLOW-   TAG-MANAGEMENT
               │         STATES
               ↓
       PROCESS-MONITOR
               │
               ↓
      MONITORING-HEARTBEATS
```

---

## Feature-by-Feature Dependency Table

| Feature | Reads From | Writes To / Triggers |
|---------|------------|----------------------|
| **SERVICE-SCRIPT-STANDARDS** | bin/*.sh files | Operation registry (→ PROJECT-DISCOVERY) |
| **PROJECT-METADATA-STANDARDS** | CLAUDE.md, git_homepage.md, Links.md | Parsed metadata (→ PROJECT-DISCOVERY) |
| **PROJECT-DISCOVERY** | Filesystem, SERVICE-SCRIPT-STANDARDS, PROJECT-METADATA-STANDARDS, GIT-INTEGRATION | Project store, operation registry (→ CONTROL-PANEL, OPERATIONS-ENGINE, GITHUB-PUBLISHER) |
| **CONTROL-PANEL** | PROJECT-DISCOVERY, OPERATIONS-ENGINE, PROCESS-MONITOR, WORKFLOW-STATES, TAG-MANAGEMENT | Launch requests (→ OPERATIONS-ENGINE), state changes (→ WORKFLOW-STATES) |
| **OPERATIONS-ENGINE** | CONTROL-PANEL (launch request), PROJECT-DISCOVERY (operation registry) | Process handle (→ PROCESS-MONITOR), run records |
| **PROCESS-MONITOR** | OPERATIONS-ENGINE (process handles), log files | Stop signals (→ OPERATIONS-ENGINE), status summary (→ CONTROL-PANEL nav bar) |
| **WORKFLOW-STATES** | User input, USAGE-ANALYTICS | Current ticket state (→ CONTROL-PANEL) |
| **GITHUB-PUBLISHER** | PROJECT-DISCOVERY (git_homepage.md data), PROJECT-METADATA-STANDARDS | Static site files, published portfolio |
| **TAG-MANAGEMENT** | User input | Tag assignments, tag colors (→ CONTROL-PANEL) |
| **CONFIGURATION-MANAGEMENT** | Profile YAML files, PROJECT-DISCOVERY (CLAUDE.md) | AI config files, staged configs (→ GIT-INTEGRATION) |
| **USAGE-ANALYTICS** | AI session JSONL logs | Usage summary (→ CONTROL-PANEL nav bar), cost data (→ WORKFLOW-STATES) |
| **GIT-INTEGRATION** | Filesystem git state | Per-project git status (→ CONTROL-PANEL), staging area (→ CONFIGURATION-MANAGEMENT) |
| **MONITORING-HEARTBEATS** | SERVICE-SCRIPT-STANDARDS (declared ports), PROCESS-MONITOR (running processes) | Health status (→ CONTROL-PANEL), alert events |

---

## Core Contract Chain

The most important chain in the system — from project file to UI button:

```
Developer writes bin/start.sh with CommandCenter header
  ↓
SERVICE-SCRIPT-STANDARDS defines the header format
  ↓
PROJECT-DISCOVERY reads the header, creates operation registry entry
  ↓
CONTROL-PANEL renders the "Service Start" button
  ↓
User clicks → OPERATIONS-ENGINE launches bin/start.sh
  ↓
PROCESS-MONITOR streams the log
  ↓
MONITORING-HEARTBEATS polls localhost:PORT for health
```

Breaking this chain at any point (wrong header format, wrong port, script not
executable) causes the button to be missing or the health check to fail silently.

---

## Portfolio Publication Chain

```
Developer edits git_homepage.md with Show on Homepage: true
  ↓
PROJECT-METADATA-STANDARDS defines the file format
  ↓
PROJECT-DISCOVERY reads git_homepage.md on next scan
  ↓
GITHUB-PUBLISHER reads discovered card data
  ↓
User clicks "Rebuild Site" → static site generated
  ↓
User clicks "Push to GitHub Pages" → portfolio live
```

---

## AI Workflow Chain

```
User creates feature ticket in WORKFLOW-STATES
  ↓
Ticket moves IDEA → PROPOSED (user adds plan)
  ↓
Ticket moves PROPOSED → READY (user adds acceptance criteria)
  ↓
USAGE-ANALYTICS confirms cost within budget
  ↓
Ticket moves READY → IN DEVELOPMENT (AI session begins)
  ↓
AI session writes transaction log (acceptance criteria, features, intent)
  ↓
Ticket moves IN DEVELOPMENT → TESTING (AI session complete)
  ↓
Human validates → DONE (or back to READY / PROPOSED)
```

---

## Features With No Outbound Dependencies

These features only consume; nothing reads from them:
- GITHUB-PUBLISHER (endpoint: published portfolio, external)
- USAGE-ANALYTICS report (HTML artifact, not consumed by other features)

---

## Contracts That Cross Multiple Features

| Contract | Defined In | Consumed By |
|----------|------------|-------------|
| CommandCenter Operation bin/ header | SERVICE-SCRIPT-STANDARDS | PROJECT-DISCOVERY, OPERATIONS-ENGINE, MONITORING-HEARTBEATS |
| git_homepage.md format | PROJECT-METADATA-STANDARDS | PROJECT-DISCOVERY, GITHUB-PUBLISHER |
| CLAUDE.md format | PROJECT-METADATA-STANDARDS | PROJECT-DISCOVERY, CONTROL-PANEL, CONFIGURATION-MANAGEMENT |
| git_site_config.md format | PROJECT-METADATA-STANDARDS (see GITHUB-PUBLISHER) | GITHUB-PUBLISHER |
| Tag color JSON | TAG-MANAGEMENT | CONTROL-PANEL |
| AI session JSONL log format | USAGE-ANALYTICS (read contract) | USAGE-ANALYTICS only |
| AI transaction log format | WORKFLOW-STATES | WORKFLOW-STATES only |

---

## Implementation Priority (suggested)

Based on dependencies — features with no upstream dependencies should be implemented first:

1. SERVICE-SCRIPT-STANDARDS, PROJECT-METADATA-STANDARDS (contracts only, no code)
2. PROJECT-DISCOVERY (reads contracts; foundation for everything)
3. CONTROL-PANEL, OPERATIONS-ENGINE, PROCESS-MONITOR (core loop)
4. GIT-INTEGRATION, TAG-MANAGEMENT, USAGE-ANALYTICS (enrichment)
5. GITHUB-PUBLISHER, CONFIGURATION-MANAGEMENT (specialized pipelines)
6. WORKFLOW-STATES (complex lifecycle; roadmap)
7. MONITORING-HEARTBEATS (polling daemon; roadmap)
