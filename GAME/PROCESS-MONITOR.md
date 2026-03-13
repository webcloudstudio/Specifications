# Process Monitor

**Live log viewer and process control.** Shows what is running, what ran, and what the output was.

---

## Capabilities

- List all running and completed processes (most recent first)
- Live log output with auto-scroll
- Stop button for running processes
- Log viewer for completed runs
- Per-process: project name, operation name, status, start time, duration

## Screens

**Process List:** Full-width list. Per row: project, operation, status badge (RUNNING/DONE/ERROR/STOPPED), start time, duration, View Log, Stop.

**Log Viewer:** Monospace output area. Auto-scrolls while running, stops on exit. Header shows project, operation, status.

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| OPERATIONS-ENGINE (process handles) | Stop signal → running process |
| Log files (by naming convention) | Status summary → CONTROL-PANEL nav bar |
