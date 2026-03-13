# Screen: Processes

**Live log viewer and process control.** Shows what is running, what ran, and the output.

---

## Layout

Process list (most recent first) with expandable log viewer.

## Process List

| Column | Description |
|--------|-------------|
| Project name | From METADATA.md |
| Operation | Derived from script filename |
| Status badge | RUNNING / DONE / ERROR / STOPPED |
| Start time | yyyymmdd_hhmmss format |
| Duration | Elapsed or total |
| View Log | Opens log viewer |
| Stop | Sends SIGTERM (shown only when RUNNING) |

## Log Viewer

Monospace output area. Auto-scrolls while the process is running. Stops on process exit.

Header shows: project name, operation name, status, start time.

Controls: Stop button (if running), Back to list.

## State Machine

```
IDLE → STARTING → RUNNING → DONE
                          → ERROR (non-zero exit)
                          → STOPPED (user cancelled)
```

The platform parses `[$PROJECT_NAME]` status lines from log output to track transitions.

## Log Files

Named per CLAUDE_RULES convention: `logs/{project}_{script}_{yyyymmdd_hhmmss}.log`. Project name prepended for sorting.

## Data Flow

| Reads | Writes |
|-------|--------|
| Process handles from operations engine | Stop signal → process |
| Log files by naming convention | Running count → dashboard nav bar |
