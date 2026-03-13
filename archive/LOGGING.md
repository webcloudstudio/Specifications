# Logging

**spec_v4 · 2026-03-11**

---

## What Logging Is For

Logging lets the platform display what an operation did, what went wrong, and how long
things took — without running the operation again or reading the source code.

A log file is the operation's permanent record. It outlasts the process. The platform
stores it; the user can read it days later.

---

## What the Platform Expects

The platform looks for log files in a predictable location with a predictable name.
When it finds them, it displays them in the log viewer.

**Location:** A `logs/` directory within the project (e.g., `data/logs/`)
**Naming:** `{OperationName}_{YYYYMMDD_HHMMSS}.log`

If the file exists and matches this pattern, the platform displays it. The script is
responsible for writing to this location. The platform never writes log files itself.

---

## What Goes in a Log

A log file should contain everything the operation printed to the terminal — both normal
output and error output, interleaved in the order it was produced.

The platform displays log files as-is. No special format is required inside the file.
Timestamps on individual lines are helpful but not required.

---

## The [GAME] Line Protocol

Within the log output, lines prefixed with `[GAME]` are parsed by the platform for
status information. These lines should appear in the log file the same as any other output.

| Line | Platform Action |
|------|----------------|
| `[GAME] Service Starting: <name>` | Sets status to STARTING |
| `[GAME] Service Started: <name>` | Sets status to RUNNING |
| `[GAME] Service Stopped: <name>` | Sets status to STOPPED |

All other `[GAME]` lines are ignored by the platform but preserved in the log.

These lines do not replace normal log output. They are a signal layer on top of it.

---

## Log Retention

Log files accumulate over time. The platform displays the most recent runs by default.

A `bin/clean-logs.sh` operation can be provided to prune old files. No automatic
cleanup is performed by the platform unless explicitly configured.

---

## What This Means for Feature Specifications

Features that involve running operations (anything that calls a script) depend on this
logging contract being honored. Feature specs should state:

- Whether the feature requires log output to function (e.g., the log viewer reads logs)
- Whether the feature emits `[GAME]` status lines (e.g., an operation that starts a service)

Features that do not run scripts have no logging requirements.
