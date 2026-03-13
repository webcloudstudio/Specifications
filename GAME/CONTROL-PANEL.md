# Feature: Control Panel

**spec_v4 · 2026-03-11**

---

## Purpose

The main dashboard. Shows every discovered project in one view with its current state,
available operations, and key metadata. All common actions happen here without navigating
away.

---

## What the User Can Do

- See all projects at a glance
- See each project's workflow state, type, tags, stack, and running status
- Launch any operation with one click
- Change a project's workflow state inline (no page reload)
- Change a project's type inline
- Navigate to a project's detail view
- Filter the list by state, type, or tag
- Trigger a rescan of the projects directory

---

## Screens

### Projects List

Full-width table or card grid. One row per project.

Each row shows:
- Project name
- Type badge and workflow state badge
- Tags (colored)
- Stack summary
- Running / idle indicator
- Operation buttons (one per registered script)
- Quick links (from CLAUDE.md bookmarks and Links.md)

Inline actions: workflow state dropdown, type selector, operation buttons.

### Project Detail

Single-project view with full information:
- All operations with descriptions and run status
- All endpoints and bookmarks
- Stack and git status
- Feature tickets (when WORKFLOW-STATES is built)
- Raw CLAUDE.md content (expandable)

### Nav Bar (all pages)

Shows count of currently running processes. Links to the Process Monitor.

---

## Data In / Out

**Reads from:**
- PROJECT-DISCOVERY: all project records
- OPERATIONS-ENGINE: current run status per operation
- PROCESS-MONITOR: running process count for nav bar
- TAG-MANAGEMENT: tag assignments and colors

**Writes to:**
- OPERATIONS-ENGINE: operation launch requests
- Workflow state store: state change on inline edit
- Project type store: type change on inline edit

---

## Contracts Used

- **Operations Contract** (THE-CONTRACT.md §1): operation buttons are derived from bin/ headers
- **AI Context Contract** (THE-CONTRACT.md §3): endpoint and bookmark links come from CLAUDE.md
- **Links Contract** (THE-CONTRACT.md §5): quick links come from Links.md

---

## Out of Scope

- Running scripts → OPERATIONS-ENGINE
- Viewing logs → PROCESS-MONITOR
- Publishing portfolio → GITHUB-PUBLISHER
- Managing tags → TAG-MANAGEMENT
