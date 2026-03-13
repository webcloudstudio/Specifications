# Feature: Operations Engine

**spec_v4 · 2026-03-11**

---

## Purpose

Runs a project's registered scripts on demand. A user clicks a button; the engine
launches the script, captures its output, and reports status back to the dashboard.

---

## What the User Can Do

- Click an operation button to run it
- See immediate feedback that it started
- Stop a running operation
- View run history for a project

---

## Screens

### Operation Buttons (inline, within Control Panel / Project Detail)

One button per registered operation. Button label = operation name from the bin/ header.

Button states: idle / running / error / done.

Clicking a running operation navigates to its live log in PROCESS-MONITOR.

### Run History (within Project Detail)

Table of past runs: operation name, start time, duration, exit status, link to log.

---

## How It Works

1. User clicks a button
2. Engine looks up the script path from the operation registry
3. Script is launched as a background process from the project's root directory
4. stdout and stderr are written to a log file (see LOGGING.md for naming)
5. Run record is created: start time, PID, status
6. Status updates as the script emits `[GAME]` status lines (see LOGGING.md)
7. On exit, final status is recorded

---

## Run States

```
IDLE → STARTING → RUNNING → DONE
                          → ERROR
                          → STOPPED (user stopped it)
```

---

## Data In / Out

**Reads:**
- Operation registry from PROJECT-DISCOVERY (script path, name, port)
- Launch requests from CONTROL-PANEL

**Writes:**
- Running process handle → PROCESS-MONITOR
- Run record (start, status, exit code, log path)

---

## Contracts Used

- **Operations Contract** (THE-CONTRACT.md §1): script path and metadata come from bin/ header
- **Logging** (LOGGING.md): log file written per run; `[GAME]` lines parsed for status

---

## Out of Scope

- Viewing logs → PROCESS-MONITOR
- Health polling → MONITORING-HEARTBEATS
- Scheduling operations → not planned
