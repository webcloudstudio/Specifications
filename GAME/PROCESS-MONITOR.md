# Feature: Process Monitor

**spec_v4 · 2026-03-11**

---

## Purpose

Shows the user what is running, what ran, and what the output was. The live log viewer
and process control panel for everything the platform executes.

---

## What the User Can Do

- See all currently running processes
- See live log output for any running process
- Stop a running process
- See logs for completed past runs
- Know which project and operation each process belongs to

---

## Screens

### Process List

Full-width list; most recent at top.

Per row: project name, operation name, status badge (RUNNING / DONE / ERROR / STOPPED),
start time, duration, View Log button, Stop button (when running).

### Log Viewer

Monospace output area. Auto-scrolls while the process is running. Stops updating on exit.

Header: project name, operation name, status, start time.

Controls: Stop button (if running), Back to Processes link.

---

## Data In / Out

**Reads:**
- Process handles from OPERATIONS-ENGINE
- Log files written by operations

**Writes:**
- Stop signal → running process
- Updated status (STOPPED) → reflected in CONTROL-PANEL nav bar

---

## Contracts Used

- **Logging** (LOGGING.md): reads log files by naming convention; parses `[GAME]` lines for
  live status updates

---

## Out of Scope

- Launching operations → OPERATIONS-ENGINE
- Health polling → MONITORING-HEARTBEATS
