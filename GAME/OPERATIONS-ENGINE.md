# Operations Engine

**Run bin/ scripts on demand.** User clicks a button, engine launches the script, captures output, reports status.

---

## Capabilities

- One-click script execution from dashboard
- Background process launch from project root
- stdout/stderr capture to log file
- Run state tracking: IDLE → STARTING → RUNNING → DONE/ERROR/STOPPED
- Run history per project (start time, duration, exit code, log path)
- Stop button for running operations

## How It Works

1. User clicks operation button
2. Engine looks up script path from operation registry
3. Script launched as background process from project root
4. Output written to log file per CLAUDE_RULES logging convention
5. `[GAME]` status lines parsed for state transitions
6. Final status recorded on exit

## State Machine

```
IDLE → STARTING → RUNNING → DONE
                          → ERROR
                          → STOPPED (user cancelled)
```

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| PROJECT-DISCOVERY (operation registry) | PROCESS-MONITOR (process handle) |
| CONTROL-PANEL (launch requests) | Run records (history) |
