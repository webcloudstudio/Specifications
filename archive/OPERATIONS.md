# Operations

**spec_v4 · 2026-03-11**

---

## What Is an Operation?

An operation is a script in a project's `bin/` directory. The platform discovers it,
gives it a button in the dashboard, runs it on demand, and monitors it while it runs.

Operations can be written in any language — bash, Python, Node, or anything the host
machine can execute. The only requirement is the declaration block described in
**THE-CONTRACT.md**.

---

## To Enable Platform Discovery

Add the declaration block to your script. See THE-CONTRACT.md, Contract 1.

```
# CommandCenter Operation
# Name: Service Start
# Port: 3000
```

Without this block, the script is not visible to the platform. It still runs normally
when invoked directly.

---

## To Enable Logging

Write all output (standard output and errors) to a file in addition to the terminal.
Name the file consistently so the platform can find and display it.

**What to produce:**
- A log file per run
- Named with the operation name and a timestamp
- Stored in a logs directory within the project

The platform reads these files to populate the log viewer. The exact mechanism (shell
redirection, Python logging, etc.) is the script's choice — the platform looks for
files matching the naming pattern.

---

## To Enable Status Tracking

Announce when the operation starts and when it stops. Use a consistent prefix so the
platform can parse state transitions without interpreting arbitrary output.

**What to produce:**
- A "starting" message when the script begins
- A "started" message when the service or process is ready
- A "stopped" message when the script exits (by any means)

The prefix `[GAME]` is reserved for these messages. Other output can say anything.

Example of what the messages communicate (not prescribing exact wording):
```
[GAME] Service Starting: Service Start
[GAME] Service Started: Service Start on port 3000
[GAME] Service Stopped: Service Start
```

The platform watches for `[GAME]` prefixed lines to update the status badge without
guessing from exit codes alone.

---

## To Enable Health Monitoring

Declare the port your service listens on in the operation header. The platform will
poll that port periodically and show UP / DOWN status in the dashboard.

```
# Port: 3000
```

If your service uses a non-root health endpoint (e.g., `/health` instead of `/`),
declare it:

```
# Health: /health
```

If no port is declared, health monitoring is not available for this operation.

---

## To Enable Clean Shutdown

When your operation is stopped from the platform (via the Stop button), it receives a
termination signal. The script should:

- Catch the signal
- Emit a `[GAME] Service Stopped` message
- Exit cleanly

Scripts that do not handle this will still be terminated — the `[GAME] Service Stopped`
message will be absent, and the platform will mark the run as STOPPED rather than
DONE.

---

## Naming Conventions

These names are not required but are recognized by the platform for default behaviors:

| Script | Expected Purpose |
|--------|----------------|
| `bin/start.sh` | Start the development server |
| `bin/stop.sh` | Stop the development server |
| `bin/build.sh` | Run the build pipeline |
| `bin/test.sh` | Run the test suite |
| `bin/deploy.sh` | Deploy to production |

---

## Summary: What a Well-Formed Operation Provides

| Capability | How |
|-----------|-----|
| Appears as a dashboard button | Declaration block with Name: |
| Logs are viewable in platform | Write to log file with consistent naming |
| Status badge updates live | Emit [GAME] prefixed status messages |
| Health monitoring | Declare Port: in header |
| Custom health check | Declare Health: path in header |
| Clean shutdown | Handle termination signal; emit stopped message |

An operation that provides all of these is fully integrated with the platform. An
operation that provides only the declaration block is still useful — it just has fewer
capabilities surfaced.
